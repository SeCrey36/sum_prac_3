import os
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Document, Finding
from apps.scanner.parser_pdf import parse_and_scan_pdf
from apps.scanner.parser_docx import parse_and_scan_docx
from apps.scanner.risk_engine import calculate_risk


@shared_task(bind=True)
def analyze_document_task(self, document_id: int):
    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        return {"status": "error", "message": "Document not found"}

    document.status = 'PROCESSING'
    document.save(update_fields=['status'])

    try:
        if not document.file or not os.path.exists(document.file.path):
            raise FileNotFoundError("Исходный файл документа не найден на сервере.")

        file_path = document.file.path
        filename_lower = document.original_filename.lower()

        if filename_lower.endswith('.pdf'):
            raw_findings = parse_and_scan_pdf(file_path)
        elif filename_lower.endswith(('.docx', '.doc')):
            raw_findings = parse_and_scan_docx(file_path)
        else:
            raise ValueError("Поддерживаются только форматы PDF и DOCX.")

        # Save findings
        findings_to_create = [
            Finding(
                document=document,
                pii_type=item['pii_type'],
                type_name=item['type_name'],
                raw_value=item['raw_value'],
                masked_value=item['masked_value'],
                page_number=item['page_number'],
                context=item.get('context', ''),
            )
            for item in raw_findings
        ]
        Finding.objects.bulk_create(findings_to_create)

        # Risk calculation
        risk_level, risk_summary, _ = calculate_risk(raw_findings)

        document.status = 'COMPLETED'
        document.risk_level = risk_level
        document.risk_summary = risk_summary
        document.total_findings = len(raw_findings)
        document.expires_at = timezone.now() + timedelta(hours=1)
        document.save(update_fields=['status', 'risk_level', 'risk_summary', 'total_findings', 'expires_at'])

        # Schedule automatic file deletion in 3600 seconds (1 hour)
        try:
            delete_document_file_task.apply_async((document.id,), countdown=3600)
        except Exception:
            # If celery broker is not active, file deletion can also be triggered during cleanup
            pass

        return {"status": "success", "findings_count": len(raw_findings), "risk": risk_level}

    except Exception as exc:
        document.status = 'FAILED'
        document.error_message = str(exc)
        document.save(update_fields=['status', 'error_message'])
        return {"status": "error", "message": str(exc)}


@shared_task
def delete_document_file_task(document_id: int):
    try:
        document = Document.objects.get(id=document_id)
        document.delete_source_file()
        return {"status": "deleted", "document_id": document_id}
    except Document.DoesNotExist:
        return {"status": "not_found", "document_id": document_id}
