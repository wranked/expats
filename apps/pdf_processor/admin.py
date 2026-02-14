from django.contrib import admin
from .models import PDFDocument, ExtractedData


@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'original_filename', 'status', 'created_at', 'modified_at']
    # list_filter = ['status', 'created_at']
    search_fields = ['original_filename']
    readonly_fields = ['original_filename', 'scraped_url', 'source_url', 'created_at', 'modified_at']


@admin.register(ExtractedData)
class ExtractedDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'pdf_document', 'data_type', 'page_number', 'processed', 'created_at']
    list_filter = ['data_type', 'processed', 'created_at']
    search_fields = ['pdf_document__original_filename']
    readonly_fields = ['created_at', 'modified_at']
