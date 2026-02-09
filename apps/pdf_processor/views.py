from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import PDFDocument, ExtractedData
from .constants import PDFStatus
from .serializers import (
    PDFDocumentSerializer,
    PDFDocumentListSerializer,
    ExtractedDataSerializer
)
from .services import PDFProcessor, WebPDFScraper, CroatianLaborPDFParser


class PDFDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing PDF documents."""
    queryset = PDFDocument.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return PDFDocumentListSerializer
        return PDFDocumentSerializer

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a PDF document to extract text and tables."""
        pdf_document = self.get_object()

        if pdf_document.status == 'processing':
            return Response(
                {'error': 'Document is already being processed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            processor = PDFProcessor(pdf_document)
            processor.process()
            serializer = self.get_serializer(pdf_document)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def extracted_data(self, request, pk=None):
        """Get all extracted data for a PDF document."""
        pdf_document = self.get_object()
        extracted_data = pdf_document.extracted_data.all()
        serializer = ExtractedDataSerializer(extracted_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def download_from_url(self, request):
        """
        Download a PDF from a web page by scraping and finding the download link.
        
        Supports two methods:
        1. Text-based search: Find PDF link near specified text
        2. Attribute-based search: Find PDF link by custom HTML attribute
        
        Text-based Request body parameters:
        - page_url (required): URL of the page to scrape
        - search_text (required): Text to search for to locate the PDF link
        
        Attribute-based Request body parameters:
        - page_url (required): URL of the page to scrape
        - attribute_name (required): HTML attribute name (e.g., 'data-fileid')
        - attribute_value (optional): HTML attribute value
        
        Returns:
            PDFDocument: The created document with the downloaded PDF
        """
        page_url = request.data.get('page_url')
        search_text = request.data.get('search_text')
        attribute_name = request.data.get('attribute_name')
        attribute_value = request.data.get('attribute_value')
        
        # Validate required parameters
        if not page_url:
            return Response(
                {'error': 'page_url is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check that either search_text or attribute_name is provided
        if not search_text and not attribute_name:
            return Response(
                {'error': 'Either search_text or attribute_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create scraper with provided parameters
            scraper = WebPDFScraper(
                page_url=page_url,
                search_text=search_text,
                attribute_name=attribute_name,
                attribute_value=attribute_value
            )
            
            # Download PDF and create document
            pdf_document = scraper.download_and_create_document()
            
            serializer = self.get_serializer(pdf_document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to download PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def parse_croatian_labor(self, request, pk=None):
        """
        Parse a Croatian Ministry of Labor PDF to extract structured company data.
        
        The PDF should contain a table with 4 columns:
        - R.BR. (Correlative index)
        - NAZIV POSLODAVCA (Company legal name)
        - OIB (Company ID)
        - ADRESA (Address)
        
        Returns:
            Structured company data extracted from the table
        """
        pdf_document = self.get_object()

        if pdf_document.status == 'processing':
            return Response(
                {'error': 'Document is already being processed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Use specialized parser
            parser = CroatianLaborPDFParser(pdf_document)
            extracted_data = parser.process_and_save()
            
            # Update document status
            pdf_document.status = PDFStatus.COMPLETED
            pdf_document.save()
            
            return Response({
                'id': extracted_data.id,
                'data_type': extracted_data.data_type,
                'companies': extracted_data.raw_data.get('companies', []),
                'total_count': extracted_data.raw_data.get('total_count', 0),
                'created_at': extracted_data.created_at,
            })
        except Exception as e:
            pdf_document.status = PDFStatus.FAILED
            pdf_document.error_message = str(e)
            pdf_document.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def companies(self, request, pk=None):
        """
        Get structured company data from a processed Croatian labor PDF.
        
        Returns:
            List of companies if the document has been parsed, otherwise empty response
        """
        pdf_document = self.get_object()
        
        # Look for structured companies data
        company_data = pdf_document.extracted_data.filter(
            data_type='structured_companies'
        ).first()
        
        if not company_data:
            return Response({
                'companies': [],
                'total_count': 0,
                'message': 'No structured company data found. Use parse_croatian_labor endpoint first.'
            })
        
        return Response({
            'companies': company_data.raw_data.get('companies', []),
            'total_count': company_data.raw_data.get('total_count', 0),
            'parsed_at': company_data.created_at,
        })

    @action(detail=True, methods=['get'])
    def parse_debug(self, request, pk=None):
        """
        Debug endpoint to see why rows are being filtered during parsing.
        
        Returns:
            Detailed breakdown of filtering statistics
        """
        pdf_document = self.get_object()

        try:
            parser = CroatianLaborPDFParser(pdf_document)
            debug_info = parser.parse_companies_table_with_debug()
            
            return Response(debug_info)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExtractedDataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing extracted data."""
    queryset = ExtractedData.objects.all()
    serializer_class = ExtractedDataSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        pdf_document_id = self.request.query_params.get('pdf_document')
        data_type = self.request.query_params.get('data_type')

        if pdf_document_id:
            queryset = queryset.filter(pdf_document_id=pdf_document_id)
        if data_type:
            queryset = queryset.filter(data_type=data_type)

        return queryset
