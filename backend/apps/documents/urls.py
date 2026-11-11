from django.urls import path
from .views import (
    DocumentUploadView,
    DocumentListView,
    DocumentDetailView,
    DocumentDownloadPdfView,
    DocumentDeleteView,
)

urlpatterns = [
    path('', DocumentListView.as_view(), name='document_list'),
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/pdf/', DocumentDownloadPdfView.as_view(), name='document_download_pdf'),
    path('<int:pk>/delete/', DocumentDeleteView.as_view(), name='document_delete'),
]
