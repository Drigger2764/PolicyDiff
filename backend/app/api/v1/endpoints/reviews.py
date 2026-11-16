from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.conflict import ConflictFinding
from app.models.review import ReviewDecision
from app.schemas.review import ReviewDecisionCreate, ReviewDecisionResponse
from app.schemas.enums import ConflictStatus

router = APIRouter()


@router.get("/conflict/{conflict_id}", response_model=List[ReviewDecisionResponse], tags=["Reviews"])
def get_conflict_reviews(conflict_id: str, db: Session = Depends(get_db)):
    return db.query(ReviewDecision).filter(ReviewDecision.conflict_id == conflict_id).all()


@router.post("/", response_model=ReviewDecisionResponse, status_code=status.HTTP_201_CREATED, tags=["Reviews"])
def submit_review_decision(payload: ReviewDecisionCreate, db: Session = Depends(get_db)):
    conflict = db.query(ConflictFinding).filter(ConflictFinding.id == payload.conflict_id).first()
    if not conflict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conflict finding not found")
    
    data = payload.model_dump()
    data["decision"] = data["decision"].value if hasattr(data["decision"], "value") else data["decision"]
    
    review = ReviewDecision(**data)
    
    # Update conflict status based on decision
    if data["decision"] in ["RESOLVED", "ACCEPTED_CONFLICT"]:
        conflict.status = ConflictStatus.RESOLVED.value
    elif data["decision"] == "DISMISSED_FALSE_POSITIVE":
        conflict.status = ConflictStatus.DISMISSED.value
    
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
