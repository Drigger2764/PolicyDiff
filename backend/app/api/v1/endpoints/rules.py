from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.rule import ExtractedRule
from app.schemas.rule import RuleCreate, RuleResponse, StructuredRuleRepresentation

router = APIRouter()


@router.get("/", response_model=List[RuleResponse], tags=["Rules"])
def list_rules(
    version_id: Optional[str] = None,
    obligation: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(ExtractedRule)
    if version_id:
        query = query.filter(ExtractedRule.version_id == version_id)
    if obligation:
        query = query.filter(ExtractedRule.obligation == obligation)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED, tags=["Rules"])
def create_rule(payload: RuleCreate, db: Session = Depends(get_db)):
    existing = db.query(ExtractedRule).filter(ExtractedRule.rule_id == payload.rule_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rule with ID '{payload.rule_id}' already exists.",
        )
    data = payload.model_dump()
    data["obligation"] = data["obligation"].value if hasattr(data["obligation"], "value") else data["obligation"]
    rule = ExtractedRule(**data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=RuleResponse, tags=["Rules"])
def get_rule(rule_id: str, db: Session = Depends(get_db)):
    rule = db.query(ExtractedRule).filter((ExtractedRule.id == rule_id) | (ExtractedRule.rule_id == rule_id)).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.post("/validate-structured", response_model=StructuredRuleRepresentation, tags=["Rules"])
def validate_structured_rule(payload: StructuredRuleRepresentation):
    """
    Validates a canonical 9-tuple structured rule representation.
    """
    return payload
