from rest_framework import serializers
from .models import PDFDocument, ExtractedData


class ExtractedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedData
        fields = [
            'id',
            'data_type',
            'raw_data',
            'processed',
            'page_number',
            'created_at',
            'modified_at'
        ]
        read_only_fields = ['id', 'created_at', 'modified_at']


class PDFDocumentSerializer(serializers.ModelSerializer):
    extracted_data = ExtractedDataSerializer(many=True, read_only=True)

    class Meta:
        model = PDFDocument
        fields = [
            'id',
            'file',
            'original_filename',
            'status',
            'error_message',
            'extracted_data',
            'created_at',
            'modified_at'
        ]
        read_only_fields = ['id', 'status', 'error_message', 'created_at', 'modified_at']

    def create(self, validated_data):
        # Automatically set original filename from uploaded file
        if 'file' in validated_data:
            validated_data['original_filename'] = validated_data['file'].name
        return super().create(validated_data)


class PDFDocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    extracted_data_count = serializers.IntegerField(
        source='extracted_data.count',
        read_only=True
    )

    class Meta:
        model = PDFDocument
        fields = [
            'id',
            'original_filename',
            'status',
            'extracted_data_count',
            'created_at',
            'modified_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'modified_at']
