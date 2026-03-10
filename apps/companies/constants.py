from django.db import models


class CategoryTypes(models.TextChoices):
    AGENCY = "Agency"
    EMPLOYMENT_AGENCY = "Employment Agency"
    TOURISM_AGENCY = "Tourism Agency"
    ACCOMMODATION = "Accommodation"
    GASTRONOMY = "Gastronomy"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"
