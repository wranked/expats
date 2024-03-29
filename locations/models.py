import uuid

from django.core.exceptions import ValidationError
from django.db import models

from common.models import BaseModel

from .constants import AddressTypes, BusinessRegionTypes, LocationNameTypes, SubRegionTypes


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    admin_level_1 = models.CharField(max_length=100, null=True, blank=True)
    admin_level_2 = models.CharField(max_length=100, null=True, blank=True)
    admin_level_3 = models.CharField(max_length=100, null=True, blank=True)
    admin_level_4 = models.CharField(max_length=100, null=True, blank=True)
    admin_level_5 = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="locations")

    def __str__(self):
        return ", ".join(filter(None, [
            self.admin_level_5,
            self.admin_level_4,
            self.admin_level_3,
            self.admin_level_2,
            self.admin_level_1,
            self.country.name
        ]))


class Address(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    address_type = models.CharField(max_length=100, choices=AddressTypes.choices, default=AddressTypes.BUSINESS)
    street = models.CharField(max_length=100, null=True, blank=True)
    number = models.CharField(max_length=100, null=True, blank=True)
    floor = models.CharField(max_length=100, null=True, blank=True)
    apartment = models.CharField(max_length=100, null=True, blank=True)
    building = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, null=True, blank=True, related_name="addresses")
    company = models.ForeignKey("expatsapp.Company", on_delete=models.CASCADE, null=True, blank=True, related_name="addresses")

    class Meta:
        verbose_name_plural = "Addresses"

    def save(self, *args, **kwargs):
        if self.user and self.company:
            raise ValidationError("Only one relation can exist")
        elif not self.user and not self.company:
            raise ValidationError("One relation must exist")
        else:
            super(Address, self).save(*args, **kwargs)

    def __str__(self):
        return " - ".join([self.company.display_name, self.name])
