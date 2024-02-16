from django.core.exceptions import ValidationError
from django.db import models


class BaseModel(models.Model):
    """Base Class from which all classes must inherit."""

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, editable=False)

    class Meta:
        abstract = True


class CategoryTypes(models.TextChoices):
    ACCOMMODATION = "Accommodation"
    GASTRONOMY = "Gastronomy"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"


class User(BaseModel):
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=256)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.CharField(max_length=100, null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)


class Company(BaseModel):
    name = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    category = models.CharField(max_length=50, choices=CategoryTypes.choices)
    location = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    @property
    def ratings(self):
        return {
            1: 1,
            2: None,
            3: None,
            4: None,
            5: 9,
            "total": 10,
            "media": 4.6,
        }


class Review(BaseModel):
    # company_name = models.CharField(max_length=100, null=True, blank=True)
    rating = models.FloatField()
    comment = models.CharField(max_length=1000)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # def clean(self):
    #     if self.company_name and self.company:
    #         raise ValidationError("Company name AND Company not allowed")

