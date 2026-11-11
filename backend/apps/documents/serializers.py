import os
from rest_framework import serializers
from .models import Document, Finding


class FindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finding
        fields = ('id', 'pii_type', 'type_name', 'masked_value', 'page_number', 'context')


class DocumentListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    risk_display = serializers.CharField(source='get_risk_level_display', read_only=True)

    class Meta:
        model = Document
        fields = (
            'id', 'original_filename', 'file_size', 'status', 'status_display',
            'risk_level', 'risk_display', 'total_findings', 'uploaded_at',
            'expires_at', 'file_deleted'
        )


class DocumentDetailSerializer(serializers.ModelSerializer):
    findings = FindingSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    risk_display = serializers.CharField(source='get_risk_level_display', read_only=True)

    class Meta:
        model = Document
        fields = (
            'id', 'original_filename', 'file_size', 'status', 'status_display',
            'risk_level', 'risk_display', 'risk_summary', 'total_findings',
            'uploaded_at', 'expires_at', 'file_deleted', 'error_message', 'findings'
        )


class DocumentUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)

    class Meta:
        model = Document
        fields = ('id', 'file')

    def validate_file(self, value):
        max_size = 20 * 1024 * 1024  # 20 MB limit per TZ
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Размер файла ({round(value.size / (1024 * 1024), 2)} МБ) превышает лимит 20 МБ."
            )

        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ['.pdf', '.docx', '.doc']:
            raise serializers.ValidationError("Поддерживаются только файлы форматов PDF и DOCX.")

        return value
