from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from apps.common.models import BaseModel
from apps.companies.models import Company
from .constants import SalaryCurrencyTypes, SalaryFrequencyTypes


class Review(BaseModel):
    # company_name = models.CharField(max_length=100, null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    salary_range = models.IntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=50, choices=SalaryCurrencyTypes.choices, default=SalaryCurrencyTypes.USD)
    salary_frequency = models.CharField(max_length=50, choices=SalaryFrequencyTypes.choices, default=SalaryFrequencyTypes.MONTHLY)
    comment = models.TextField()
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="reviews")

    # def clean(self):
    #     if self.company_name and self.company:
    #         raise ValidationError("Company name AND Company not allowed")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['company', 'reviewer'], name="unique_reviewer_per_company"),
        ]

    def __str__(self):
        return " - ".join([self.company.display_name, (self.reviewer.display_name or "Anonymous")])



