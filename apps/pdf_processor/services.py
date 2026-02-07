import pdfplumber
import pandas as pd
from typing import List, Dict, Any
from .models import PDFDocument, ExtractedData
from .constants import PDFStatus, DataType
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from django.core.files.base import ContentFile
import os


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


class WebPDFScraper:
    """Service class for scraping and downloading PDF files from web pages."""

    def __init__(self, page_url: str, search_text: str, headers: Dict[str, str] = None):
        """
        Initialize the web scraper.
        
        Args:
            page_url: URL of the page to scrape
            search_text: Text to search for to locate the PDF link
            headers: Optional HTTP headers for the request
        """
        self.page_url = page_url
        self.search_text = search_text
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def find_pdf_link(self) -> str:
        """
        Find PDF download link on the page near the specified search text.
        
        Returns:
            str: Absolute URL of the PDF file
            
        Raises:
            ValueError: If search text or PDF link not found
        """
        try:
            # Fetch the page
            response = requests.get(self.page_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Ensure proper encoding for Croatian text
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the text element
            text_element = None
            for element in soup.find_all(['p', 'div', 'span', 'h2', 'h3', 'h4']):
                if self.search_text.lower() in element.get_text().lower():
                    text_element = element
                    break
            
            if not text_element:
                raise ValueError(f"Search text not found: {self.search_text}")
            
            # Look for PDF link near the found text
            # Check in the same parent, next siblings, or nearby elements
            pdf_link = self._find_pdf_link_in_vicinity(text_element)
            
            if not pdf_link:
                raise ValueError("PDF link not found near the search text")
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(self.page_url, pdf_link)
            return absolute_url
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch page: {str(e)}")

    def _find_pdf_link_in_vicinity(self, element) -> str:
        """
        Find PDF link in the vicinity of the given element.
        Searches in: the element itself, parent, siblings, and nearby elements.
        """
        # Check the element itself and its children
        for link in element.find_all('a', href=True):
            href = link.get('href', '')
            if href.lower().endswith('.pdf'):
                return href
        
        # Check parent element
        parent = element.parent
        if parent:
            for link in parent.find_all('a', href=True):
                href = link.get('href', '')
                if href.lower().endswith('.pdf'):
                    return href
        
        # Check next siblings
        sibling = element.find_next_sibling()
        while sibling and sibling.name:
            for link in sibling.find_all('a', href=True):
                href = link.get('href', '')
                if href.lower().endswith('.pdf'):
                    return href
            sibling = sibling.find_next_sibling()
        
        # Check previous siblings
        sibling = element.find_previous_sibling()
        while sibling and sibling.name:
            for link in sibling.find_all('a', href=True):
                href = link.get('href', '')
                if href.lower().endswith('.pdf'):
                    return href
            sibling = sibling.find_previous_sibling()
        
        return None

    def download_and_create_document(self, search_text: str = None) -> PDFDocument:
        """
        Download PDF from found link and create a PDFDocument record.
        
        Args:
            search_text: Optional override for search text
            
        Returns:
            PDFDocument: Created document instance
            
        Raises:
            ValueError: If download or creation fails
        """
        if search_text:
            self.search_text = search_text
        
        try:
            # Find PDF link
            pdf_url = self.find_pdf_link()
            
            # Download PDF file
            response = requests.get(pdf_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Extract filename from URL
            filename = pdf_url.split('/')[-1].split('?')[0]
            if not filename.lower().endswith('.pdf'):
                filename = f"{filename}.pdf"
            
            # Create PDFDocument
            pdf_document = PDFDocument(
                original_filename=filename,
                source_url=self.page_url,
                status=PDFStatus.PENDING
            )
            
            # Save the file
            pdf_document.file.save(
                filename,
                ContentFile(response.content),
                save=True
            )
            
            return pdf_document
            
        except Exception as e:
            raise ValueError(f"Failed to download and create document: {str(e)}")
