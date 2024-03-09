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
    legal_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CategoryTypes.choices)
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    @property
    def rating_summary(self):
        reviews = self.reviews
        result = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            "total": self.reviews.count(),  # TODO: change key to "count"
            "media": None,
        }
        total = 0
        for review in reviews.iterator():
            total += review.rating
            result[review.rating] += 1
        if self.reviews.count():
            result["media"] = total/self.reviews.count()
        return result

    def __str__(self):
        return self.name


class Review(BaseModel):
    # company_name = models.CharField(max_length=100, null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    salary_range = models.IntegerField()
    salary_currency = models.CharField(max_length=50)
    comment = models.CharField(max_length=1000)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="reviews")
    worker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reviews")
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # def clean(self):
    #     if self.company_name and self.company:
    #         raise ValidationError("Company name AND Company not allowed")

    def __str__(self):
        return " - ".join([self.company.name, (self.worker.display_name or "Anonymous")])


class BusinessRegionTypes(models.TextChoices):
    AMER = "Americas"
    APAC = "Asia & Pacific"
    EMEA = "Europe Middle East/Africa"


class SubRegionTypes(models.TextChoices):
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
    CENTRAL_AMERICA = "Central America"
    CARIBBEAN = "Caribbean"
    CENTRAL_SOUTH_ASIA = "Central & South Asia"
    NORTHEASTERN_ASIA = "Northeastern Asia"
    SOUTHEASTERN_ASIA = "Southeastern Asia"
    AUSTRALIA_OCEANIA = "Australia and Oceania"
    NORTHERN_EUROPE = "Northern Europe"
    SOUTHERN_EUROPE = "Southern Europe"
    EASTERN_EUROPE = "Eastern Europe"
    WESTERN_EUROPE = "Western Europe"
    MIDDLE_EAST = "Middle East"
    NORTHERN_AFRICA = "Northern Africa"
    SOUTHERN_AFRICA = "Southern Africa"


class LocationTypes(models.TextChoices):
    BILLING = "Billing"
    BUSINESS = "Business"
    CONTACT = "Contact"
    HOME = "Home"
    SHIPPING = "Shipping"


class Country(BaseModel):
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    subregion = models.CharField(max_length=50, choices=SubRegionTypes.choices)
    business_region = models.CharField(max_length=50, choices=BusinessRegionTypes.choices)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return f"{self.name} ({self.country_code})"


class Location(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    location_type = models.CharField(max_length=100, choices=LocationTypes.choices, default=LocationTypes.BUSINESS)
    street = models.CharField(max_length=100, null=True, blank=True)
    number = models.CharField(max_length=100, null=True, blank=True)
    floor = models.CharField(max_length=100, null=True, blank=True)
    apartment = models.CharField(max_length=100, null=True, blank=True)
    building = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    admin_level_1 = models.CharField(max_length=100, null=True, blank=True)
    admin_level_2 = models.CharField(max_length=100, null=True, blank=True)
    admin_level_3 = models.CharField(max_length=100, null=True, blank=True)
    admin_level_4 = models.CharField(max_length=100, null=True, blank=True)
    admin_level_5 = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="locations")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="locations")

    def __str__(self):
        return " - ".join([self.company.name, self.name])
