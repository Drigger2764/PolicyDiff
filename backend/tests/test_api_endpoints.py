import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.api.v1.endpoints.workspaces import create_workspace, list_workspaces, get_workspace
from app.api.v1.endpoints.rules import validate_structured_rule, create_rule, list_rules
from app.api.v1.endpoints.conflicts import create_conflict, list_conflicts
from app.api.v1.endpoints.reviews import submit_review_decision, get_conflict_reviews
from app.schemas.workspace import WorkspaceCreate
from app.schemas.rule import StructuredRuleRepresentation, RuleCreate
from app.schemas.conflict import ConflictFindingCreate
from app.schemas.review import ReviewDecisionCreate
from app.schemas.enums import (
    ObligationType,
    ConflictCategory,
    ConflictSeverity,
    ConflictStatus,
    ReviewDecisionType,
)
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.section import ExtractedSection


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_workspace_endpoints(db):
    payload = WorkspaceCreate(
        name="Enterprise Information Security",
        slug="infosec",
        description="IT & Cloud Security Governance Policies",
    )
    created = create_workspace(payload=payload, db=db)
    assert created.id is not None
    assert created.name == "Enterprise Information Security"
    assert created.slug == "infosec"

    # List workspaces
    workspaces = list_workspaces(db=db)
    assert len(workspaces) == 1
    assert workspaces[0].slug == "infosec"

    # Get workspace by id
    fetched = get_workspace(workspace_id=created.id, db=db)
    assert fetched.id == created.id


def test_validate_structured_rule_endpoint():
    rule_input = StructuredRuleRepresentation(
        rule_id="HR-EXP-01",
        subject="Employees",
        action="submit",
        target_object="expense receipts",
        conditions=["within 30 calendar days of expense occurrence"],
        obligation=ObligationType.MUST,
        exceptions=["unless hospitalization or medical leave intervened"],
        source_document="Travel & Expense Policy 2024",
        source_section="4.2 Expense Submission Timelines",
    )
    validated = validate_structured_rule(payload=rule_input)
    assert validated.rule_id == "HR-EXP-01"
    assert validated.obligations == ObligationType.MUST
    assert validated.action == "submit"
    assert validated.object == "expense receipts"


def test_conflict_and_review_workflow(db):
    # Setup prerequisite hierarchy
    ws = create_workspace(payload=WorkspaceCreate(name="Finance", slug="finance"), db=db)
    doc = Document(workspace_id=ws.id, title="Travel Policy", category="Finance")
    db.add(doc)
    db.flush()

    ver = DocumentVersion(
        document_id=doc.id,
        version_tag="1.0.0",
        file_name="travel.pdf",
        file_format="pdf",
        file_path="/storage/travel.pdf",
        file_size_bytes=5000,
        status="extracted",
    )
    db.add(ver)
    db.flush()

    sec = ExtractedSection(
        version_id=ver.id,
        heading="Flights",
        raw_text="Employees must book economy class.",
        order_index=1,
    )
    db.add(sec)
    db.flush()

    # Create Rule A and Rule B
    rule_a = create_rule(
        payload=RuleCreate(
            rule_id="FIN-001",
            version_id=ver.id,
            section_id=sec.id,
            subject="Employees",
            obligation=ObligationType.MUST,
            action="book",
            target_object="economy class flights",
            conditions=["for all domestic travel"],
            exceptions=[],
            raw_text="Employees must book economy class flights.",
        ),
        db=db,
    )

    rule_b = create_rule(
        payload=RuleCreate(
            rule_id="FIN-002",
            version_id=ver.id,
            section_id=sec.id,
            subject="Senior Managers",
            obligation=ObligationType.MAY,
            action="book",
            target_object="business class flights",
            conditions=["for flights over 4 hours"],
            exceptions=[],
            raw_text="Senior Managers may book business class flights for flights over 4 hours.",
        ),
        db=db,
    )

    # Create Conflict Finding
    conflict_payload = ConflictFindingCreate(
        workspace_id=ws.id,
        rule_a_id=rule_a.id,
        rule_b_id=rule_b.id,
        category=ConflictCategory.CONDITIONAL_CONTRADICTION,
        severity=ConflictSeverity.HIGH,
        description="General domestic flight policy requires economy, but manager policy allows business class without cross-reference.",
        confidence=0.88,
    )
    conflict = create_conflict(payload=conflict_payload, db=db)
    assert conflict.id is not None
    assert conflict.status == ConflictStatus.PENDING.value

    # Submit Review Decision
    review_payload = ReviewDecisionCreate(
        conflict_id=conflict.id,
        decision=ReviewDecisionType.ACCEPTED_CONFLICT,
        notes="Approved manager exception needs to be integrated as an explicit exception in FIN-001.",
    )
    review = submit_review_decision(payload=review_payload, db=db)
    assert review.id is not None
    assert review.decision == ReviewDecisionType.ACCEPTED_CONFLICT.value

    # Verify conflict status updated to RESOLVED
    conflicts = list_conflicts(workspace_id=ws.id, db=db)
    assert len(conflicts) == 1
    assert conflicts[0].status == ConflictStatus.RESOLVED.value

    # Check reviews listing
    reviews = get_conflict_reviews(conflict_id=conflict.id, db=db)
    assert len(reviews) == 1
    assert reviews[0].notes == review_payload.notes
