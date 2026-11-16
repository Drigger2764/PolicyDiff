import uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ConflictFinding(Base):
    __tablename__ = "conflict_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_a_id: Mapped[str] = mapped_column(String(36), ForeignKey("extracted_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_b_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("extracted_rules.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Conflict Taxonomy:
    # DIRECT_CONTRADICTION, CONDITIONAL_CONTRADICTION, MISSING_EXCEPTION,
    # SUPERSEDED_RULE, AMBIGUOUS_INSTRUCTION, HARMLESS_WORDING_CHANGE
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Severity: CRITICAL, HIGH, MEDIUM, LOW, INFO
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    # Status: PENDING, RESOLVED, DISMISSED
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="conflicts")
    rule_a = relationship("ExtractedRule", foreign_keys=[rule_a_id], back_populates="conflicts_as_rule_a")
    rule_b = relationship("ExtractedRule", foreign_keys=[rule_b_id], back_populates="conflicts_as_rule_b")
    reviews = relationship("ReviewDecision", back_populates="conflict", cascade="all, delete-orphan", order_by="desc(ReviewDecision.created_at)")
