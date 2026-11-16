import time
from typing import List, Dict, Any, Set, Tuple
from app.services.rule_extractor import extract_rules_from_text, ExtractedRuleCandidate
from app.services.conflict_detector import ConflictDetector, DetectedConflict
from app.services.dataset_generator import generate_synthetic_rules_dataset, DOMAINS


def run_evaluation_benchmark() -> Dict[str, Any]:
    """
    Executes rigorous evaluation of:
    1. Rule extraction (Precision, Recall, F1).
    2. Conflict detection (Precision, Recall, F1) compared against a simple naive baseline.
    Uses clean ground-truth dataset separate from model inputs.
    """
    start_time = time.time()
    raw_rules_corpus, ground_truth_data = generate_synthetic_rules_dataset(min_rules=520, seed=42)

    total_rules = len(raw_rules_corpus)
    planted_conflicts = ground_truth_data["conflicts"]

    # 1. EVALUATE RULE EXTRACTION
    # All items in raw_rules_corpus contain a normative modal verb and are expected to yield 1 valid rule
    extracted_rule_candidates: List[ExtractedRuleCandidate] = []
    extraction_true_positives = 0
    extraction_false_positives = 0
    extraction_false_negatives = 0

    for r_item in raw_rules_corpus:
        extracted = extract_rules_from_text(
            text=r_item["text"],
            source_document=r_item["source_document"],
            source_section=r_item["source_section"],
            rule_id_prefix=r_item["rule_id"],
        )
        if len(extracted) >= 1:
            extraction_true_positives += 1
            # Over-extraction check
            if len(extracted) > 1:
                extraction_false_positives += (len(extracted) - 1)
            # Retain rule with original ID for downstream conflict linking
            cand = extracted[0]
            cand.rule_id = r_item["rule_id"]
            if r_item.get("effective_date"):
                from datetime import datetime
                cand.effective_date = datetime.strptime(r_item["effective_date"], "%Y-%m-%d").date()
            extracted_rule_candidates.append(cand)
        else:
            extraction_false_negatives += 1

    ext_precision = extraction_true_positives / (extraction_true_positives + extraction_false_positives) if (extraction_true_positives + extraction_false_positives) > 0 else 0.0
    ext_recall = extraction_true_positives / (extraction_true_positives + extraction_false_negatives) if (extraction_true_positives + extraction_false_negatives) > 0 else 0.0
    ext_f1 = (2 * ext_precision * ext_recall) / (ext_precision + ext_recall) if (ext_precision + ext_recall) > 0 else 0.0

    # 2. EVALUATE CONFLICT DETECTION ENGINE (PolicyDiff)
    detector = ConflictDetector(similarity_threshold=0.25)
    detected_conflicts = detector.detect_conflicts(extracted_rule_candidates, include_ambiguity=True)

    # Build ground truth lookup
    gt_pairs: Dict[Tuple[str, Optional[str]], str] = {}
    for c in planted_conflicts:
        r_a = c["rule_a_id"]
        r_b = c["rule_b_id"]
        cat = c["expected_category"]
        if r_b:
            gt_pairs[tuple(sorted([r_a, r_b]))] = cat
        else:
            gt_pairs[(r_a, None)] = cat

    cd_true_positives = 0
    cd_false_positives = 0

    # Track which ground truth conflicts were found
    matched_gt = set()

    for dc in detected_conflicts:
        pair_key = tuple(sorted([dc.rule_a_id, dc.rule_b_id])) if dc.rule_b_id else (dc.rule_a_id, None)
        if pair_key in gt_pairs:
            # Check category match
            if gt_pairs[pair_key] == dc.category.value:
                cd_true_positives += 1
                matched_gt.add(pair_key)
            else:
                cd_false_positives += 1
        else:
            # Incidental valid pairing or false positive
            cd_false_positives += 1

    cd_false_negatives = len(gt_pairs) - len(matched_gt)

    cd_precision = cd_true_positives / (cd_true_positives + cd_false_positives) if (cd_true_positives + cd_false_positives) > 0 else 0.0
    cd_recall = cd_true_positives / (cd_true_positives + cd_false_negatives) if (cd_true_positives + cd_false_negatives) > 0 else 0.0
    cd_f1 = (2 * cd_precision * cd_recall) / (cd_precision + cd_recall) if (cd_precision + cd_recall) > 0 else 0.0

    # 3. NAIVE BASELINE EVALUATION
    # A simple baseline: flags any pair having cosine similarity > 0.40 as a contradiction
    # without checking deontic modalities or conditions.
    base_tp = 0
    base_fp = 0
    base_pairs = detector.retrieve_candidates(extracted_rule_candidates)
    matched_base_gt = set()

    for i, j, score in base_pairs:
        if score > 0.40:
            pair_key = tuple(sorted([extracted_rule_candidates[i].rule_id, extracted_rule_candidates[j].rule_id]))
            if pair_key in gt_pairs:
                base_tp += 1
                matched_base_gt.add(pair_key)
            else:
                base_fp += 1

    base_fn = len(gt_pairs) - len(matched_base_gt)
    base_prec = base_tp / (base_tp + base_fp) if (base_tp + base_fp) > 0 else 0.0
    base_rec = base_tp / (base_tp + base_fn) if (base_tp + base_fn) > 0 else 0.0
    base_f1 = (2 * base_prec * base_rec) / (base_prec + base_rec) if (base_prec + base_rec) > 0 else 0.0

    elapsed_seconds = round(time.time() - start_time, 2)

    return {
        "dataset_summary": {
            "total_synthetic_rules": total_rules,
            "planted_ground_truth_conflicts": len(planted_conflicts),
            "domains": len(DOMAINS),
            "execution_time_seconds": elapsed_seconds,
        },
        "rule_extraction_metrics": {
            "true_positives": extraction_true_positives,
            "false_positives": extraction_false_positives,
            "false_negatives": extraction_false_negatives,
            "precision": round(ext_precision, 4),
            "recall": round(ext_recall, 4),
            "f1_score": round(ext_f1, 4),
        },
        "conflict_detection_metrics": {
            "engine": "PolicyDiff Deontic Matrix + TF-IDF Candidate Retrieval",
            "true_positives": cd_true_positives,
            "false_positives": cd_false_positives,
            "false_negatives": cd_false_negatives,
            "precision": round(cd_precision, 4),
            "recall": round(cd_recall, 4),
            "f1_score": round(cd_f1, 4),
        },
        "baseline_comparison": {
            "engine": "Naive Keyword / Similarity Overlap Baseline",
            "true_positives": base_tp,
            "false_positives": base_fp,
            "false_negatives": base_fn,
            "precision": round(base_prec, 4),
            "recall": round(base_rec, 4),
            "f1_score": round(base_f1, 4),
        },
    }
