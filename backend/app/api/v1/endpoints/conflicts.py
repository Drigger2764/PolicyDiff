from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.conflict import ConflictFinding
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.section import ExtractedSection
from app.models.rule import ExtractedRule
from app.models.review import ReviewDecision
from app.schemas.conflict import ConflictFindingCreate, ConflictFindingResponse
from app.schemas.review import ReviewDecisionCreate, ReviewDecisionResponse
from app.schemas.enums import ConflictStatus, ReviewDecisionType
from app.services.rule_extractor import extract_rules_from_text, ExtractedRuleCandidate
from app.services.conflict_detector import ConflictDetector

router = APIRouter()


@router.get("/", response_model=List[ConflictFindingResponse], tags=["Conflicts"])
def list_conflicts(
    workspace_id: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(ConflictFinding)
    if workspace_id:
        query = query.filter(ConflictFinding.workspace_id == workspace_id)
    if category:
        query = query.filter(ConflictFinding.category == category)
    if status_filter:
        query = query.filter(ConflictFinding.status == status_filter)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=ConflictFindingResponse, status_code=status.HTTP_201_CREATED, tags=["Conflicts"])
def create_conflict(payload: ConflictFindingCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["category"] = data["category"].value if hasattr(data["category"], "value") else data["category"]
    data["severity"] = data["severity"].value if hasattr(data["severity"], "value") else data["severity"]
    data["status"] = data["status"].value if hasattr(data["status"], "value") else data["status"]
    
    conflict = ConflictFinding(**data)
    db.add(conflict)
    db.commit()
    db.refresh(conflict)
    return conflict


@router.post("/detect", response_model=List[ConflictFindingResponse], tags=["Conflicts"])
def trigger_conflict_detection(workspace_id: str, db: Session = Depends(get_db)):
    """
    Extracts rules from sections across documents in the workspace,
    runs the deontic conflict detection engine, persists new findings, and returns them.
    """
    # 1. Fetch all documents in workspace
    documents = db.query(Document).filter(Document.workspace_id == workspace_id).all()
    if not documents:
        return []

    rule_candidates: List[ExtractedRuleCandidate] = []
    rule_orm_map: Dict[str, ExtractedRule] = {}

    for doc in documents:
        for version in doc.versions:
            # Check if rules already extracted for this version
            existing_rules = db.query(ExtractedRule).filter(ExtractedRule.version_id == version.id).all()
            if not existing_rules:
                # Extract rules from sections
                for sec in version.sections:
                    cands = extract_rules_from_text(
                        text=sec.raw_text,
                        source_document=doc.title,
                        source_section=sec.heading or sec.section_number or "General",
                        doc_effective_date=version.effective_date,
                        rule_id_prefix=f"{doc.title[:3].upper()}-{version.version_tag}",
                    )
                    for c in cands:
                        orm_rule = ExtractedRule(
                            rule_id=f"{c.rule_id}-{len(rule_orm_map) + 1}",
                            version_id=version.id,
                            section_id=sec.id,
                            subject=c.subject,
                            obligation=c.obligation.value,
                            action=c.action,
                            target_object=c.target_object,
                            conditions=c.conditions,
                            exceptions=c.exceptions,
                            raw_text=c.raw_text,
                            char_start=c.char_start,
                            char_end=c.char_end,
                            confidence_score=c.confidence_score,
                        )
                        db.add(orm_rule)
                        db.flush()
                        rule_orm_map[orm_rule.rule_id] = orm_rule
                        c.rule_id = orm_rule.rule_id
                        rule_candidates.append(c)
                version.status = "extracted"
            else:
                for r in existing_rules:
                    rule_orm_map[r.rule_id] = r
                    from app.schemas.enums import ObligationType
                    cand = ExtractedRuleCandidate(
                        rule_id=r.rule_id,
                        subject=r.subject,
                        obligation=ObligationType(r.obligation),
                        action=r.action,
                        target_object=r.target_object,
                        conditions=r.conditions,
                        exceptions=r.exceptions,
                        effective_date=version.effective_date,
                        raw_text=r.raw_text,
                        char_start=r.char_start or 0,
                        char_end=r.char_end or 0,
                        confidence_score=r.confidence_score,
                        source_document=doc.title,
                        source_section=r.section.heading if r.section else "General",
                    )
                    rule_candidates.append(cand)

    db.commit()

    # 2. Run ConflictDetector
    detector = ConflictDetector(similarity_threshold=0.35)
    detected = detector.detect_conflicts(rule_candidates, include_ambiguity=True)

    persisted_conflicts: List[ConflictFinding] = []
    for d in detected:
        orm_a = rule_orm_map.get(d.rule_a_id)
        orm_b = rule_orm_map.get(d.rule_b_id) if d.rule_b_id else None

        if not orm_a:
            continue

        # Avoid duplicates
        existing = db.query(ConflictFinding).filter(
            ConflictFinding.workspace_id == workspace_id,
            ConflictFinding.rule_a_id == orm_a.id,
            ConflictFinding.category == d.category.value,
        ).first()

        if not existing:
            cf = ConflictFinding(
                workspace_id=workspace_id,
                rule_a_id=orm_a.id,
                rule_b_id=orm_b.id if orm_b else None,
                category=d.category.value,
                severity=d.severity.value,
                description=d.description,
                confidence=d.confidence,
                status=ConflictStatus.PENDING.value,
            )
            db.add(cf)
            db.flush()
            persisted_conflicts.append(cf)
        else:
            persisted_conflicts.append(existing)

    db.commit()
    return db.query(ConflictFinding).filter(ConflictFinding.workspace_id == workspace_id).all()


@router.get("/graph", tags=["Conflicts"])
def get_conflict_graph(workspace_id: str, db: Session = Depends(get_db)):
    """
    Returns NetworkX graph topology nodes, links, and cluster metrics for visualization.
    """
    conflicts = db.query(ConflictFinding).filter(ConflictFinding.workspace_id == workspace_id).all()
    rules = db.query(ExtractedRule).join(DocumentVersion).join(Document).filter(Document.workspace_id == workspace_id).all()

    from app.schemas.enums import ObligationType
    cands: List[ExtractedRuleCandidate] = []
    for r in rules:
        cands.append(
            ExtractedRuleCandidate(
                rule_id=r.rule_id,
                subject=r.subject,
                obligation=ObligationType(r.obligation),
                action=r.action,
                target_object=r.target_object,
                conditions=r.conditions,
                exceptions=r.exceptions,
                raw_text=r.raw_text,
                char_start=0,
                char_end=0,
                confidence_score=r.confidence_score,
                source_document=r.version.document.title if r.version and r.version.document else "Policy",
                source_section=r.section.heading if r.section else "General",
            )
        )

    from app.services.conflict_detector import DetectedConflict, ConflictEvidence, ConflictCategory, ConflictSeverity
    det_list: List[DetectedConflict] = []
    for c in conflicts:
        det_list.append(
            DetectedConflict(
                category=ConflictCategory(c.category),
                severity=ConflictSeverity(c.severity),
                description=c.description,
                confidence=c.confidence,
                rule_a_id=c.rule_a.rule_id if c.rule_a else c.rule_a_id,
                rule_b_id=c.rule_b.rule_id if c.rule_b else None,
                evidence=ConflictEvidence(
                    rule_a_id=c.rule_a.rule_id if c.rule_a else c.rule_a_id,
                    rule_a_text=c.rule_a.raw_text if c.rule_a else "",
                    rule_a_source="",
                    clashing_aspect="",
                ),
            )
        )

    detector = ConflictDetector()
    return detector.build_networkx_graph(cands, det_list)


@router.post("/{conflict_id}/review", response_model=ReviewDecisionResponse, tags=["Conflicts"])
def review_conflict(
    conflict_id: str,
    payload: ReviewDecisionCreate,
    db: Session = Depends(get_db),
):
    """
    Applies human determination (ACCEPTED_CONFLICT, DISMISSED_FALSE_POSITIVE, RESOLVED, FLAGGED_FOR_LEGAL).
    """
    conflict = db.query(ConflictFinding).filter(ConflictFinding.id == conflict_id).first()
    if not conflict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conflict not found.")

    dec_val = payload.decision.value if hasattr(payload.decision, "value") else payload.decision

    review = ReviewDecision(
        conflict_id=conflict.id,
        decision=dec_val,
        notes=payload.notes,
        action_taken=payload.action_taken,
    )

    if dec_val in ["RESOLVED", "ACCEPTED_CONFLICT"]:
        conflict.status = ConflictStatus.RESOLVED.value
    elif dec_val == "DISMISSED_FALSE_POSITIVE":
        conflict.status = ConflictStatus.DISMISSED.value
    elif dec_val == "FLAGGED_FOR_LEGAL":
        conflict.status = "UNDER_LEGAL_REVIEW"

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/{conflict_id}", response_model=ConflictFindingResponse, tags=["Conflicts"])
def get_conflict(conflict_id: str, db: Session = Depends(get_db)):
    conflict = db.query(ConflictFinding).filter(ConflictFinding.id == conflict_id).first()
    if not conflict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conflict finding not found")
    return conflict
