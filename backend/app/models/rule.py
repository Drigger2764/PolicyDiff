import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ExtractedRule(Base):
    __tablename__ = "extracted_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id: Mapped[str] = mapped_column(String(36), ForeignKey("extracted_sections.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Core Deontic Attributes
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    obligation: Mapped[str] = mapped_column(String(50), nullable=False)  # MUST, MUST_NOT, SHOULD, MAY, CANNOT
    action: Mapped[str] = mapped_column(String(500), nullable=False)
    target_object: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Complex clauses
    conditions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    exceptions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # Provenance
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    char_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    char_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    version = relationship("DocumentVersion", back_populates="rules")
    section = relationship("ExtractedSection", back_populates="rules")
    conflicts_as_rule_a = relationship("ConflictFinding", foreign_keys="ConflictFinding.rule_a_id", back_populates="rule_a", cascade="all, delete-orphan")
    conflicts_as_rule_b = relationship("ConflictFinding", foreign_keys="ConflictFinding.rule_b_id", back_populates="rule_b")
