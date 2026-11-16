import re
import io
from typing import List, Optional, Tuple
from pydantic import BaseModel


class ParsedSection(BaseModel):
    section_number: Optional[str] = None
    heading: Optional[str] = None
    level: int = 1
    page_start: int = 1
    page_end: int = 1
    raw_text: str
    order_index: int


class DocumentParsingError(Exception):
    pass


class EmptyDocumentError(DocumentParsingError):
    pass


class UnsupportedFormatError(DocumentParsingError):
    pass


# Regex patterns for detecting numbered headings e.g. "1.0 Overview", "4.2.1 Access Controls"
SECTION_HEADING_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)\s+([A-Z][^\n\r]+)", re.MULTILINE)


def extract_from_pdf(file_bytes: bytes) -> List[ParsedSection]:
    """
    Extracts structured sections from PDF bytes using PyMuPDF (fitz).
    Preserves page boundaries, headings, section numbers, and text blocks.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise EmptyDocumentError("PDF file is empty (0 bytes).")

    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise DocumentParsingError("PyMuPDF (fitz) is not installed.")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise DocumentParsingError(f"Corrupted or invalid PDF document: {str(e)}")

    if doc.page_count == 0:
        raise EmptyDocumentError("PDF document has 0 pages.")

    sections: List[ParsedSection] = []
    current_heading = "General"
    current_sec_num = "1.0"
    current_level = 1
    current_text_lines: List[str] = []
    current_page_start = 1
    order_idx = 0

    total_extracted_text = ""

    for page_idx in range(doc.page_count):
        page = doc.load_page(page_idx)
        page_num = page_idx + 1
        blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)

        for b in blocks:
            # block_type 0 is text
            if len(b) >= 5 and b[4]:
                text = b[4].strip()
                if not text:
                    continue

                total_extracted_text += text + "\n"

                # Check if block looks like a heading
                lines = text.split("\n")
                first_line = lines[0].strip()

                match = SECTION_HEADING_PATTERN.match(first_line)
                is_short_caps = len(first_line) < 80 and (first_line.isupper() or first_line.istitle()) and not first_line.endswith(".")

                if match or (is_short_caps and len(lines) == 1):
                    # Flush accumulated section
                    if current_text_lines:
                        body = "\n".join(current_text_lines).strip()
                        if body:
                            sections.append(
                                ParsedSection(
                                    section_number=current_sec_num,
                                    heading=current_heading,
                                    level=current_level,
                                    page_start=current_page_start,
                                    page_end=page_num,
                                    raw_text=body,
                                    order_index=order_idx,
                                )
                            )
                            order_idx += 1
                        current_text_lines = []

                    if match:
                        current_sec_num = match.group(1)
                        current_heading = match.group(2)
                        current_level = len(current_sec_num.split("."))
                    else:
                        current_heading = first_line
                        current_sec_num = f"{order_idx + 1}.0"
                        current_level = 1

                    current_page_start = page_num
                    # Append remaining lines of the block if any
                    if len(lines) > 1:
                        current_text_lines.append("\n".join(lines[1:]))
                else:
                    current_text_lines.append(text)

    # Flush final section
    if current_text_lines:
        body = "\n".join(current_text_lines).strip()
        if body:
            sections.append(
                ParsedSection(
                    section_number=current_sec_num,
                    heading=current_heading,
                    level=current_level,
                    page_start=current_page_start,
                    page_end=doc.page_count,
                    raw_text=body,
                    order_index=order_idx,
                )
            )

    if not total_extracted_text.strip():
        raise EmptyDocumentError("PDF document contains no extractable text content.")

    return sections


def extract_from_docx(file_bytes: bytes) -> List[ParsedSection]:
    """
    Extracts structured sections from DOCX bytes using python-docx.
    Preserves heading styles, numbered prefixes, and ordered paragraphs.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise EmptyDocumentError("DOCX file is empty (0 bytes).")

    try:
        import docx
    except ImportError:
        raise DocumentParsingError("python-docx is not installed.")

    try:
        file_stream = io.BytesIO(file_bytes)
        doc = docx.Document(file_stream)
    except Exception as e:
        raise DocumentParsingError(f"Corrupted or invalid DOCX document: {str(e)}")

    sections: List[ParsedSection] = []
    current_heading = "General"
    current_sec_num = "1.0"
    current_level = 1
    current_text_lines: List[str] = []
    order_idx = 0
    total_text = ""

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        total_text += text + "\n"
        style_name = para.style.name if para.style else ""

        is_heading_style = "Heading" in style_name
        match = SECTION_HEADING_PATTERN.match(text)

        if is_heading_style or match:
            # Flush existing section
            if current_text_lines:
                body = "\n".join(current_text_lines).strip()
                if body:
                    sections.append(
                        ParsedSection(
                            section_number=current_sec_num,
                            heading=current_heading,
                            level=current_level,
                            page_start=1,
                            page_end=1,
                            raw_text=body,
                            order_index=order_idx,
                        )
                    )
                    order_idx += 1
                current_text_lines = []

            if match:
                current_sec_num = match.group(1)
                current_heading = match.group(2)
                current_level = len(current_sec_num.split("."))
            else:
                current_heading = text
                if "Heading 1" in style_name:
                    current_level = 1
                elif "Heading 2" in style_name:
                    current_level = 2
                elif "Heading 3" in style_name:
                    current_level = 3
                else:
                    current_level = 1
                current_sec_num = f"{order_idx + 1}.0"
        else:
            current_text_lines.append(text)

    # Process tables if any
    for table in doc.tables:
        table_rows = []
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                table_rows.append(row_text)
        if table_rows:
            current_text_lines.append("\n".join(table_rows))
            total_text += "\n".join(table_rows) + "\n"

    # Flush final
    if current_text_lines:
        body = "\n".join(current_text_lines).strip()
        if body:
            sections.append(
                ParsedSection(
                    section_number=current_sec_num,
                    heading=current_heading,
                    level=current_level,
                    page_start=1,
                    page_end=1,
                    raw_text=body,
                    order_index=order_idx,
                )
            )

    if not total_text.strip():
        raise EmptyDocumentError("DOCX document contains no extractable text content.")

    return sections


def parse_document(file_name: str, file_bytes: bytes) -> List[ParsedSection]:
    """
    Routes document parsing based on file extension.
    Validates file format and non-empty content.
    """
    ext = file_name.lower().split(".")[-1]
    if ext == "pdf":
        return extract_from_pdf(file_bytes)
    elif ext in ["docx", "doc"]:
        return extract_from_docx(file_bytes)
    else:
        raise UnsupportedFormatError(f"Unsupported file format '.{ext}'. Supported formats are: PDF, DOCX.")
