import os
from django.utils import timezone
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Document
from .serializers import (
    DocumentListSerializer,
    DocumentDetailSerializer,
    DocumentUploadSerializer,
)
from .tasks import analyze_document_task
from apps.scanner.pdf_export import generate_pdf_report


class DocumentUploadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        doc = Document.objects.create(
            user=request.user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            status='PENDING',
        )

        # Trigger analysis (Celery async or Eager sync)
        try:
            analyze_document_task.delay(doc.id)
        except Exception:
            analyze_document_task(doc.id)

        # Refresh from DB
        doc.refresh_from_db()
        return Response(DocumentDetailSerializer(doc).data, status=status.HTTP_201_CREATED)


class DocumentListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DocumentListSerializer

    def get_queryset(self):
        # Lazy cleanup of expired source files
        expired_docs = Document.objects.filter(
            user=self.request.user,
            file_deleted=False,
            expires_at__isnull=False,
            expires_at__lte=timezone.now()
        )
        for d in expired_docs:
            d.delete_source_file()

        return Document.objects.filter(user=self.request.user)


class DocumentDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DocumentDetailSerializer

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def get_object(self):
        obj = super().get_object()
        # Check if file has expired
        if not obj.file_deleted and obj.expires_at and obj.expires_at <= timezone.now():
            obj.delete_source_file()
            obj.refresh_from_db()
        return obj


class DocumentDownloadPdfView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, *args, **kwargs):
        try:
            doc = Document.objects.get(pk=pk, user=request.user)
        except Document.DoesNotExist:
            return Response({"error": "Документ не найден"}, status=status.HTTP_404_NOT_FOUND)

        findings_data = [
            {
                "pii_type": f.pii_type,
                "type_name": f.type_name,
                "masked_value": f.masked_value,
                "page_number": f.page_number,
                "context": f.context,
            }
            for f in doc.findings.all()
        ]

        uploaded_date_str = doc.uploaded_at.strftime("%d.%m.%Y %H:%M:%S")
        pdf_bytes = generate_pdf_report(
            original_filename=doc.original_filename,
            file_size_bytes=doc.file_size,
            uploaded_at_str=uploaded_date_str,
            risk_level=doc.risk_level,
            risk_summary=doc.risk_summary,
            findings=findings_data,
            file_deleted=doc.file_deleted,
        )

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"report_doc_{doc.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class DocumentDeleteView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete_source_file()
        instance.delete()
