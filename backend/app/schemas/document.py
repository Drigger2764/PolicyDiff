from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import DocumentStatus


class SectionBase(BaseModel):
    section_number: Optional[str] = None
    heading: Optional[str] = None
    level: int = 1
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    raw_text: str
    order_index: int


class SectionCreate(SectionBase):
    version_id: str
    parent_section_id: Optional[str] = None


class SectionResponse(SectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    version_id: str
    parent_section_id: Optional[str] = None
    created_at: datetime


class DocumentVersionBase(BaseModel):
    version_tag: str
    file_name: str
    file_format: str
    file_size_bytes: int
    effective_date: Optional[date] = None
    status: DocumentStatus = DocumentStatus.PENDING


class DocumentVersionCreate(DocumentVersionBase):
    document_id: str
    file_path: str


class DocumentVersionResponse(DocumentVersionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    file_path: str
    uploaded_by: Optional[str] = None
    created_at: datetime


class DocumentBase(BaseModel):
    title: str
    category: str
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    workspace_id: str


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime
    versions: List[DocumentVersionResponse] = []
