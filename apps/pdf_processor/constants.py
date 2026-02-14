from django.db import models


class PDFStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'


class DataType(models.TextChoices):
    STRUCTURED_COMPANIES = 'structured_companies', 'Structured Companies'
