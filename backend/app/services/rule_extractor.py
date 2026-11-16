import re
from typing import List, Optional, Tuple, Dict, Any
from datetime import date
from pydantic import BaseModel
from app.schemas.enums import ObligationType
from app.schemas.rule import StructuredRuleRepresentation


class ExtractedRuleCandidate(BaseModel):
    rule_id: str
    subject: str
    obligation: ObligationType
    action: str
    target_object: str
    conditions: List[str]
    exceptions: List[str]
    effective_date: Optional[date] = None
    raw_text: str
    char_start: int
    char_end: int
    confidence_score: float
    source_document: str
    source_section: str


# Deontic keywords mapped to obligation types
MODAL_PATTERNS: List[Tuple[re.Pattern, ObligationType]] = [
    (re.compile(r"\b(must\s+not|shall\s+not|are\s+prohibited\s+from|is\s+prohibited\s+from|cannot|may\s+not)\b", re.IGNORECASE), ObligationType.MUST_NOT),
    (re.compile(r"\b(must|shall|is\s+required\s+to|are\s+required\s+to|will\s+ensure)\b", re.IGNORECASE), ObligationType.MUST),
    (re.compile(r"\b(should|is\s+recommended\s+to|are\s+advised\s+to|ought\s+to)\b", re.IGNORECASE), ObligationType.SHOULD),
    (re.compile(r"\b(may|is\s+permitted\s+to|are\s+authorized\s+to|is\s+allowed\s+to)\b", re.IGNORECASE), ObligationType.MAY),
    (re.compile(r"\b(cannot|is\s+ineligible\s+to|are\s+ineligible\s+to)\b", re.IGNORECASE), ObligationType.CANNOT),
]

CONDITION_PATTERNS = [
    re.compile(r"\b(if\s+[^,;.]+)", re.IGNORECASE),
    re.compile(r"\b(when\s+[^,;.]+)", re.IGNORECASE),
    re.compile(r"\b(where\s+[^,;.]+)", re.IGNORECASE),
    re.compile(r"\b(in\s+the\s+event\s+of\s+[^,;.]+)", re.IGNORECASE),
    re.compile(r"\b(for\s+(?:all\s+)?(?:domestic|international|emergency|remote|production|staging)[^,;.]+)", re.IGNORECASE),
    re.compile(r"\b(exceeding\s+[^,;.]+)", re.IGNORECASE),
    re.compile(r"\b(prior\s+to\s+[^,;.]+)", re.IGNORECASE),
    re.compile(r"\b(upon\s+[^,;.]+)", re.IGNORECASE),
]

EXCEPTION_PATTERNS = [
    re.compile(r"\b(?:except|unless|with\s+the\s+exception\s+of|excluding)\s+([^.;]+)", re.IGNORECASE),
    re.compile(r"\bprovided\s+that\s+([^.;]+)", re.IGNORECASE),
]

DATE_PATTERN = re.compile(r"\b(?:effective(?:\s+date)?[:\s]+)?(\d{4}-\d{2}-\d{2}|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b", re.IGNORECASE)


def split_sentences(text: str) -> List[Tuple[str, int, int]]:
    """
    Splits text into sentences while tracking character start and end offsets.
    """
    sentences = []
    # Match sentences ending with period, question mark, exclamation, or newline list items
    pattern = re.compile(r"([A-Z0-9][^.!?\n]+[.!?]?)", re.MULTILINE)
    for m in pattern.finditer(text):
        s_text = m.group(1).strip()
        if len(s_text) > 10:  # Skip trivial fragments
            sentences.append((s_text, m.start(), m.end()))
    return sentences


def normalize_token(t: str) -> str:
    """Removes noise articles and punctuation for semantic canonical matching."""
    t = re.sub(r"^(the|a|an|all|any)\s+", "", t.strip(), flags=re.IGNORECASE)
    t = re.sub(r"[^\w\s-]", "", t)
    return t.strip().lower()


