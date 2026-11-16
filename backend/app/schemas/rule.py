from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.enums import ObligationType


class StructuredRuleRepresentation(BaseModel):
    """
    Normalized compliance rule 9-tuple as required by PolicyDiff core engine:
    rule_id, subject, action, object, conditions, obligations, exceptions,
    source_document, source_section.
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    rule_id: str = Field(..., description="Unique human-readable identifier (e.g. SEC-V1-R001)")
    subject: str = Field(..., description="Entity governed by this policy rule (e.g. 'Software Engineers')")
    action: str = Field(..., description="Canonical operative verb (e.g. 'store', 'submit', 'encrypt')")
    object: str = Field(..., description="Target asset or process (e.g. 'customer payment data')", alias="target_object")
    conditions: List[str] = Field(default_factory=list, description="Prerequisite conditions or clauses")
    obligations: ObligationType = Field(..., description="Deontic force (MUST, MUST_NOT, SHOULD, MAY, CANNOT)", alias="obligation")
    exceptions: List[str] = Field(default_factory=list, description="Carve-outs and exemptions")
    source_document: str = Field(..., description="Name or identifier of the source document")
    source_section: str = Field(..., description="Section title or number where rule originates")


class RuleBase(BaseModel):
    rule_id: str
    subject: str
    obligation: ObligationType
    action: str
    target_object: str
    conditions: List[str] = Field(default_factory=list)
    exceptions: List[str] = Field(default_factory=list)
    raw_text: str
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    confidence_score: float = 1.0


class RuleCreate(RuleBase):
    version_id: str
    section_id: str


class RuleResponse(RuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    version_id: str
    section_id: str
    created_at: datetime
