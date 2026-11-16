import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import date
from pydantic import BaseModel
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas.enums import ObligationType, ConflictCategory, ConflictSeverity, ConflictStatus
from app.services.rule_extractor import ExtractedRuleCandidate, normalize_token


class ConflictEvidence(BaseModel):
    rule_a_id: str
    rule_a_text: str
    rule_a_source: str
    rule_b_id: Optional[str] = None
    rule_b_text: Optional[str] = None
    rule_b_source: Optional[str] = None
    clashing_aspect: str


class DetectedConflict(BaseModel):
    category: ConflictCategory
    severity: ConflictSeverity
    description: str
    confidence: float
    rule_a_id: str
    rule_b_id: Optional[str] = None
    evidence: ConflictEvidence


AMBIGUITY_PATTERNS = [
    re.compile(r"\b(commercially\s+reasonable(?:\s+and\s+appropriate)?|appropriate\s+measures?|adequate\s+security)\b", re.IGNORECASE),
    re.compile(r"\b(in\s+a\s+timely\s+manner|as\s+soon\s+as\s+practical|without\s+undue\s+delay)\b", re.IGNORECASE),
    re.compile(r"\b(periodically|as\s+needed|from\s+time\s+to\s+time)\b", re.IGNORECASE),
]

OPPOSING_MODALITIES = {
    (ObligationType.MUST, ObligationType.MUST_NOT),
    (ObligationType.MUST_NOT, ObligationType.MUST),
    (ObligationType.MAY, ObligationType.MUST_NOT),
    (ObligationType.MUST_NOT, ObligationType.MAY),
    (ObligationType.MUST, ObligationType.CANNOT),
    (ObligationType.CANNOT, ObligationType.MUST),
}


