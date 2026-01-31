import uuid

from django.core.exceptions import ValidationError
from django.db import models
import requests
from geopy.geocoders import Nominatim

from apps.common.models import BaseModel

from .constants import AddressTypes, BusinessRegionTypes, LocationNameTypes, SubRegionTypes, RegionTypes


class Country(BaseModel):
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    region = models.CharField(max_length=50, choices=RegionTypes.choices, null=True, blank=True)
    subregion = models.CharField(max_length=50, choices=SubRegionTypes.choices)
    business_region = models.CharField(max_length=50, choices=BusinessRegionTypes.choices)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return f"{self.name} ({self.country_code})"


# class Location(BaseModel):
#     """Location model to store the location of a company or user"""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100, null=True, blank=True)
#     country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="locations")
#     location_type = models.CharField(max_length=100, choices=LocationNameTypes.choices, default=LocationNameTypes.CITY)

    # postal_code = models.CharField(max_length=100, null=True, blank=True)
    # admin_level_1 = models.CharField(max_length=100, null=True, blank=True)
    # admin_level_2 = models.CharField(max_length=100, null=True, blank=True)
    # admin_level_3 = models.CharField(max_length=100, null=True, blank=True)
    # admin_level_4 = models.CharField(max_length=100, null=True, blank=True)
    # admin_level_5 = models.CharField(max_length=100, null=True, blank=True)

    # def __str__(self):
    #     return ", ".join(filter(None, [
    #         self.admin_level_5,
    #         self.admin_level_4,
    #         self.admin_level_3,
    #         self.admin_level_2,
    #         self.admin_level_1,
    #         self.country.name
    #     ]))

class Location(BaseModel):
    """ Location model to store the location of a company or user """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    level_type = models.CharField(max_length=50, choices=LocationNameTypes.choices, default=LocationNameTypes.CITY)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="locations")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subdivisions"
    )

    def __str__(self):
        parts = [self.name] if self.name else []
        parent = self.parent
        while parent:
            parts.append(parent.name)
            parent = parent.parent
        parts.append(self.country.name)
        return ", ".join(filter(None, parts))

class Address(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    address_type = models.CharField(max_length=100, choices=AddressTypes.choices, default=AddressTypes.BUSINESS)
    street = models.CharField(max_length=100, null=True, blank=True)
    number = models.CharField(max_length=100, null=True, blank=True)
    floor = models.CharField(max_length=100, null=True, blank=True)
    apartment = models.CharField(max_length=100, null=True, blank=True)
    building = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, editable=False)
    longitude = models.FloatField(null=True, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    # user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, null=True, blank=True, related_name="addresses")
    # branch = models.OneToOneField("companies.Branch", on_delete=models.CASCADE, null=True, blank=True, related_name="address")

    class Meta:
        verbose_name_plural = "Addresses"

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            self.latitude, self.longitude = self.get_coordinates()
        # if self.user and self.branch:
        #     raise ValidationError("Only one relation can exist")
        # elif not self.user and not self.branch:
        #     raise ValidationError("One relation must exist")
        # else:
        super().save(*args, **kwargs)
    
    def get_coordinates(self):
        """Get coordinates from  GeoPy"""

        geolocator = Nominatim(user_agent="myGeocoder")
        location = geolocator.geocode(f"{self.street} {self.number}, {self.postal_code}, {self.location}")
        if location:
            return location.latitude, location.longitude
        return None, None

        # GOOGLE_MAPS_API_KEY = "AIzaSyDmm12sorDfX8xsYOei0qUDY-Ld86jIZGE"  # settings.GOOGLE_MAPS_API_KEY
        # address = f"{self.street} {self.number}, {self.postal_code}, {self.location}"
        # url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
        
        # response = requests.get(url)
        # data = response.json()
        
        # if data["status"] == "OK":
        #     location = data["results"][0]["geometry"]["location"]
        #     return location["lat"], location["lng"]
        # return None, None

    def __str__(self):
        # if self.user:
        #     return self.user.name
        return ", ".join([self.street + " " + self.number, self.postal_code, self.location.__str__()])
