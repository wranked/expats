from random import random

from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from apps.common.models import BaseModel

from .constants import CategoryTypes
from .utils import clean_display_name


User = get_user_model()


class Company(BaseModel):

    name_validator = UnicodeUsernameValidator()

    display_name = models.CharField(max_length=255, null=True, blank=True)
    id_name = models.CharField(max_length=255, unique=True, validators=[name_validator], null=True, blank=True)
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    legal_id = models.CharField(max_length=50, null=True, blank=True, help_text="Legal identification number (e.g., Croatian OIB)")
    url = models.URLField(null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CategoryTypes.choices)  # TODO: Change to industry?
    # picture = models.URLField(blank=True)
    avatar = CloudinaryField("avatar", null=True, blank=True)
    # admin = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, null=True, blank=True)
    # locations = models.ManyToManyField("locations.Location", through="Branch", related_name="companies", blank=True)
    reviews_rating = models.FloatField(default=0, editable=False)
    reviews_count = models.IntegerField(default=0, editable=False)

    class Meta:
        verbose_name_plural = "Companies"

    def save(self, *args, **kwargs):
        # Clean the display_name by removing common suffixes and descriptors
        if self.display_name:
            self.display_name = clean_display_name(self.display_name)
        if not self.id_name:
            self.id_name = slugify(self.display_name + str(int(random()*10**12)))
        super(Company, self).save(*args, **kwargs)

    def update_rating(self):
        reviews = self.reviews.all()
        total_reviews = reviews.count()

        if total_reviews > 0:
            self.reviews_rating = sum(review.rating for review in reviews) / total_reviews
            self.reviews_count = total_reviews
        else:
            self.reviews_rating = 0
            self.reviews_count = 0

        self.save()

    @property
    def rating_summary(self):
        reviews = self.reviews
        result = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            # "count": self.reviews.count(),
            # "media": None,
        }
        # total = 0
        for review in reviews.all():
            # total += review.rating
            result[review.rating] += 1
        # if self.reviews.count():
        #     result["media"] = total/self.reviews.count()
        return result

    def __str__(self):
        return self.display_name


class Branch(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="branches")
    location = models.ForeignKey("locations.Location", on_delete=models.CASCADE, related_name="branches")
    address = models.OneToOneField("locations.Address", on_delete=models.CASCADE, null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    # class Meta:
    #     unique_together = ("company", "location")  

    def save(self, *args, **kwargs):
        """ Ensure just one primary location by company."""
        if self.is_primary:
            if Branch.objects.filter(company=self.company, is_primary=True).exclude(id=self.id).exists():
                raise ValidationError("This company already has a primary location.")
        super().save(*args, **kwargs)

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
