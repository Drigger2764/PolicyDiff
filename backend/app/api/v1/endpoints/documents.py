import os
import uuid
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.section import ExtractedSection
from app.schemas.document import DocumentResponse, DocumentVersionResponse, SectionResponse
from app.services.document_parser import (
    parse_document,
    DocumentParsingError,
    EmptyDocumentError,
    UnsupportedFormatError,
)

router = APIRouter()

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, tags=["Documents"])
async def upload_document(
    workspace_id: str = Form(...),
    title: str = Form(...),
    category: str = Form("General"),
    description: Optional[str] = Form(None),
    version_tag: str = Form("1.0.0"),
    effective_date: Optional[date] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and parse a policy document (PDF or DOCX).
    Saves file, extracts structured sections, and commits to database.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded.")

    file_ext = file.filename.lower().split(".")[-1]
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '.{file_ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty (0 bytes).")

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB.",
        )

    # 1. Parse document sections
    try:
        parsed_sections = parse_document(file.filename, file_bytes)
    except EmptyDocumentError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UnsupportedFormatError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DocumentParsingError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Parsing failure: {str(e)}")

    # 2. Save physical file
    safe_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_disk_path = os.path.join(UPLOAD_DIR, safe_filename)
    with open(file_disk_path, "wb") as f:
        f.write(file_bytes)

    # 3. Create or find Document
    document = Document(
        workspace_id=workspace_id,
        title=title,
        category=category,
        description=description,
    )
    db.add(document)
    db.flush()

    # 4. Create DocumentVersion
    doc_version = DocumentVersion(
        document_id=document.id,
        version_tag=version_tag,
        file_name=file.filename,
        file_format=file_ext,
        file_path=file_disk_path,
        file_size_bytes=file_size,
        status="parsed",
        effective_date=effective_date,
    )
    db.add(doc_version)
    db.flush()

    # 5. Save ExtractedSections
    for s in parsed_sections:
        sec = ExtractedSection(
            version_id=doc_version.id,
            section_number=s.section_number,
            heading=s.heading,
            level=s.level,
            page_start=s.page_start,
            page_end=s.page_end,
            raw_text=s.raw_text,
            order_index=s.order_index,
        )
        db.add(sec)

    db.commit()
    db.refresh(document)
    return document


@router.get("/", response_model=List[DocumentResponse], tags=["Documents"])
def list_documents(
    workspace_id: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Document)
    if workspace_id:
        query = query.filter(Document.workspace_id == workspace_id)
    if category:
        query = query.filter(Document.category == category)
    return query.offset(skip).limit(limit).all()


@router.get("/{document_id}", response_model=DocumentResponse, tags=["Documents"])
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Documents"])
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    db.delete(doc)
    db.commit()
    return None


@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse], tags=["Documents"])
def list_document_versions(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return doc.versions


@router.get("/versions/{version_id}/sections", response_model=List[SectionResponse], tags=["Documents"])
def get_version_sections(version_id: str, db: Session = Depends(get_db)):
    version = db.query(DocumentVersion).filter(DocumentVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document version not found.")
    return version.sections
