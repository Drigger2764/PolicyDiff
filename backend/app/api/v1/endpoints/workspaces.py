from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse

router = APIRouter()


@router.get("/", response_model=List[WorkspaceResponse], tags=["Workspaces"])
def list_workspaces(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Workspace).offset(skip).limit(limit).all()


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED, tags=["Workspaces"])
def create_workspace(payload: WorkspaceCreate, db: Session = Depends(get_db)):
    existing = db.query(Workspace).filter(Workspace.slug == payload.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workspace with slug '{payload.slug}' already exists.",
        )
    workspace = Workspace(**payload.model_dump())
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceResponse, tags=["Workspaces"])
def get_workspace(workspace_id: str, db: Session = Depends(get_db)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace
