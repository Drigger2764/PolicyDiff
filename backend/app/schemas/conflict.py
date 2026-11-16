from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.enums import ConflictCategory, ConflictSeverity, ConflictStatus
from app.schemas.rule import RuleResponse


class ConflictFindingBase(BaseModel):
    category: ConflictCategory
    severity: ConflictSeverity = ConflictSeverity.MEDIUM
    description: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    status: ConflictStatus = ConflictStatus.PENDING


class ConflictFindingCreate(ConflictFindingBase):
    workspace_id: str
    rule_a_id: str
    rule_b_id: Optional[str] = None


class ConflictFindingResponse(ConflictFindingBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    rule_a_id: str
    rule_b_id: Optional[str] = None
    created_at: datetime
    rule_a: Optional[RuleResponse] = None
    rule_b: Optional[RuleResponse] = None
