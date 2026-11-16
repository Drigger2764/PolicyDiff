import pytest
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.workspace import Workspace
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.section import ExtractedSection
from app.models.rule import ExtractedRule
from app.models.conflict import ConflictFinding
from app.models.review import ReviewDecision

from app.schemas.enums import (
    ObligationType,
    ConflictCategory,
    ConflictSeverity,
    ConflictStatus,
    ReviewDecisionType,
)
from app.schemas.rule import StructuredRuleRepresentation


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_structured_rule_representation():
    """Validates the 9-tuple structured rule schema representation."""
    rule_data = {
        "rule_id": "SEC-R001",
        "subject": "System Administrators",
        "action": "rotate",
        "object": "API keys and database credentials",
        "conditions": ["every 90 days", "immediately upon personnel offboarding"],
        "obligations": "MUST",
        "exceptions": ["service accounts with hardware security modules"],
        "source_document": "Global IT Security Policy v2.0",
        "source_section": "Section 4.3 - Access Management",
    }
    
    rule = StructuredRuleRepresentation(**rule_data)
    assert rule.rule_id == "SEC-R001"
    assert rule.subject == "System Administrators"
    assert rule.action == "rotate"
    assert rule.object == "API keys and database credentials"
    assert len(rule.conditions) == 2
    assert rule.obligations == ObligationType.MUST
    assert len(rule.exceptions) == 1
    assert rule.source_document == "Global IT Security Policy v2.0"
    assert rule.source_section == "Section 4.3 - Access Management"


def test_conflict_categories_taxonomy():
    """Validates that all six required conflict categories exist and validate."""
    expected_categories = [
        "Direct contradiction",
        "Conditional contradiction",
        "Missing exception",
        "Superseded rule",
        "Ambiguous instruction",
        "Harmless wording change",
    ]
    for category in expected_categories:
        enum_val = ConflictCategory(category)
        assert enum_val.value == category


def test_database_entities_full_lifecycle(db_session):
    """Verifies that all 8 core database entities persist and relate properly."""
    # 1. User
    user = User(
        email="analyst@policydiff.internal",
        full_name="Alice Security Analyst",
        hashed_password="hashed_pw_test",
        role="analyst",
    )
    db_session.add(user)
    db_session.flush()
    assert user.id is not None

    # 2. Workspace
    workspace = Workspace(
        name="Enterprise Information Security",
        slug="infosec",
        description="IT & Cloud Security Governance Policies",
    )
    db_session.add(workspace)
    db_session.flush()
    assert workspace.id is not None

    # 3. Document
    doc = Document(
        workspace_id=workspace.id,
        title="Access Control Policy",
        category="Security",
        description="Authentication and Authorization protocols",
    )
    db_session.add(doc)
    db_session.flush()

    # 4. Document Version
    version_1 = DocumentVersion(
        document_id=doc.id,
        version_tag="1.0.0",
        file_name="Access_Control_v1.pdf",
        file_format="pdf",
        file_path="/storage/policies/Access_Control_v1.pdf",
        file_size_bytes=1048576,
        status="extracted",
        effective_date=date(2023, 1, 1),
        uploaded_by=user.id,
    )
    db_session.add(version_1)
    db_session.flush()

    # 5. Extracted Section
    section = ExtractedSection(
        version_id=version_1.id,
        section_number="2.1",
        heading="MFA Requirements",
        level=2,
        page_start=4,
        page_end=4,
        raw_text="All employees must authenticate using multi-factor authentication for remote access.",
        order_index=1,
    )
    db_session.add(section)
    db_session.flush()

    # 6. Extracted Rules
    rule_a = ExtractedRule(
        rule_id="SEC-V1-R001",
        version_id=version_1.id,
        section_id=section.id,
        subject="All employees",
        obligation="MUST",
        action="authenticate",
        target_object="multi-factor authentication",
        conditions=["for remote access"],
        exceptions=[],
        raw_text=section.raw_text,
        confidence_score=0.98,
    )
    rule_b = ExtractedRule(
        rule_id="SEC-V1-R002",
        version_id=version_1.id,
        section_id=section.id,
        subject="Contractors",
        obligation="MAY",
        action="authenticate",
        target_object="single-factor credentials",
        conditions=["when on VPN"],
        exceptions=[],
        raw_text="Contractors may authenticate with single-factor credentials when on VPN.",
        confidence_score=0.92,
    )
    db_session.add_all([rule_a, rule_b])
    db_session.flush()

    # 7. Conflict Finding
    conflict = ConflictFinding(
        workspace_id=workspace.id,
        rule_a_id=rule_a.id,
        rule_b_id=rule_b.id,
        category=ConflictCategory.DIRECT_CONTRADICTION.value,
        severity=ConflictSeverity.CRITICAL.value,
        description="Rule SEC-V1-R001 mandates MFA for all remote access while Rule SEC-V1-R002 allows single-factor for contractors on VPN.",
        confidence=0.95,
        status=ConflictStatus.PENDING.value,
    )
    db_session.add(conflict)
    db_session.flush()

    # 8. Review Decision
    review = ReviewDecision(
        conflict_id=conflict.id,
        reviewer_id=user.id,
        decision=ReviewDecisionType.ACCEPTED_CONFLICT.value,
        notes="Confirmed contradiction: contractor policy has not been aligned with 2024 zero-trust mandate.",
        action_taken="Ticket SEC-891 created to update contractor handbook.",
    )
    db_session.add(review)
    db_session.commit()

    # Assert relations
    assert len(workspace.documents) == 1
    assert len(doc.versions) == 1
    assert len(version_1.sections) == 1
    assert len(version_1.rules) == 2
    assert len(conflict.reviews) == 1
    assert conflict.reviews[0].reviewer.email == "analyst@policydiff.internal"
