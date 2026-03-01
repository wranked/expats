from django.db import models


class CategoryTypes(models.TextChoices):
    AGENCY = "Agency"
    ACCOMMODATION = "Accommodation"
    GASTRONOMY = "Gastronomy"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"
