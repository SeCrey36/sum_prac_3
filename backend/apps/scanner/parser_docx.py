import docx
from typing import List, Dict, Any
from .pii_rules import find_pii_in_text


def parse_and_scan_docx(file_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text from paragraphs and tables of a DOCX file using python-docx,
    tracking page breaks or estimating pages, and searches for PII entities.
    """
    doc = docx.Document(file_path)
    findings: List[Dict[str, Any]] = []

    current_page = 1
    word_count_in_page = 0
    current_page_text_chunks: List[str] = []

    def flush_page_findings():
        nonlocal current_page_text_chunks, word_count_in_page
        if current_page_text_chunks:
            full_page_text = "\n".join(current_page_text_chunks)
            page_findings = find_pii_in_text(full_page_text, page_number=current_page)
            findings.extend(page_findings)
            current_page_text_chunks = []
            word_count_in_page = 0

    for paragraph in doc.paragraphs:
        # Check for page break in runs
        has_page_break = False
        for run in paragraph.runs:
            if 'w:br' in run._element.xml and 'w:type="page"' in run._element.xml:
                has_page_break = True

        p_text = paragraph.text.strip()
        if p_text:
            current_page_text_chunks.append(p_text)
            word_count_in_page += len(p_text.split())

        if has_page_break or word_count_in_page > 350:
            flush_page_findings()
            current_page += 1

    # Also parse tables
    for table in doc.tables:
        for row in table.rows:
            row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_texts:
                current_page_text_chunks.append(" | ".join(row_texts))
                word_count_in_page += sum(len(t.split()) for t in row_texts)
                if word_count_in_page > 350:
                    flush_page_findings()
                    current_page += 1

    flush_page_findings()
    return findings
