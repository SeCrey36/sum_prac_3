from django.contrib import admin
from .models import Document, Finding


class FindingInline(admin.TabularInline):
    model = Finding
    extra = 0
    readonly_fields = ('pii_type', 'type_name', 'masked_value', 'page_number', 'context')
    can_delete = False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_filename', 'user', 'status', 'risk_level', 'total_findings', 'uploaded_at', 'file_deleted')
    list_filter = ('status', 'risk_level', 'file_deleted', 'uploaded_at')
    search_fields = ('original_filename', 'user__username', 'user__email')
    readonly_fields = ('uploaded_at', 'expires_at', 'file_deleted', 'file_size', 'total_findings', 'risk_level', 'risk_summary')
    inlines = [FindingInline]


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'pii_type', 'masked_value', 'page_number')
    list_filter = ('pii_type', 'page_number')
    search_fields = ('masked_value', 'context')
