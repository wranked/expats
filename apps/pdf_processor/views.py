from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import PDFDocument, ExtractedData
from .serializers import (
    PDFDocumentSerializer,
    PDFDocumentListSerializer,
    ExtractedDataSerializer
)
from .services import PDFProcessor


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
