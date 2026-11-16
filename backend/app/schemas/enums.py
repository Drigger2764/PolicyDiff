from enum import Enum


class ObligationType(str, Enum):
    MUST = "MUST"
    MUST_NOT = "MUST_NOT"
    SHOULD = "SHOULD"
    MAY = "MAY"
    CANNOT = "CANNOT"


class ConflictCategory(str, Enum):
    DIRECT_CONTRADICTION = "Direct contradiction"
    CONDITIONAL_CONTRADICTION = "Conditional contradiction"
    MISSING_EXCEPTION = "Missing exception"
    SUPERSEDED_RULE = "Superseded rule"
    AMBIGUOUS_INSTRUCTION = "Ambiguous instruction"
    HARMLESS_WORDING_CHANGE = "Harmless wording change"


class ConflictSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ConflictStatus(str, Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ReviewDecisionType(str, Enum):
    ACCEPTED_CONFLICT = "ACCEPTED_CONFLICT"
    DISMISSED_FALSE_POSITIVE = "DISMISSED_FALSE_POSITIVE"
    RESOLVED = "RESOLVED"
    FLAGGED_FOR_LEGAL = "FLAGGED_FOR_LEGAL"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PARSED = "parsed"
    EXTRACTED = "extracted"
    FAILED = "failed"
