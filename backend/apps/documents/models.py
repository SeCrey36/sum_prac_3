import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Document(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Ожидает анализа'),
        ('PROCESSING', 'Анализируется'),
        ('COMPLETED', 'Завершено'),
        ('FAILED', 'Ошибка анализа'),
    )

    RISK_CHOICES = (
        ('LOW', 'Низкий'),
        ('MEDIUM', 'Средний'),
        ('CRITICAL', 'Критический'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, default='')

    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default='LOW')
    risk_summary = models.TextField(blank=True, default='')
    total_findings = models.IntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    file_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_filename} ({self.get_status_display()}) - {self.user.username}"

    def delete_source_file(self):
        """Removes the original physical file from disk after expiration."""
        if self.file and not self.file_deleted:
            try:
                if os.path.isfile(self.file.path):
                    os.remove(self.file.path)
            except Exception:
                pass
            self.file = None
            self.file_deleted = True
            self.save(update_fields=['file', 'file_deleted'])


class Finding(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='findings')
    pii_type = models.CharField(max_length=50)
    type_name = models.CharField(max_length=100)
    raw_value = models.CharField(max_length=255)
    masked_value = models.CharField(max_length=255)
    page_number = models.IntegerField(default=1)
    context = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['page_number', 'id']

    def __str__(self):
        return f"[{self.pii_type}] p.{self.page_number}: {self.masked_value}"
