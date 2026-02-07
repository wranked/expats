from django.db import models
from apps.common.models import BaseModel
from .constants import PDFStatus, DataType


class PDFDocument(BaseModel):
    """Model to store uploaded PDF documents."""
    file = models.FileField(upload_to='pdfs/')
    original_filename = models.CharField(max_length=255)
    source_url = models.URLField(null=True, blank=True, help_text="URL the PDF was scraped/downloaded from")
    status = models.CharField(
        max_length=20,
        choices=PDFStatus.choices,
        default=PDFStatus.PENDING
    )
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'pdf_processor_pdfdocument'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_filename} - {self.status}"


class ExtractedData(BaseModel):
    """Model to store data extracted from PDFs."""
    pdf_document = models.ForeignKey(
        PDFDocument,
        on_delete=models.CASCADE,
        related_name='extracted_data'
    )
    data_type = models.CharField(
        max_length=20,
        choices=DataType.choices
    )
    raw_data = models.JSONField()
    processed = models.BooleanField(default=False)
    page_number = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'pdf_processor_extracteddata'
        ordering = ['pdf_document', 'page_number', 'created_at']

    def __str__(self):
        return f"{self.pdf_document.original_filename} - {self.data_type}"
