from random import random

from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone

from apps.common.models import BaseModel

from .constants import CategoryTypes, CreatedViaTypes
from .utils import clean_display_name


User = get_user_model()


class Company(BaseModel):

    name_validator = UnicodeUsernameValidator()

    display_name = models.CharField(max_length=255, null=True, blank=True)
    id_name = models.CharField(max_length=255, unique=True, validators=[name_validator], null=True, blank=True)
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    legal_id = models.CharField(max_length=50, null=True, blank=True, help_text="Legal identification number")
    legal_id_type = models.CharField(max_length=50, null=True, blank=True, help_text="Type of legal identification (e.g., OIB, EIN)")
    url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CategoryTypes.choices)  # TODO: Change to industry?
    avatar = CloudinaryField("avatar", null=True, blank=True)
    reviews_rating = models.FloatField(default=0, editable=False)
    reviews_count = models.IntegerField(default=0, editable=False)
    rating_summary = models.JSONField(default=dict, editable=False)
    blacklisted_at = models.DateTimeField(null=True, blank=True)
    last_blacklisted_at = models.DateTimeField(null=True, blank=True)
    is_certified = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    primary_location = models.CharField(max_length=255, null=True, blank=True, editable=False)
    raw_address = models.CharField(max_length=255, null=True, blank=True)
    country = models.ForeignKey("locations.Country", on_delete=models.SET_NULL, null=True, blank=True, related_name="companies")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_companies")
    created_via = models.CharField(max_length=20, choices=CreatedViaTypes.choices, default=CreatedViaTypes.API)
    related_companies = models.ManyToManyField("self", blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    def save(self, *args, **kwargs):
        # Clean the display_name by removing common suffixes and descriptors
        if self.display_name:
            self.display_name = clean_display_name(self.display_name)
        if not self.id_name:
            self.id_name = slugify(self.display_name + str(int(random()*10**12)))
        super().save(*args, **kwargs)

    def update_rating(self):
        reviews = self.reviews.filter(approved_at__isnull=False)
        total_reviews = reviews.count()
        summary = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
        }

        for review in reviews:
            summary[review.rating] += 1

        if total_reviews > 0:
            self.reviews_rating = sum(review.rating for review in reviews) / total_reviews
        else:
            self.reviews_rating = 0

        self.reviews_count = total_reviews
        self.rating_summary = summary

        self.save()

    def __str__(self):
        return self.display_name


class Branch(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="branches")
    address = models.OneToOneField("locations.Address", on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)

    @property
    def resolved_location(self):
        return self.address.location if self.address_id else None

    def clean(self):
        super().clean()

        if not self.address_id:
            raise ValidationError({"address": "Branch must have an address."})

        if self.is_primary and self.company_id:
            if Branch.objects.filter(company_id=self.company_id, is_primary=True).exclude(id=self.id).exists():
                raise ValidationError("This company already has a primary location.")

    def _sync_company_primary_location(self):
        primary_branch = Branch.objects.filter(
            company_id=self.company_id,
            is_primary=True,
        ).select_related("address__location").first()
        primary_location = primary_branch.resolved_location if primary_branch else None
        Company.objects.filter(id=self.company_id).update(
            primary_location=str(primary_location) if primary_location else None,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self._sync_company_primary_location()

    def delete(self, *args, **kwargs):
        company_id = self.company_id
        super().delete(*args, **kwargs)
        primary_branch = Branch.objects.filter(
            company_id=company_id,
            is_primary=True,
        ).select_related("address__location").first()
        primary_location = primary_branch.resolved_location if primary_branch else None
        Company.objects.filter(id=company_id).update(
            primary_location=str(primary_location) if primary_location else None,
        )

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return " - ".join([self.company.display_name, self.name or ""])


class CompanyAdmin(models.Model):
    SUPERADMIN = "superadmin"
    CONTENT_ADMIN = "content-admin"

    ROLE_CHOICES = [
        (SUPERADMIN, "Super Admin"),
        (CONTENT_ADMIN, "Content Admin"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="admins")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="company_roles")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ("company", "user")

    @classmethod
    def user_has_role(cls, user, company, role):
        return cls.objects.filter(user=user, company=company, role=role).exists()

    def __str__(self):
        return f"{self.user} - {self.company} ({self.role})"
