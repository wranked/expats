# PDF Web Scraper Usage Guide

## Overview
The `WebPDFScraper` service allows you to scrape web pages and automatically download PDF files using two methods:
1. **Text-based search**: Find PDF links near specified text
2. **Attribute-based search**: Find PDF links by custom HTML attributes (e.g., `data-fileid`)

## API Endpoint

**Endpoint**: `POST /api/pdf-documents/download_from_url/`

## Method 1: Text-Based Search

Find a PDF link near specific text on the page.

**Request Body**:
```json
{
    "page_url": "https://example.com/some-page",
    "search_text": "Text to find near the PDF link"
}
```

**Example - Croatian Government Labor Site**:
```bash
curl -X POST http://localhost:8000/api/pdf-documents/download_from_url/ \
  -H "Content-Type: application/json" \
  -d '{
    "page_url": "https://mrosp.gov.hr/popisi-poslodavaca-kod-kojih-je-proveden-nadzor-u-podrucju-prijavljivanja-rada/13602",
    "search_text": "Popis poslodavaca kod kojih je tijekom inspekcijskog nadzora zapisnikom utvrđeno postojanje neprijavljenog rada"
  }'
```

## Method 2: Attribute-Based Search

Find a PDF link by looking for a specific HTML attribute. This is useful when the page uses custom data attributes like `data-fileid`.

**Request Body**:
```json
{
    "page_url": "https://example.com/some-page",
    "attribute_name": "data-fileid",
    "attribute_value": "12345"
}
```

**Example - Using data-fileid attribute (specific value)**:
```bash
curl -X POST http://localhost:8000/api/pdf-documents/download_from_url/ \
  -H "Content-Type: application/json" \
  -d '{
    "page_url": "https://mrosp.gov.hr/popisi-poslodavaca-kod-kojih-je-proveden-nadzor-u-podrucju-prijavljivanja-rada/13602",
    "attribute_name": "data-fileid",
        "attribute_value": "19791"
  }'
```

**Example - Using data-fileid attribute (any value)**:
```bash
curl -X POST http://localhost:8000/api/pdf-documents/download_from_url/ \
    -H "Content-Type: application/json" \
    -d '{
        "page_url": "https://mrosp.gov.hr/popisi-poslodavaca-kod-kojih-je-proveden-nadzor-u-podrucju-prijavljivanja-rada/13602",
        "attribute_name": "data-fileid"
    }'
```

## Response

Both methods return the same response format:

## Response

Both methods return the same response format:

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

## How It Works

### Text-Based Search
1. **Fetch the Page**: Downloads the HTML from the specified URL
2. **Parse HTML**: Parses the page using BeautifulSoup
3. **Find Text**: Searches for the specified text (case-insensitive)
4. **Locate PDF Link**: Looks for a PDF link (`.pdf` file) near the found text:
   - In the same element
   - In parent elements
   - In next/previous siblings
5. **Download PDF**: Downloads the file from the found link
6. **Create Document**: Creates a PDFDocument record

### Attribute-Based Search
1. **Fetch the Page**: Downloads the HTML from the specified URL
2. **Parse HTML**: Parses the page using BeautifulSoup
3. **Find Attribute**: Looks for `<a>` tags with the specified attribute name (and optional value)
4. **Extract Link**: Gets the `href` from the first matching element
5. **Download PDF**: Downloads the file from the found link
6. **Create Document**: Creates a PDFDocument record

## Python Service Usage

### Text-Based
```python
from apps.pdf_processor.services import WebPDFScraper

scraper = WebPDFScraper(
    page_url="https://example.com/page",
    search_text="Download PDF Report"
)

try:
    pdf_document = scraper.download_and_create_document()
    print(f"Downloaded: {pdf_document.original_filename}")
except ValueError as e:
    print(f"Error: {e}")
```

### Attribute-Based
```python
from apps.pdf_processor.services import WebPDFScraper

scraper = WebPDFScraper(
    page_url="https://example.com/page",
    attribute_name="data-fileid",
    attribute_value="12345"
)

try:
    pdf_document = scraper.download_and_create_document()
    print(f"Downloaded: {pdf_document.original_filename}")
except ValueError as e:
    print(f"Error: {e}")
```

## Error Handling

- **page_url missing**: Returns HTTP 400 with "page_url is required"
- **No search method provided**: Returns HTTP 400 with "Either search_text or both attribute_name and attribute_value are required"
- **Text not found**: Returns HTTP 400 with "Search text not found: ..."
- **Attribute not found**: Returns HTTP 400 with "No link found with attribute_name='...'"
- **PDF link not found**: Returns HTTP 400 with "PDF link not found near the search text"
- **Download failure**: Returns HTTP 400/500 with detailed error message
- **Page fetch failure**: Returns HTTP 400 with "Failed to fetch page: ..."

## Tips

### Finding the Right Attribute
Use browser developer tools to inspect the page:
1. Right-click on the PDF link → "Inspect"
2. Look for custom attributes like:
   - `data-fileid`
   - `data-url`
   - `data-file`
   - `data-document-id`
   - Other custom attributes

### Choosing Between Methods

**Use Text-Based Search when:**
- You have descriptive text near the PDF link
- The link structure is variable
- You're targeting user-facing text

**Use Attribute-Based Search when:**
- The page uses custom attributes to identify elements
- Multiple links exist and you need to be specific
- The structure is consistent but text might change

## Features

- **Dynamic Link Detection**: Automatically finds PDF links without hardcoding URLs
- **Flexible Search**: Supports both text-based and attribute-based searching
- **Robust Parsing**: Handles various HTML structures and element types
- **Source Tracking**: Records which page the PDF came from
- **Error Messages**: Detailed error information for debugging
- **Custom Headers**: Supports custom HTTP headers (User-Agent, etc.)

## Next Steps

After downloading a PDF, you can:
1. Process it using the `/api/pdf-documents/{id}/process/` endpoint
2. Extract tables and text from it
3. Access extracted data via `/api/pdf-documents/{id}/extracted_data/`

## Custom Headers

Both methods support custom HTTP headers:

```python
scraper = WebPDFScraper(
    page_url="https://example.com/page",
    search_text="PDF",
    headers={
        'User-Agent': 'Custom User Agent',
        'Accept-Language': 'hr-HR',
        'Authorization': 'Bearer token'
    }
)
```
