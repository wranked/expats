import pdfplumber
import pandas as pd
from typing import List, Dict, Any
from .models import PDFDocument, ExtractedData
from .constants import PDFStatus, DataType


class PDFExtractor:
    """Service class for extracting data from PDF files."""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def extract_text(self) -> List[Dict[str, Any]]:
        """Extract text from all pages of the PDF."""
        extracted_pages = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    extracted_pages.append({
                        'page_number': page_num,
                        'content': text.strip()
                    })
        return extracted_pages

    def extract_tables(self) -> List[Dict[str, Any]]:
        """Extract tables from all pages of the PDF."""
        extracted_tables = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_tables = page.extract_tables()
                for table_index, table in enumerate(page_tables):
                    if table and len(table) > 1:
                        # Convert table to DataFrame for better structure
                        df = pd.DataFrame(table[1:], columns=table[0])
                        extracted_tables.append({
                            'page_number': page_num,
                            'table_index': table_index,
                            'headers': table[0],
                            'rows': df.to_dict('records')
                        })
        return extracted_tables


class PDFProcessor:
    """Service class for processing PDF documents."""

    def __init__(self, pdf_document: PDFDocument):
        self.pdf_document = pdf_document

    def process(self) -> None:
        """Process the PDF document: extract text and tables."""
        try:
            # Update status to processing
            self.pdf_document.status = PDFStatus.PROCESSING
            self.pdf_document.save()

            # Initialize extractor
            extractor = PDFExtractor(self.pdf_document.file.path)

            # Extract text
            text_data = extractor.extract_text()
            for page_data in text_data:
                ExtractedData.objects.create(
                    pdf_document=self.pdf_document,
                    data_type=DataType.TEXT,
                    page_number=page_data['page_number'],
                    raw_data={'content': page_data['content']}
                )

            # Extract tables
            table_data = extractor.extract_tables()
            for table in table_data:
                ExtractedData.objects.create(
                    pdf_document=self.pdf_document,
                    data_type=DataType.TABLE,
                    page_number=table['page_number'],
                    raw_data=table
                )

            # Update status to completed
            self.pdf_document.status = PDFStatus.COMPLETED
            self.pdf_document.error_message = ''
            self.pdf_document.save()

        except Exception as e:
            # Update status to failed with error message
            self.pdf_document.status = PDFStatus.FAILED
            self.pdf_document.error_message = str(e)
            self.pdf_document.save()
            raise
