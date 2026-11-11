from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from apps.documents.models import Document, Finding


class DocumentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
        self.client.force_authenticate(user=self.user)

    def test_upload_txt_as_doc_fails(self):
        # Only PDF/DOCX allowed
        bad_file = SimpleUploadedFile("test.exe", b"binary content", content_type="application/octet-stream")
        response = self.client.post('/api/documents/upload/', {'file': bad_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_oversized_file_fails(self):
        # 21 MB file
        huge_content = b"x" * (21 * 1024 * 1024)
        huge_file = SimpleUploadedFile("big.pdf", huge_content, content_type="application/pdf")
        response = self.client.post('/api/documents/upload/', {'file': huge_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_documents(self):
        Document.objects.create(user=self.user, original_filename="doc1.pdf", file_size=1024)
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_download_pdf_report(self):
        doc = Document.objects.create(
            user=self.user,
            original_filename="audit.pdf",
            file_size=2048,
            risk_level="LOW",
            risk_summary="Всё чисто",
            status="COMPLETED"
        )
        response = self.client.get(f'/api/documents/{doc.id}/pdf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
