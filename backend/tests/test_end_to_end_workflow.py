import io
import pytest
import fitz
import docx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.workspace import Workspace
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.section import ExtractedSection
from app.models.rule import ExtractedRule
from app.models.conflict import ConflictFinding
from app.models.review import ReviewDecision
from app.services.document_parser import extract_from_pdf, extract_from_docx
from app.services.rule_extractor import extract_rules_from_text
from app.services.conflict_detector import ConflictDetector, ConflictCategory, ConflictSeverity, ConflictStatus
from app.api.v1.endpoints.conflicts import trigger_conflict_detection, review_conflict
from app.api.v1.endpoints.audit import generate_audit_report
from app.schemas.review import ReviewDecisionCreate


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


def test_complete_end_to_end_workflow(db):
    # Step 1: Create Workspace
    ws = Workspace(name="Global Risk & Compliance", slug="global-risk", description="Enterprise governance standards")
    db.add(ws)
    db.commit()
    db.refresh(ws)
    assert ws.id is not None

    # Step 2: Create Policy A (PDF) - Baseline Access Policy
    pdf_doc = fitz.open()
    p1 = pdf_doc.new_page()
    p1.insert_text((50, 72), "1.0 Remote Access Protocol\nAll personnel must use multi-factor authentication when accessing corporate networks remotely.", fontsize=12)
    p1.insert_text((50, 150), "2.0 Backup Policy\nCloud engineers must store production database backups in the primary us-east-1 region.", fontsize=12)
    pdf_bytes = pdf_doc.tobytes()
    pdf_doc.close()

    parsed_pdf_sections = extract_from_pdf(pdf_bytes)
    assert len(parsed_pdf_sections) >= 2

    doc_a = Document(workspace_id=ws.id, title="Baseline Access Policy", category="Information Security")
    db.add(doc_a)
    db.flush()

    ver_a = DocumentVersion(
        document_id=doc_a.id,
        version_tag="1.0.0",
        file_name="Access_Policy_v1.pdf",
        file_format="pdf",
        file_path="/storage/test_a.pdf",
        file_size_bytes=len(pdf_bytes),
        status="parsed",
    )
    db.add(ver_a)
    db.flush()

    for s in parsed_pdf_sections:
        sec = ExtractedSection(
            version_id=ver_a.id,
            section_number=s.section_number,
            heading=s.heading,
            level=s.level,
            page_start=s.page_start,
            page_end=s.page_end,
            raw_text=s.raw_text,
            order_index=s.order_index,
        )
        db.add(sec)
    db.commit()

    # Step 3: Create Policy B (DOCX) - Regional Guidelines containing planted contradiction
    docx_file = docx.Document()
    docx_file.add_heading("1.0 Disaster Recovery Restrictions", level=1)
    docx_file.add_paragraph("Cloud engineers must not store production database backups in the primary us-east-1 region.")
    docx_stream = io.BytesIO()
    docx_file.save(docx_stream)
    docx_bytes = docx_stream.getvalue()

    parsed_docx_sections = extract_from_docx(docx_bytes)
    assert len(parsed_docx_sections) >= 1

    doc_b = Document(workspace_id=ws.id, title="Disaster Recovery Guideline", category="Information Security")
    db.add(doc_b)
    db.flush()

    ver_b = DocumentVersion(
        document_id=doc_b.id,
        version_tag="1.0.0",
        file_name="DR_Guidelines.docx",
        file_format="docx",
        file_path="/storage/test_b.docx",
        file_size_bytes=len(docx_bytes),
        status="parsed",
    )
    db.add(ver_b)
    db.flush()

    for s in parsed_docx_sections:
        sec = ExtractedSection(
            version_id=ver_b.id,
            section_number=s.section_number,
            heading=s.heading,
            level=s.level,
            page_start=s.page_start,
            page_end=s.page_end,
            raw_text=s.raw_text,
            order_index=s.order_index,
        )
        db.add(sec)
    db.commit()

    # Step 4: Trigger Automated Conflict Detection
    findings = trigger_conflict_detection(workspace_id=ws.id, db=db)
    assert len(findings) >= 1

    # Step 5: Verify Evidence References
    contradiction = next((f for f in findings if f.category == ConflictCategory.DIRECT_CONTRADICTION.value), None)
    assert contradiction is not None
    assert contradiction.rule_a is not None
    assert contradiction.rule_b is not None
    assert "must store" in contradiction.rule_a.raw_text.lower()
    assert "must not store" in contradiction.rule_b.raw_text.lower()
    assert contradiction.severity == ConflictSeverity.CRITICAL.value

    # Step 6: Review Determination
    review_res = review_conflict(
        conflict_id=contradiction.id,
        payload=ReviewDecisionCreate(
            conflict_id=contradiction.id,
            decision="ACCEPTED_CONFLICT",
            notes="Acknowledged direct contradiction between baseline backup policy and disaster recovery restriction.",
            action_taken="Ticket SEC-991 logged for cross-departmental policy alignment.",
        ),
        db=db,
    )
    assert review_res.decision == "ACCEPTED_CONFLICT"
    assert contradiction.status == ConflictStatus.RESOLVED.value

    # Step 7: Audit Report Generation
    audit_report = generate_audit_report(workspace_id=ws.id, db=db)
    assert audit_report["workspace"]["id"] == ws.id
    assert audit_report["statistics"]["total_documents"] == 2
    assert audit_report["statistics"]["total_conflicts_detected"] >= 1
    assert audit_report["statistics"]["resolved_conflicts"] >= 1
    assert audit_report["statistics"]["resolution_rate_percent"] > 0
