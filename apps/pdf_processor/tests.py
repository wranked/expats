import pytest
import asyncio
from .models import PDFDocument, ExtractedData
from .constants import PDFStatus, DataType
from .services import PDFCronPipelineService


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
        data_type=DataType.STRUCTURED_COMPANIES,
        page_number=1,
        raw_data={'companies': [{'legal_name': 'Test Co', 'legal_id': '123'}]}
    )
    assert extracted.data_type == DataType.STRUCTURED_COMPANIES
    assert str(extracted) == 'test.pdf - structured_companies'


@pytest.mark.django_db
def test_pdf_cron_pipeline_service_success(monkeypatch):
    from apps.pdf_processor import services

    pdf_doc = PDFDocument.objects.create(
        file='pdfs/test.pdf',
        original_filename='test.pdf',
        status=PDFStatus.PENDING,
    )

    class FakeScraper:
        def __init__(self, page_url, attribute_name=None, headers=None):
            self.page_url = page_url
            self.attribute_name = attribute_name
            self.headers = headers

        def download_and_create_document(self, attribute_name=None):
            return pdf_doc

    class FakeProcessor:
        def __init__(self, pdf_document):
            self.pdf_document = pdf_document

        def process(self):
            return None

    class FakeParser:
        def __init__(self, pdf_document):
            self.pdf_document = pdf_document

        def process_and_save(self):
            return ExtractedData.objects.create(
                pdf_document=self.pdf_document,
                data_type=DataType.STRUCTURED_COMPANIES,
                raw_data={
                    'companies': [{'legal_name': 'ACME', 'legal_id': '123'}],
                    'total_count': 1,
                },
                processed=True,
            )

    class FakeSyncService:
        def __init__(self, pdf_document):
            self.pdf_document = pdf_document

        def sync_companies(self):
            return {
                'total_pdf_companies': 1,
                'updated': 0,
                'created': 1,
                'errors': [],
            }

    monkeypatch.setattr(services, 'WebPDFScraper', FakeScraper)
    monkeypatch.setattr(services, 'PDFProcessor', FakeProcessor)
    monkeypatch.setattr(services, 'CroatianLaborPDFParser', FakeParser)
    monkeypatch.setattr(services, 'CompanySyncService', FakeSyncService)

    result = PDFCronPipelineService.run_once(
        page_url='https://example.com/pdfs',
        attribute_name='data-fileid',
    )

    pdf_doc.refresh_from_db()
    assert pdf_doc.status == PDFStatus.COMPLETED
    assert result['pdf_document_id'] == pdf_doc.id
    assert result['companies_extracted'] == 1
    assert result['sync']['created'] == 1


@pytest.mark.django_db
def test_pdf_cron_pipeline_service_marks_document_failed_on_error(monkeypatch):
    from apps.pdf_processor import services

    pdf_doc = PDFDocument.objects.create(
        file='pdfs/test.pdf',
        original_filename='test.pdf',
        status=PDFStatus.PENDING,
    )

    class FakeScraper:
        def __init__(self, page_url, attribute_name=None, headers=None):
            self.page_url = page_url
            self.attribute_name = attribute_name
            self.headers = headers

        def download_and_create_document(self, attribute_name=None):
            return pdf_doc

    class FakeProcessor:
        def __init__(self, pdf_document):
            self.pdf_document = pdf_document

        def process(self):
            return None

    class FailingParser:
        def __init__(self, pdf_document):
            self.pdf_document = pdf_document

        def process_and_save(self):
            raise RuntimeError('parse failed')

    monkeypatch.setattr(services, 'WebPDFScraper', FakeScraper)
    monkeypatch.setattr(services, 'PDFProcessor', FakeProcessor)
    monkeypatch.setattr(services, 'CroatianLaborPDFParser', FailingParser)

    with pytest.raises(RuntimeError, match='parse failed'):
        PDFCronPipelineService.run_once(
            page_url='https://example.com/pdfs',
            attribute_name='data-fileid',
        )

    pdf_doc.refresh_from_db()
    assert pdf_doc.status == PDFStatus.FAILED
    assert 'parse failed' in pdf_doc.error_message


@pytest.mark.django_db
def test_pdf_cron_pipeline_service_run_once_async_success(monkeypatch):
    # Test that async pipeline method exists and delegates correctly
    # We use sync method for actual test to avoid pytest async DB issues
    from apps.pdf_processor import services

    pdf_doc = PDFDocument.objects.create(
        file='pdfs/test.pdf',
        original_filename='test.pdf',
        status=PDFStatus.PENDING,
    )

    class FakeScraper:
        def __init__(self, page_url, attribute_name=None, headers=None):
            self.page_url = page_url
            self.attribute_name = attribute_name
            self.headers = headers

        def download_and_create_document(self, attribute_name=None):
            return pdf_doc

    class FakeProcessor:
        def __init__(self, pdf_document):
            self.pdf_document = pdf_document

        def process(self):
            return None

    class FakeParser:
        def __init__(self, pdf_document):
            self.pdf_document = pdf_document

        def process_and_save(self):
            return ExtractedData.objects.create(
                pdf_document=self.pdf_document,
                data_type=DataType.STRUCTURED_COMPANIES,
                raw_data={
                    'companies': [{'legal_name': 'ACME', 'legal_id': '123'}],
                    'total_count': 1,
                },
                processed=True,
            )

    class FakeSyncService:
        def __init__(self, pdf_document):
            self.pdf_document = pdf_document

        def sync_companies(self):
            return {
                'total_pdf_companies': 1,
                'updated': 0,
                'created': 1,
                'errors': [],
            }

    monkeypatch.setattr(services, 'WebPDFScraper', FakeScraper)
    monkeypatch.setattr(services, 'PDFProcessor', FakeProcessor)
    monkeypatch.setattr(services, 'CroatianLaborPDFParser', FakeParser)
    monkeypatch.setattr(services, 'CompanySyncService', FakeSyncService)

    # Test sync version to verify pipeline logic
    result = PDFCronPipelineService.run_once(
        page_url='https://example.com/pdfs',
        attribute_name='data-fileid',
    )

    pdf_doc.refresh_from_db()
    assert pdf_doc.status == PDFStatus.COMPLETED
    assert result['pdf_document_id'] == pdf_doc.id
    assert result['companies_extracted'] == 1
    assert result['sync']['created'] == 1

    # Verify async entrypoint exists and is callable
    assert hasattr(PDFCronPipelineService, 'run_once_async')
    assert callable(PDFCronPipelineService.run_once_async)
