# Croatian Labor Ministry PDF Parser

## Overview
The `CroatianLaborPDFParser` is a specialized parser for extracting structured company data from Croatian Ministry of Labor inspection PDFs.

## PDF Format
These PDFs contain a table with the following structure:
- **R.BR.** (Correlative index): Sequential number
- **NAZIV POSLODAVCA** (Company legal name): Full legal name of the company
- **OIB** (Company ID): Croatian tax identification number
- **ADRESA** (Address): Company address

The table header is repeated on every page, and the first page contains a title before the table starts.

## API Endpoints

### 1. Parse Croatian Labor PDF

**Endpoint**: `POST /api/pdf-documents/{id}/parse_croatian_labor/`

Parses the PDF and extracts structured company data.

**Example**:
```bash
curl -X POST http://localhost:8000/api/pdf-documents/1/parse_croatian_labor/
```

**Response**:
```json
{
    "id": 1,
    "data_type": "structured_companies",
    "companies": [
        {
            "index": "1",
            "legal_name": "COMPANY NAME d.o.o.",
            "company_id": "12345678901",
            "address": "Street Name 123, 10000 Zagreb",
            "page_number": 1
        },
        ...
    ],
    "total_count": 150,
    "created_at": "2026-02-07T14:30:00Z"
}
```

### 2. Get Parsed Companies

**Endpoint**: `GET /api/pdf-documents/{id}/companies/`

Retrieves previously parsed company data.

**Example**:
```bash
curl -X GET http://localhost:8000/api/pdf-documents/1/companies/
```

**Response**:
```json
{
    "companies": [...],
    "total_count": 150,
    "parsed_at": "2026-02-07T14:30:00Z"
}
```

If the document hasn't been parsed yet:
```json
{
    "companies": [],
    "total_count": 0,
    "message": "No structured company data found. Use parse_croatian_labor endpoint first."
}
```

## Complete Workflow

### Step 1: Download PDF from Government Website
```bash
curl -X POST http://localhost:8000/api/pdf-documents/download_from_url/ \
  -H "Content-Type: application/json" \
  -d '{
    "page_url": "https://mrosp.gov.hr/popisi-poslodavaca-kod-kojih-je-proveden-nadzor-u-podrucju-prijavljivanja-rada/13602",
    "attribute_name": "data-fileid"
  }'
```

**Response**: Returns PDFDocument with `id: 1`

### Step 2: Parse the PDF
```bash
curl -X POST http://localhost:8000/api/pdf-documents/1/parse_croatian_labor/
```

**Response**: Returns structured company data

### Step 3: Retrieve Parsed Data (Optional)
```bash
curl -X GET http://localhost:8000/api/pdf-documents/1/companies/
```

## Python Service Usage

```python
from apps.pdf_processor.services import CroatianLaborPDFParser
from apps.pdf_processor.models import PDFDocument

# Get the PDF document
pdf_document = PDFDocument.objects.get(id=1)

# Parse the document
parser = CroatianLaborPDFParser(pdf_document)
extracted_data = parser.process_and_save()

# Access the companies
companies = extracted_data.raw_data['companies']
total_count = extracted_data.raw_data['total_count']

for company in companies:
    print(f"{company['legal_name']} - {company['company_id']}")
```

## Data Processing Features

- **Header Detection**: Automatically skips duplicate table headers on each page
- **Data Cleaning**: Removes extra whitespace and normalizes text
- **Empty Row Filtering**: Ignores empty rows in the table
- **Page Tracking**: Records which page each company was found on
- **Validation**: Only includes rows with at least a company name

## Data Structure

Each company entry contains:
```python
{
    'index': str,           # Sequential number from the table
    'legal_name': str,     # Full legal company name
    'company_id': str,     # Croatian OIB (tax ID)
    'address': str,        # Company address
    'page_number': int     # Page number where found
}
```

## Error Handling

- If PDF is already being processed: Returns HTTP 400
- If parsing fails: Updates document status to 'failed' and returns HTTP 500
- If no company data found after parsing: Returns empty list with message

## Notes

- The parser uses `pdfplumber` to extract tables
- It's specifically designed for Croatian Ministry of Labor PDF format
- Header keywords: 'r.br', 'naziv', 'oib', 'adresa'
- Can handle multi-page documents with repeated headers
