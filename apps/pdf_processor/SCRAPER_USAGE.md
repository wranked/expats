# PDF Web Scraper Usage Guide

## Overview
The `WebPDFScraper` service allows you to scrape web pages and automatically download PDF files by searching for specific text near the PDF link.

## Basic Usage

### API Endpoint

**Endpoint**: `POST /api/pdf-documents/download_from_url/`

**Request Body**:
```json
{
    "page_url": "https://example.com/some-page",
    "search_text": "Text to find near the PDF link"
}
```

**Response**:
```json
{
    "id": 1,
    "file": "/media/pdfs/document.pdf",
    "original_filename": "document.pdf",
    "source_url": "https://example.com/some-page",
    "status": "pending",
    "error_message": "",
    "extracted_data": [],
    "created_at": "2026-02-07T12:34:56Z",
    "modified_at": "2026-02-07T12:34:56Z"
}
```

### Example: Croatian Government Labor Site

To scrape the PDF from the Croatian Ministry of Labor website:

```bash
curl -X POST http://localhost:8000/api/pdf-documents/download_from_url/ \
  -H "Content-Type: application/json" \
  -d '{
    "page_url": "https://mrosp.gov.hr/popisi-poslodavaca-kod-kojih-je-proveden-nadzor-u-podrucju-prijavljivanja-rada/13602",
    "search_text": "Popis poslodavaca kod kojih je tijekom inspekcijskog nadzora zapisnikom utvrđeno postojanje neprijavljenog rada"
  }'
```

## How It Works

1. **Fetch the Page**: The scraper fetches the specified URL using HTTP requests
2. **Parse HTML**: The page HTML is parsed using BeautifulSoup
3. **Find Text**: Searches for the specified search text (case-insensitive)
4. **Locate PDF Link**: Looks for a PDF link (`.pdf` file) near the found text:
   - In the same element
   - In parent elements
   - In next/previous siblings
5. **Download PDF**: Downloads the PDF file from the found link
6. **Create Document**: Creates a `PDFDocument` record with:
   - The downloaded file
   - Original filename (extracted from URL)
   - Source URL (for auditing)
   - Status set to "pending"

## Python Service Usage

```python
from apps.pdf_processor.services import WebPDFScraper

# Initialize scraper
scraper = WebPDFScraper(
    page_url="https://mrosp.gov.hr/popisi-poslodavaca-kod-kojih-je-proveden-nadzor-u-podrucju-prijavljivanja-rada/13602",
    search_text="Popis poslodavaca kod kojih je tijekom inspekcijskog nadzora записnikom utvrđeno postojanje neprijavljenog rada"
)

# Download and create document
try:
    pdf_document = scraper.download_and_create_document()
    print(f"Downloaded: {pdf_document.original_filename}")
except ValueError as e:
    print(f"Error: {e}")
```

## Error Handling

- **Page not found**: Returns HTTP 400 with "Search text not found"
- **PDF link not found**: Returns HTTP 400 with "PDF link not found near the search text"
- **Download failure**: Returns HTTP 400/500 with detailed error message
- **Invalid parameters**: Returns HTTP 400 with "page_url and search_text are required"

## Features

- **Dynamic Link Detection**: Automatically finds PDF links on the page without hardcoding URLs
- **Robust Parsing**: Handles various HTML structures and element types
- **Source Tracking**: Records which page the PDF came from
- **Error Messages**: Detailed error information for debugging
- **Custom Headers**: Supports custom HTTP headers (User-Agent, etc.)

## Extending Configuration

You can also manually control the scraper search by creating one with different parameters:

```python
scraper = WebPDFScraper(
    page_url="https://example.com/page",
    search_text="PDF Report",
    headers={
        'User-Agent': 'Custom User Agent',
        'Accept-Language': 'hr-HR'
    }
)
```

## Next Steps

After downloading a PDF, you can:
1. Process it using the `/api/pdf-documents/{id}/process/` endpoint
2. Extract tables and text from it
3. Access extracted data via `/api/pdf-documents/{id}/extracted_data/`
