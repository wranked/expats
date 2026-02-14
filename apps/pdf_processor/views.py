from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import PDFDocument, ExtractedData
from .serializers import (
    PDFDocumentSerializer,
    PDFDocumentListSerializer,
    ExtractedDataSerializer
)


class PDFDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing PDF documents."""
    queryset = PDFDocument.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return PDFDocumentListSerializer
        return PDFDocumentSerializer


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
