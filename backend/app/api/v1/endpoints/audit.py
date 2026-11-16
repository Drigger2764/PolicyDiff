from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.workspace import Workspace
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.rule import ExtractedRule
from app.models.conflict import ConflictFinding
from app.models.review import ReviewDecision
from app.services.evaluator import run_evaluation_benchmark

router = APIRouter()


@router.get("/report", tags=["Audit"])
def generate_audit_report(workspace_id: str, db: Session = Depends(get_db)):
    """
    Generates a comprehensive audit compliance summary report across documents,
    extracted rules, detected conflict findings, and reviewer determinations.
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    docs = db.query(Document).filter(Document.workspace_id == workspace_id).all()
    conflicts = db.query(ConflictFinding).filter(ConflictFinding.workspace_id == workspace_id).all()
    
    total_rules = (
        db.query(ExtractedRule)
        .join(DocumentVersion)
        .join(Document)
        .filter(Document.workspace_id == workspace_id)
        .count()
    )

    conflict_breakdown: Dict[str, int] = {}
    severity_breakdown: Dict[str, int] = {}
    resolved_count = 0
    dismissed_count = 0
    pending_count = 0

    for c in conflicts:
        conflict_breakdown[c.category] = conflict_breakdown.get(c.category, 0) + 1
        severity_breakdown[c.severity] = severity_breakdown.get(c.severity, 0) + 1
        if c.status == "RESOLVED":
            resolved_count += 1
        elif c.status == "DISMISSED":
            dismissed_count += 1
        else:
            pending_count += 1

    return {
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "slug": workspace.slug,
        },
        "statistics": {
            "total_documents": len(docs),
            "total_extracted_rules": total_rules,
            "total_conflicts_detected": len(conflicts),
            "resolved_conflicts": resolved_count,
            "dismissed_conflicts": dismissed_count,
            "pending_conflicts": pending_count,
            "resolution_rate_percent": round((resolved_count / len(conflicts) * 100), 1) if conflicts else 0.0,
        },
        "conflict_categories": conflict_breakdown,
        "severity_distribution": severity_breakdown,
    }


@router.get("/benchmark", tags=["Audit"])
def get_evaluation_benchmark():
    """
    Executes and returns the real, measured NLP & conflict detection evaluation benchmark.
    """
    return run_evaluation_benchmark()
