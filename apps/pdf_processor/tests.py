import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import PDFDocument, ExtractedData
from .constants import PDFStatus, DataType


@pytest.mark.django_db
def test_pdf_document_creation():
    pdf_doc = PDFDocument.objects.create(
        file='pdfs/test.pdf',
        original_filename='test.pdf',
        status=PDFStatus.PENDING
    )
    assert pdf_doc.status == PDFStatus.PENDING
    assert str(pdf_doc) == 'test.pdf - pending'


@pytest.mark.django_db
def test_extracted_data_creation():
    pdf_doc = PDFDocument.objects.create(
        file='pdfs/test.pdf',
        original_filename='test.pdf',
    )
    extracted = ExtractedData.objects.create(
        pdf_document=pdf_doc,
        data_type=DataType.TEXT,
        page_number=1,
        raw_data={'content': 'Sample text'}
    )
    assert extracted.data_type == DataType.TEXT
    assert str(extracted) == 'test.pdf - text'
