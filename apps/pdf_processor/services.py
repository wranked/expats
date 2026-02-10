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

    def extract_tables(self) -> List[Dict[str, Any]]:
        """Extract largest table from all pages of the PDF."""
        extracted_tables = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                table = page.extract_table()
                
                if table:
                    # Convert table to DataFrame for better structure
                    # df = pd.DataFrame(table[2:])
                    extracted_tables.append({
                        'page_number': page_num,
                        'rows': table[2:]
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


class CroatianLaborPDFParser:
    """Specialized parser for Croatian Ministry of Labor PDF tables."""

    def __init__(self, pdf_document: PDFDocument):
        self.pdf_document = pdf_document
        self.extractor = PDFExtractor(pdf_document.file.path)

    def parse_companies_table(self) -> List[Dict[str, Any]]:
        """
        Parse the companies table from the Croatian labor ministry PDF.
        
        Expected table structure (4 columns):
        1. Correlative index (R.BR.)
        2. Company legal name (NAZIV POSLODAVCA)
        3. Company ID/OIB (OIB)
        4. Address (ADRESA)
        
        Returns:
            List of company dictionaries with cleaned data
        """
        companies = []
        skipped_rows = []
        header_keywords = ['r.br', 'naziv', 'oib', 'adresa', 'redni broj']
        
        # Extract all tables from PDF
        tables_data = self.extractor.extract_tables()
        
        for table_info in tables_data:
            page_number = table_info['page_number']
            rows = table_info.get('rows', [])
            
            # Skip if no rows
            if not rows:
                continue
            
            # Remove empty rows (where first cell is None) by merging them with the previous row assuming they are continuations of the previous row
            row_count = 1
            while row_count < len(rows):
                if rows[row_count][0] is None:
                    for j in range(len(rows[row_count])):
                        if rows[row_count-1][j] is not None and rows[row_count][j] is not None:
                            rows[row_count-1][j] += " " + rows[row_count][j]           
                    rows.pop(row_count)
                else:
                    row_count += 1
            

            # Process each row
            for row_values in rows:

                # Clean row values
                row_values = list(filter(None, row_values))

                # Skip if row has less than 4 columns
                if len(row_values) < 4:
                    skipped_rows.append(('less_than_4_cols', row_values))
                    continue
                
                # Skip header rows (check if any cell contains header keywords)
                is_header = False
                for cell in row_values:
                    cell_str = str(cell).lower().strip() if cell else ''
                    if any(keyword in cell_str for keyword in header_keywords):
                        is_header = True
                        break
                
                if is_header:
                    skipped_rows.append(('is_header', row_values))
                    continue
                
                # Clean all values
                cleaned_values = [self._clean_value(v) for v in row_values[:4]]
                index, legal_name, company_id, address = cleaned_values
                
                # Strict validation: skip incomplete rows
                # A valid row must have at least: legal_name and company_id
                if not legal_name:
                    skipped_rows.append(('no_legal_name', row_values))
                    continue
                
                if not company_id:
                    skipped_rows.append(('no_legal_id', row_values))
                    continue
                
                # Company name should be at least 3 characters
                if len(legal_name) < 3:
                    skipped_rows.append(('name_too_short', row_values))
                    continue
                
                company = {
                    'index': index,
                    'legal_name': legal_name,
                    'legal_id': company_id,
                    'address': address,
                    'page_number': page_number
                }
                
                companies.append(company)
        
        return companies

    def _is_valid_oib(self, oib: str) -> bool:
        """Check if the OIB is valid (should not be empty or just whitespace)."""
        if not oib:
            return False
        
        # Remove any whitespace and check if there's something left
        oib_clean = oib.replace(' ', '').strip()
        
        # Just need to ensure it has some content (not all empty/whitespace)
        return len(oib_clean) > 0

    def _clean_value(self, value: Any) -> str:
        """Clean and normalize cell values."""
        if value is None:
            return ''
        
        # Convert to string and strip whitespace
        cleaned = str(value).strip()
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned

    def process_and_save(self) -> ExtractedData:
        """
        Parse the companies table and save as structured data.
        
        Returns:
            ExtractedData instance with structured company data
        """
        companies = self.parse_companies_table()
        
        # Create ExtractedData record
        extracted_data = ExtractedData.objects.create(
            pdf_document=self.pdf_document,
            data_type=DataType.STRUCTURED_COMPANIES,
            raw_data={
                'companies': companies,
                'total_count': len(companies),
                'parser': 'CroatianLaborPDFParser'
            },
            processed=True
        )
        
        return extracted_data
    
    def parse_companies_table_with_debug(self) -> Dict[str, Any]:
        """
        Parse the companies table and return detailed debug information.
        
        Useful for understanding why rows are being filtered.
        
        Returns:
            Dictionary with companies and filtering statistics
        """
        companies = []
        filters = {
            'less_than_4_cols': 0,
            'is_header': 0,
            'no_legal_name': 0,
            'no_legal_id': 0,
            'name_too_short': 0,
        }
        
        header_keywords = ['r.br', 'naziv', 'oib', 'adresa', 'redni broj']
        
        # Extract all tables from PDF
        tables_data = self.extractor.extract_tables()
        
        for table_info in tables_data:
            page_number = table_info['page_number']
            rows = table_info.get('rows', [])
            
            if not rows:
                continue
            
            for row in rows:
                row_values = list(row.values())
                
                if len(row_values) < 4:
                    filters['less_than_4_cols'] += 1
                    continue
                
                is_header = False
                for cell in row_values:
                    cell_str = str(cell).lower().strip() if cell else ''
                    if any(keyword in cell_str for keyword in header_keywords):
                        is_header = True
                        break
                
                if is_header:
                    filters['is_header'] += 1
                    continue
                
                cleaned_values = [self._clean_value(v) for v in row_values[:4]]
                index, legal_name, company_id, address = cleaned_values
                
                if not legal_name:
                    filters['no_legal_name'] += 1
                    continue
                
                if not company_id:
                    filters['no_legal_id'] += 1
                    continue
                
                if len(legal_name) < 3:
                    filters['name_too_short'] += 1
                    continue
                
                company = {
                    'index': index,
                    'legal_name': legal_name,
                    'legal_id': company_id,
                    'address': address,
                    'page_number': page_number
                }
                
                companies.append(company)
        
        return {
            'companies': companies,
            'total_count': len(companies),
            'filters_applied': filters,
            'total_rows_filtered': sum(filters.values())
        }


class WebPDFScraper:
    """Service class for scraping and downloading PDF files from web pages."""

    def __init__(
        self,
        page_url: str,
        search_text: str = None,
        attribute_name: str = None,
        attribute_value: str = None,
        headers: Dict[str, str] = None
    ):
        """
        Initialize the web scraper.
        
        Args:
            page_url: URL of the page to scrape
            search_text: Text to search for to locate the PDF link
            attribute_name: Custom attribute name to search for (e.g., 'data-fileid')
            attribute_value: Custom attribute value to search for
            headers: Optional HTTP headers for the request
        """
        self.page_url = page_url
        self.search_text = search_text
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def find_pdf_link(self) -> str:
        """
        Find PDF download link on the page using either text search or attribute search.
        
        Returns:
            str: Absolute URL of the PDF file
            
        Raises:
            ValueError: If link not found
        """
        if self.attribute_name:
            return self.find_pdf_link_by_attribute()
        elif self.search_text:
            return self.find_pdf_link_by_text()
        else:
            raise ValueError("Either search_text or attribute_name must be provided")

    def find_pdf_link_by_text(self) -> str:
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
            for element in soup.find_all(['p', 'a', 'div', 'span', 'h2', 'h3', 'h4']):
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

    def find_pdf_link_by_attribute(self) -> str:
        """
        Find PDF download link on the page by custom attribute.
        
        Returns:
            str: Absolute URL of the PDF file
            
        Raises:
            ValueError: If attribute or PDF link not found
        """
        try:
            if not self.attribute_name:
                raise ValueError("attribute_name is required for attribute search")

            # Fetch the page
            response = requests.get(self.page_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if self.attribute_value:
                links = soup.find_all('a', attrs={self.attribute_name: self.attribute_value})
            else:
                links = soup.find_all('a', attrs={self.attribute_name: True})

            # Find all links with the specified attribute
            for link in links:
                href = link.get('href', '')
                if href:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(self.page_url, href)
                    return absolute_url
            
            if self.attribute_value:
                raise ValueError(
                    f"No link found with {self.attribute_name}='{self.attribute_value}'"
                )

            raise ValueError(f"No link found with attribute {self.attribute_name}")
            
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

    def download_and_create_document(
        self,
        search_text: str = None,
        attribute_name: str = None,
        attribute_value: str = None
    ) -> PDFDocument:
        """
        Download PDF from found link and create a PDFDocument record.
        
        Args:
            search_text: Optional override for search text
            attribute_name: Optional override for attribute name
            attribute_value: Optional override for attribute value
            
        Returns:
            PDFDocument: Created document instance
            
        Raises:
            ValueError: If download or creation fails
        """
        # Update search parameters if provided
        if search_text:
            self.search_text = search_text
        if attribute_name:
            self.attribute_name = attribute_name
        if attribute_value:
            self.attribute_value = attribute_value
        
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


class CompanySyncService:
    """Service to synchronize companies from PDF data to the Company app."""

    def __init__(self, pdf_document: PDFDocument):
        self.pdf_document = pdf_document

    def sync_companies(self) -> Dict[str, Any]:
        """
        Synchronize companies from PDF to Company app.
        
        Rules:
        - If company exists in Company app (by legal_name or legal_id), skip it
        - If company is in PDF but not in Company app, create it
        
        Returns:
            Dictionary with sync statistics
        """
        from apps.companies.models import Company
        
        # Get parsed company data from PDF
        company_data = self.pdf_document.extracted_data.filter(
            data_type=DataType.STRUCTURED_COMPANIES
        ).first()
        
        if not company_data:
            raise ValueError("No structured company data found. Parse the PDF first using parse_croatian_labor.")
        
        pdf_companies = company_data.raw_data.get('companies', [])
        
        stats = {
            'total_pdf_companies': len(pdf_companies),
            'skipped': 0,
            'created': 0,
            'errors': []
        }
        
        for pdf_company in pdf_companies:
            legal_name = pdf_company.get('legal_name')
            legal_id = pdf_company.get('legal_id')
            address = pdf_company.get('address')
            
            try:
                # Check if company already exists by legal_id or legal_name
                existing = None
                
                if legal_id:
                    existing = Company.objects.filter(legal_id=legal_id).first()
                
                if not existing and legal_name:
                    existing = Company.objects.filter(legal_name__iexact=legal_name).first()
                
                if existing:
                    stats['skipped'] += 1
                    continue
                
                # Create new company
                Company.objects.create(
                    legal_name=legal_name,
                    display_name=legal_name,  # Use legal_name as display_name initially
                    legal_id=legal_id,
                    category='OTHER',  # Default category, can be updated later
                    description=f"Imported from PDF. Address: {address}" if address else "Imported from PDF"
                )
                
                stats['created'] += 1
                
            except Exception as e:
                stats['errors'].append({
                    'legal_name': legal_name,
                    'legal_id': legal_id,
                    'error': str(e)
                })
        
        return stats
