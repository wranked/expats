from random import random

from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

from common.models import BaseModel

from .constants import (
    CategoryTypes,
    SalaryCurrencyTypes,
    SalaryFrequencyTypes,
    HiringType,
    JobPlace,
    JobHours,
    JobDuration,
)


class Company(BaseModel):

    name_validator = UnicodeUsernameValidator()

    display_name = models.CharField(max_length=100, null=True, blank=True)
    id_name = models.CharField(max_length=100, unique=True, validators=[name_validator], null=True, blank=True)
    legal_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CategoryTypes.choices)
    picture = models.URLField(blank=True)
    admin = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, null=True, blank=True)
    locations = models.ManyToManyField("locations.Location", blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    def save(self, *args, **kwargs):
        if not self.id_name:
            self.id_name = slugify(self.display_name + str(int(random()*10**12)))
        super(Company, self).save(*args, **kwargs)

    @property
    def rating_summary(self):
        reviews = self.reviews
        result = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            "count": self.reviews.count(),
            "media": None,
        }
        total = 0
        for review in reviews.all():
            total += review.rating
            result[review.rating] += 1
        if self.reviews.count():
            result["media"] = total/self.reviews.count()
        return result

    def __str__(self):
        return self.display_name


class Review(BaseModel):
    # company_name = models.CharField(max_length=100, null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    salary_range = models.IntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=50, choices=SalaryCurrencyTypes.choices, default=SalaryCurrencyTypes.USD)
    salary_frequency = models.CharField(max_length=50, choices=SalaryFrequencyTypes.choices, default=SalaryFrequencyTypes.MONTHLY)
    comment = models.CharField(max_length=1000)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=True)
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


class Job(BaseModel):
    """

    """
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    expires_on = models.DateTimeField(null=True, blank=True)
    hiring_type = models.CharField(max_length=100, choices=HiringType.choices, default=HiringType.EMPLOYEE)
    hours = models.CharField(max_length=100, choices=JobHours.choices, default=JobHours.FULL_TIME)
    duration = models.CharField(max_length=100, choices=JobDuration.choices, default=JobDuration.SEASONAL)
    place = models.CharField(max_length=100, choices=JobPlace.choices, default=JobPlace.ON_SITE)
    has_sponsorship = models.BooleanField(default=False)
    has_accommodation = models.BooleanField(default=False)
    has_meal = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    location = models.ForeignKey("locations.Location", on_delete=models.CASCADE, related_name="jobs", null=True, blank=True)
    admin = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.location and self.company.locations.first():
            self.location = self.company.locations.first()
        super(Job, self).save(*args, **kwargs)

    def __str__(self):
        return " - ".join([self.company.display_name, self.title])