def extract_rules_from_text(
    text: str,
    source_document: str = "Unknown Document",
    source_section: str = "1.0 General",
    doc_effective_date: Optional[date] = None,
    rule_id_prefix: str = "RULE",
) -> List[ExtractedRuleCandidate]:
    """
    Extracts structured policy rules from natural language text.
    Identifies deontic force, subjects, verbs, objects, conditions, and exceptions.
    """
    rules: List[ExtractedRuleCandidate] = []
    sentences = split_sentences(text)
    rule_counter = 1

    for sent_text, start_offset, end_offset in sentences:
        detected_modal: Optional[ObligationType] = None
        modal_match = None

        # 1. Detect deontic modality
        for pattern, modality in MODAL_PATTERNS:
            m = pattern.search(sent_text)
            if m:
                detected_modal = modality
                modal_match = m
                break

        if not detected_modal or not modal_match:
            continue  # Non-normative sentence

        modal_start, modal_end = modal_match.span()

        # 2. Extract Subject (preceding the modal verb)
        raw_subject = sent_text[:modal_start].strip()
        # Clean subject of clause connectors
        raw_subject = re.sub(r"^(however|furthermore|additionally|in\s+addition|note\s+that),?\s*", "", raw_subject, flags=re.IGNORECASE)
        if not raw_subject:
            raw_subject = "All Personnel"

        # 3. Extract Predicate (Action & Object) following modal verb
        remainder = sent_text[modal_end:].strip()
        # Strip leading infinitive "to" if present
        if remainder.lower().startswith("to "):
            remainder = remainder[3:].strip()

        # 4. Extract Exceptions
        exceptions: List[str] = []
        for exc_pat in EXCEPTION_PATTERNS:
            for exc_match in exc_pat.finditer(remainder):
                exc_clause = exc_match.group(1).strip()
                exceptions.append(exc_clause)
                # Remove exception from remainder
                remainder = remainder.replace(exc_match.group(0), "")

        # 5. Extract Conditions
        conditions: List[str] = []
        for cond_pat in CONDITION_PATTERNS:
            for cond_match in cond_pat.finditer(remainder):
                cond_clause = cond_match.group(1).strip()
                conditions.append(cond_clause)
                # Remove condition clause from remainder
                remainder = remainder.replace(cond_match.group(0), "")

        # Also check for conditions in the subject portion (e.g. "When traveling, employees must...")
        for cond_pat in CONDITION_PATTERNS:
            for cond_match in cond_pat.finditer(raw_subject):
                cond_clause = cond_match.group(1).strip()
                conditions.append(cond_clause)
                raw_subject = raw_subject.replace(cond_match.group(0), "").strip()

        # 6. Separate Action (first 1-2 verbs/phrase) and Object from remaining predicate
        remainder_words = remainder.split()
        if len(remainder_words) == 0:
            action = "comply"
            target_object = "policy"
        elif len(remainder_words) == 1:
            action = remainder_words[0]
            target_object = "requirements"
        else:
            action = remainder_words[0]
            target_object = " ".join(remainder_words[1:]).strip(" ,;.")

        # 7. Check for effective date within sentence
        effective_date = doc_effective_date
        date_match = DATE_PATTERN.search(sent_text)
        if date_match and not effective_date:
            pass  # Can parse string date if needed

        confidence = 0.90
        if len(exceptions) > 0:
            confidence += 0.05
        if len(conditions) > 0:
            confidence += 0.03
        confidence = min(1.0, confidence)

        rule_id = f"{rule_id_prefix}-{rule_counter:03d}"
        rule_counter += 1

        rules.append(
            ExtractedRuleCandidate(
                rule_id=rule_id,
                subject=raw_subject,
                obligation=detected_modal,
                action=action,
                target_object=target_object,
                conditions=conditions,
                exceptions=exceptions,
                effective_date=effective_date,
                raw_text=sent_text,
                char_start=start_offset,
                char_end=end_offset,
                confidence_score=confidence,
                source_document=source_document,
                source_section=source_section,
            )
        )

    return rules
