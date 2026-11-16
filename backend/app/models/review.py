import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conflict_id: Mapped[str] = mapped_column(String(36), ForeignKey("conflict_findings.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Decisions: ACCEPTED_CONFLICT, DISMISSED_FALSE_POSITIVE, RESOLVED, FLAGGED_FOR_LEGAL
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conflict = relationship("ConflictFinding", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
