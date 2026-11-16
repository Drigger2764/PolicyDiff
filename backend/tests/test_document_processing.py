import io
import pytest
import fitz  # PyMuPDF
import docx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.workspace import Workspace
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.section import ExtractedSection
from app.services.document_parser import (
    extract_from_pdf,
    extract_from_docx,
    parse_document,
    EmptyDocumentError,
    UnsupportedFormatError,
    DocumentParsingError,
)


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


def generate_sample_pdf() -> bytes:
    """Creates an in-memory 2-page PDF document with structured headings and body text."""
    doc = fitz.open()
    # Page 1
    p1 = doc.new_page()
    p1.insert_text((50, 72), "1.0 Information Security Overview\nAll employees must follow access controls.", fontsize=12)
    p1.insert_text((50, 150), "1.1 Credential Management\nPasswords must be at least 16 characters in length.", fontsize=11)
    
    # Page 2
    p2 = doc.new_page()
    p2.insert_text((50, 72), "2.0 Cloud Infrastructure\nProduction cloud resources must be tagged.", fontsize=12)
    
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def generate_sample_docx() -> bytes:
    """Creates an in-memory DOCX document with headings, paragraphs, and tables."""
    doc = docx.Document()
    doc.add_heading("1.0 Travel and Expense Policy", level=1)
    doc.add_paragraph("Employees must submit expense reports within 30 days of travel completion.")
    
    doc.add_heading("2.0 Flight Bookings", level=2)
    doc.add_paragraph("All domestic flights must be booked in economy class.")
    
    # Add a table
    table = doc.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text = "Role"
    table.rows[0].cells[1].text = "Per Diem Limit"
    table.rows[1].cells[0].text = "Engineer"
    table.rows[1].cells[1].text = "$75 / day"
    
    stream = io.BytesIO()
    doc.save(stream)
    return stream.getvalue()


def test_valid_pdf_extraction():
    pdf_bytes = generate_sample_pdf()
    sections = extract_from_pdf(pdf_bytes)
    
    assert len(sections) >= 2
    assert any("Information Security Overview" in s.heading for s in sections)
    assert any(s.page_start >= 1 for s in sections)
    # Validate text content
    text_corpus = " ".join(s.raw_text for s in sections)
    assert "Passwords must be at least 16 characters" in text_corpus


def test_valid_docx_extraction():
    docx_bytes = generate_sample_docx()
    sections = extract_from_docx(docx_bytes)
    
    assert len(sections) >= 2
    assert any("Travel and Expense Policy" in s.heading for s in sections)
    text_corpus = " ".join(s.raw_text for s in sections)
    assert "domestic flights must be booked in economy" in text_corpus
    assert "Per Diem Limit" in text_corpus


def test_invalid_file_format():
    with pytest.raises(UnsupportedFormatError):
        parse_document("spreadsheet.xlsx", b"some binary data")
        
    with pytest.raises(UnsupportedFormatError):
        parse_document("script.exe", b"binary")


def test_empty_documents():
    # 0 bytes PDF
    with pytest.raises(EmptyDocumentError):
        extract_from_pdf(b"")
        
    # 0 bytes DOCX
    with pytest.raises(EmptyDocumentError):
        extract_from_docx(b"")

    # PDF with empty text
    empty_pdf = fitz.open()
    empty_pdf.new_page()  # Page has no text
    empty_bytes = empty_pdf.tobytes()
    empty_pdf.close()
    with pytest.raises(EmptyDocumentError):
        extract_from_pdf(empty_bytes)


def test_corrupted_document_failure():
    with pytest.raises(DocumentParsingError):
        extract_from_pdf(b"Not a real PDF stream")

    with pytest.raises(DocumentParsingError):
        extract_from_docx(b"Not a real zip archive DOCX")


def test_database_document_and_version_operations(db):
    # Create workspace
    ws = Workspace(name="Legal Ops", slug="legal-ops")
    db.add(ws)
    db.flush()

    # Create document
    doc = Document(workspace_id=ws.id, title="Employee NDA", category="Legal")
    db.add(doc)
    db.flush()

    # Create version
    ver = DocumentVersion(
        document_id=doc.id,
        version_tag="1.0",
        file_name="nda_v1.pdf",
        file_format="pdf",
        file_path="/storage/nda_v1.pdf",
        file_size_bytes=12400,
        status="parsed",
    )
    db.add(ver)
    db.flush()

    # Create sections
    s1 = ExtractedSection(
        version_id=ver.id,
        section_number="1.0",
        heading="Confidential Information",
        level=1,
        raw_text="Employees must not disclose proprietary code.",
        order_index=0,
    )
    db.add(s1)
    db.commit()

    # Query
    queried_doc = db.query(Document).filter(Document.id == doc.id).first()
    assert queried_doc is not None
    assert len(queried_doc.versions) == 1
    assert len(queried_doc.versions[0].sections) == 1
    assert queried_doc.versions[0].sections[0].heading == "Confidential Information"

    # Test deletion cascade
    db.delete(queried_doc)
    db.commit()

    assert db.query(Document).filter(Document.id == doc.id).first() is None
    assert db.query(DocumentVersion).filter(DocumentVersion.document_id == doc.id).first() is None
    assert db.query(ExtractedSection).filter(ExtractedSection.version_id == ver.id).first() is None
