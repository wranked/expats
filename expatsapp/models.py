from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import CustomUser


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


# class User(BaseModel):
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=256)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     username = models.CharField(max_length=100, null=True, blank=True)
#     birth_date = models.CharField(max_length=100, null=True, blank=True)
#     validated_at = models.DateTimeField(null=True, blank=True)
#
#     def __str__(self):
#         return self.email


class Company(BaseModel):
    name = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    category = models.CharField(max_length=50, choices=CategoryTypes.choices)
    location = models.CharField(max_length=100)
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    @property
    def rating_summary(self):
        reviews = Review.objects.all()
        count = len(reviews)
        total = 0

        result = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            "total": count,
            "media": 0,
        }

        for review in reviews.iterator():
            total += review.rating
            result[review.rating] += 1
        result["media"] = total/count

        return result


class Review(BaseModel):
    # company_name = models.CharField(max_length=100, null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    comment = models.CharField(max_length=1000)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="reviews")
    worker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="workers")
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # def clean(self):
    #     if self.company_name and self.company:
    #         raise ValidationError("Company name AND Company not allowed")

