import pdfplumber
from typing import List, Dict, Any
from .pii_rules import find_pii_in_text


def parse_and_scan_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text from each page of a PDF file using pdfplumber,
    and searches for PII entities.
    Returns a list of finding dicts with page numbers.
    """
    findings: List[Dict[str, Any]] = []
    with pdfplumber.open(file_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text:
                page_findings = find_pii_in_text(text, page_number=page_idx)
                findings.extend(page_findings)
    return findings
