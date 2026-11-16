import pytest
from datetime import date
from app.schemas.enums import ObligationType, ConflictCategory
from app.services.rule_extractor import extract_rules_from_text
from app.services.conflict_detector import ConflictDetector
from app.services.evaluator import run_evaluation_benchmark


def test_rule_extraction_deontic_modalities():
    text = (
        "All engineers must rotate IAM keys every 90 days.\n"
        "Contractors may not access production environments directly.\n"
        "Staff should verify sender addresses prior to opening attachments.\n"
        "Team members may request sandbox cloud environments."
    )
    rules = extract_rules_from_text(text, source_document="Security Standard", source_section="1.1")
    
    assert len(rules) == 4
    assert rules[0].obligation == ObligationType.MUST
    assert rules[0].action == "rotate"
    assert "IAM keys" in rules[0].target_object
    
    assert rules[1].obligation == ObligationType.MUST_NOT
    assert rules[2].obligation == ObligationType.SHOULD
    assert rules[3].obligation == ObligationType.MAY


def test_rule_extraction_conditions_and_exceptions():
    text = "Employees must book economy flights when traveling domestically, except for flights exceeding 6 hours in duration."
    rules = extract_rules_from_text(text, source_document="Travel Policy", source_section="2.1")
    
    assert len(rules) == 1
    rule = rules[0]
    assert rule.obligation == ObligationType.MUST
    assert any("traveling domestically" in c for c in rule.conditions)
    assert any("exceeding 6 hours" in e for e in rule.exceptions)


def test_direct_contradiction_detection():
    text_a = "Cloud engineers must store production database backups in the primary us-east-1 region."
    text_b = "Cloud engineers must not store production database backups in the primary us-east-1 region."
    
    rule_a = extract_rules_from_text(text_a, source_document="Policy A", source_section="1.0", rule_id_prefix="POL-A")[0]
    rule_b = extract_rules_from_text(text_b, source_document="Policy B", source_section="2.0", rule_id_prefix="POL-B")[0]
    
    detector = ConflictDetector(similarity_threshold=0.3)
    conflicts = detector.detect_conflicts([rule_a, rule_b])
    
    assert len(conflicts) == 1
    assert conflicts[0].category == ConflictCategory.DIRECT_CONTRADICTION
    assert "MUST vs MUST_NOT" in conflicts[0].evidence.clashing_aspect


def test_missing_exception_detection():
    text_a = "All employees must not connect external USB storage drives, except encrypted hardware keys approved by IT."
    text_b = "All employees must not connect external USB storage drives under any circumstances."
    
    rule_a = extract_rules_from_text(text_a, source_document="Endpoint Policy", source_section="1.0", rule_id_prefix="EP-01")[0]
    rule_b = extract_rules_from_text(text_b, source_document="Zero Trust", source_section="1.0", rule_id_prefix="ZT-01")[0]
    
    detector = ConflictDetector(similarity_threshold=0.3)
    conflicts = detector.detect_conflicts([rule_a, rule_b])
    
    assert any(c.category == ConflictCategory.MISSING_EXCEPTION for c in conflicts)


def test_ambiguous_instruction_detection():
    text = "Employees should take commercially reasonable and appropriate measures to safeguard corporate assets."
    rules = extract_rules_from_text(text, source_document="Conduct Policy", source_section="3.0", rule_id_prefix="CND-01")
    
    detector = ConflictDetector()
    conflicts = detector.detect_conflicts(rules)
    
    assert any(c.category == ConflictCategory.AMBIGUOUS_INSTRUCTION for c in conflicts)


def test_networkx_graph_construction():
    text_a = "Engineers must encrypt database backups."
    text_b = "Engineers must not encrypt database backups."
    rule_a = extract_rules_from_text(text_a, rule_id_prefix="R1")[0]
    rule_b = extract_rules_from_text(text_b, rule_id_prefix="R2")[0]
    
    detector = ConflictDetector(similarity_threshold=0.3)
    conflicts = detector.detect_conflicts([rule_a, rule_b])
    graph_data = detector.build_networkx_graph([rule_a, rule_b], conflicts)
    
    assert graph_data["metrics"]["total_nodes"] == 2
    assert graph_data["metrics"]["total_edges"] == 1
    assert len(graph_data["links"]) == 1


def test_evaluation_benchmark_runs_with_500_plus_rules():
    benchmark_results = run_evaluation_benchmark()
    
    assert benchmark_results["dataset_summary"]["total_synthetic_rules"] >= 500
    assert benchmark_results["rule_extraction_metrics"]["f1_score"] >= 0.90
    assert benchmark_results["conflict_detection_metrics"]["recall"] >= 0.80
    # PolicyDiff outperforms naive baseline
    assert benchmark_results["conflict_detection_metrics"]["precision"] > benchmark_results["baseline_comparison"]["precision"]