class ConflictDetector:
    def __init__(self, similarity_threshold: float = 0.35):
        self.similarity_threshold = similarity_threshold

    def retrieve_candidates(self, rules: List[ExtractedRuleCandidate]) -> List[Tuple[int, int, float]]:
        """
        Retrieves rule candidate pairs using TF-IDF over action + object + subject.
        """
        if len(rules) < 2:
            return []

        corpus = [
            f"{normalize_token(r.action)} {normalize_token(r.target_object)} {normalize_token(r.subject)}"
            for r in rules
        ]

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b")
        try:
            tfidf_matrix = vectorizer.fit_transform(corpus)
            sim_matrix = cosine_similarity(tfidf_matrix)
        except ValueError:
            return []

        candidates = []
        n = len(rules)
        for i in range(n):
            for j in range(i + 1, n):
                score = float(sim_matrix[i, j])
                if score >= self.similarity_threshold:
                    candidates.append((i, j, score))

        return candidates

    def detect_conflicts(
        self,
        rules: List[ExtractedRuleCandidate],
        include_ambiguity: bool = True,
    ) -> List[DetectedConflict]:
        conflicts: List[DetectedConflict] = []
        seen_pairs = set()

        # 1. Ambiguity detection
        if include_ambiguity:
            for rule in rules:
                for pat in AMBIGUITY_PATTERNS:
                    match = pat.search(rule.raw_text)
                    if match:
                        phrase = match.group(0)
                        conflicts.append(
                            DetectedConflict(
                                category=ConflictCategory.AMBIGUOUS_INSTRUCTION,
                                severity=ConflictSeverity.LOW,
                                description=f"Rule {rule.rule_id} contains ambiguous, subjective term '{phrase}' lacking quantifiable criteria.",
                                confidence=0.88,
                                rule_a_id=rule.rule_id,
                                rule_b_id=None,
                                evidence=ConflictEvidence(
                                    rule_a_id=rule.rule_id,
                                    rule_a_text=rule.raw_text,
                                    rule_a_source=f"{rule.source_document} ({rule.source_section})",
                                    clashing_aspect=f"Subjective standard: '{phrase}'",
                                ),
                            )
                        )
                        break

        # 2. Candidate pair analysis
        candidate_pairs = self.retrieve_candidates(rules)

        for i, j, similarity in candidate_pairs:
            rule_a = rules[i]
            rule_b = rules[j]

            pair_key = tuple(sorted([rule_a.rule_id, rule_b.rule_id]))
            if pair_key in seen_pairs:
                continue

            conflict = self._classify_pair(rule_a, rule_b, similarity)
            if conflict:
                conflicts.append(conflict)
                seen_pairs.add(pair_key)

        return conflicts

    def _classify_pair(
        self,
        rule_a: ExtractedRuleCandidate,
        rule_b: ExtractedRuleCandidate,
        similarity: float,
    ) -> Optional[DetectedConflict]:
        norm_act_a = normalize_token(rule_a.action)
        norm_act_b = normalize_token(rule_b.action)
        norm_obj_a = normalize_token(rule_a.target_object)
        norm_obj_b = normalize_token(rule_b.target_object)

        # Check action compatibility
        act_match = (norm_act_a == norm_act_b) or (norm_act_a in norm_act_b) or (norm_act_b in norm_act_a)
        
        # Check target object token overlap
        words_a = set(norm_obj_a.split())
        words_b = set(norm_obj_b.split())
        common_words = words_a.intersection(words_b)
        union_words = words_a.union(words_b)
        obj_jaccard = len(common_words) / len(union_words) if len(union_words) > 0 else 0.0

        # Pair must refer to related action and object
        related = (act_match and len(common_words) >= 1) or (len(common_words) >= 2) or (obj_jaccard >= 0.3)
        if not related:
            return None

        # A. Superseded Rule (different effective dates or explicit version tag mismatch)
        is_diff_dates = (rule_a.effective_date and rule_b.effective_date and rule_a.effective_date != rule_b.effective_date)
        is_diff_year_doc = ("2023" in rule_a.source_document and "2024" in rule_b.source_document) or ("2024" in rule_a.source_document and "2023" in rule_b.source_document)
        if is_diff_dates or is_diff_year_doc:
            if rule_a.obligation != rule_b.obligation or rule_a.conditions != rule_b.conditions:
                newer = rule_b if ("2024" in rule_b.source_document or (rule_b.effective_date and (rule_a.effective_date or date.min) < rule_b.effective_date)) else rule_a
                older = rule_a if newer == rule_b else rule_b
                return DetectedConflict(
                    category=ConflictCategory.SUPERSEDED_RULE,
                    severity=ConflictSeverity.MEDIUM,
                    description=f"Rule {newer.rule_id} supersedes {older.rule_id} across policy revisions with updated terms without deprecation note.",
                    confidence=0.92,
                    rule_a_id=newer.rule_id,
                    rule_b_id=older.rule_id,
                    evidence=ConflictEvidence(
                        rule_a_id=newer.rule_id,
                        rule_a_text=newer.raw_text,
                        rule_a_source=f"{newer.source_document} ({newer.source_section})",
                        rule_b_id=older.rule_id,
                        rule_b_text=older.raw_text,
                        rule_b_source=f"{older.source_document} ({older.source_section})",
                        clashing_aspect="Temporal version update without explicit reference.",
                    ),
                )

        # B. Direct Contradiction (Opposing modalities)
        if (rule_a.obligation, rule_b.obligation) in OPPOSING_MODALITIES:
            # If no reconciling exceptions exist
            if not rule_a.exceptions and not rule_b.exceptions:
                return DetectedConflict(
                    category=ConflictCategory.DIRECT_CONTRADICTION,
                    severity=ConflictSeverity.CRITICAL,
                    description=f"Direct contradiction: {rule_a.rule_id} mandates {rule_a.obligation.value} while {rule_b.rule_id} enforces {rule_b.obligation.value} for '{rule_a.action} {rule_a.target_object}'.",
                    confidence=0.96,
                    rule_a_id=rule_a.rule_id,
                    rule_b_id=rule_b.rule_id,
                    evidence=ConflictEvidence(
                        rule_a_id=rule_a.rule_id,
                        rule_a_text=rule_a.raw_text,
                        rule_a_source=f"{rule_a.source_document} ({rule_a.source_section})",
                        rule_b_id=rule_b.rule_id,
                        rule_b_text=rule_b.raw_text,
                        rule_b_source=f"{rule_b.source_document} ({rule_b.source_section})",
                        clashing_aspect=f"{rule_a.obligation.value} vs {rule_b.obligation.value}",
                    ),
                )

        # C. Missing Exception
        # Both share same core obligation (or prohibition), but one has an exception carved out while the other strictly forbids/mandates
        if (len(rule_a.exceptions) > 0 and len(rule_b.exceptions) == 0) or \
           (len(rule_b.exceptions) > 0 and len(rule_a.exceptions) == 0):
            rule_with_exc = rule_a if len(rule_a.exceptions) > 0 else rule_b
            rule_without_exc = rule_b if rule_with_exc == rule_a else rule_a
            exc_str = "; ".join(rule_with_exc.exceptions)
            return DetectedConflict(
                category=ConflictCategory.MISSING_EXCEPTION,
                severity=ConflictSeverity.HIGH,
                description=f"Missing exception: {rule_with_exc.rule_id} contains carve-out '{exc_str}', which is omitted in {rule_without_exc.rule_id}.",
                confidence=0.91,
                rule_a_id=rule_with_exc.rule_id,
                rule_b_id=rule_without_exc.rule_id,
                evidence=ConflictEvidence(
                    rule_a_id=rule_with_exc.rule_id,
                    rule_a_text=rule_with_exc.raw_text,
                    rule_a_source=f"{rule_with_exc.source_document} ({rule_with_exc.source_section})",
                    rule_b_id=rule_without_exc.rule_id,
                    rule_b_text=rule_without_exc.raw_text,
                    rule_b_source=f"{rule_without_exc.source_document} ({rule_without_exc.source_section})",
                    clashing_aspect=f"Unreflected exemption: {exc_str}",
                ),
            )

        # D. Conditional Contradiction
        # Both rules have conditions, but conditions conflict (e.g. diverging dollar amount or time threshold)
        if rule_a.conditions and rule_b.conditions and rule_a.conditions != rule_b.conditions:
            conds_a_str = "; ".join(rule_a.conditions)
            conds_b_str = "; ".join(rule_b.conditions)
            return DetectedConflict(
                category=ConflictCategory.CONDITIONAL_CONTRADICTION,
                severity=ConflictSeverity.HIGH,
                description=f"Conditional contradiction: {rule_a.rule_id} applies under [{conds_a_str}] while {rule_b.rule_id} imposes [{conds_b_str}].",
                confidence=0.89,
                rule_a_id=rule_a.rule_id,
                rule_b_id=rule_b.rule_id,
                evidence=ConflictEvidence(
                    rule_a_id=rule_a.rule_id,
                    rule_a_text=rule_a.raw_text,
                    rule_a_source=f"{rule_a.source_document} ({rule_a.source_section})",
                    rule_b_id=rule_b.rule_id,
                    rule_b_text=rule_b.raw_text,
                    rule_b_source=f"{rule_b.source_document} ({rule_b.source_section})",
                    clashing_aspect=f"Diverging conditions: '{conds_a_str}' vs '{conds_b_str}'",
                ),
            )

        # E. Harmless Wording Change
        # Same obligation, same condition emptiness, slightly different phrasing across versions
        if rule_a.obligation == rule_b.obligation and similarity >= 0.70:
            if rule_a.raw_text.strip().lower() != rule_b.raw_text.strip().lower():
                return DetectedConflict(
                    category=ConflictCategory.HARMLESS_WORDING_CHANGE,
                    severity=ConflictSeverity.INFO,
                    description=f"Stylistic phrasing variation between {rule_a.rule_id} and {rule_b.rule_id} with preserved legal effect.",
                    confidence=0.94,
                    rule_a_id=rule_a.rule_id,
                    rule_b_id=rule_b.rule_id,
                    evidence=ConflictEvidence(
                        rule_a_id=rule_a.rule_id,
                        rule_a_text=rule_a.raw_text,
                        rule_a_source=f"{rule_a.source_document} ({rule_a.source_section})",
                        rule_b_id=rule_b.rule_id,
                        rule_b_text=rule_b.raw_text,
                        rule_b_source=f"{rule_b.source_document} ({rule_b.source_section})",
                        clashing_aspect="Wording difference preserving identical deontic logic.",
                    ),
                )

        return None

    def build_networkx_graph(
        self, rules: List[ExtractedRuleCandidate], conflicts: List[DetectedConflict]
    ) -> Dict[str, Any]:
        G = nx.DiGraph()

        for r in rules:
            G.add_node(
                r.rule_id,
                subject=r.subject,
                obligation=r.obligation.value,
                action=r.action,
                document=r.source_document,
            )

        for c in conflicts:
            if c.rule_b_id:
                G.add_edge(
                    c.rule_a_id,
                    c.rule_b_id,
                    category=c.category.value,
                    severity=c.severity.value,
                    confidence=c.confidence,
                )

        nodes_data = [{"id": n, **G.nodes[n]} for n in G.nodes]
        links_data = [{"source": u, "target": v, **G.edges[u, v]} for u, v in G.edges]

        connected_count = nx.number_weakly_connected_components(G) if len(G) > 0 else 0
        cycles = list(nx.simple_cycles(G)) if len(G) > 0 else []

        return {
            "nodes": nodes_data,
            "links": links_data,
            "metrics": {
                "total_nodes": G.number_of_nodes(),
                "total_edges": G.number_of_edges(),
                "connected_clusters": connected_count,
                "circular_dependencies": len(cycles),
            },
        }
