import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ExtractedSection(Base):
    __tablename__ = "extracted_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_section_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("extracted_sections.id", ondelete="SET NULL"), nullable=True)
    section_number: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "4.1.2"
    heading: Mapped[str | None] = mapped_column(String(500), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    version = relationship("DocumentVersion", back_populates="sections")
    parent_section = relationship("ExtractedSection", remote_side=[id], backref="child_sections")
    rules = relationship("ExtractedRule", back_populates="section", cascade="all, delete-orphan")
