from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import ReviewDecisionType


class ReviewDecisionBase(BaseModel):
    decision: ReviewDecisionType
    notes: Optional[str] = None
    action_taken: Optional[str] = None


class ReviewDecisionCreate(ReviewDecisionBase):
    conflict_id: str


class ReviewDecisionResponse(ReviewDecisionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conflict_id: str
    reviewer_id: Optional[str] = None
    created_at: datetime
