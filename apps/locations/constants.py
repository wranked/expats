from django.db import models


class BusinessRegionTypes(models.TextChoices):
    AMER = "Americas"
    APAC = "Asia & Pacific"
    EMEA = "Europe Middle East/Africa"


class RegionTypes(models.TextChoices):
    AFRICA = "Africa"
    AMERICAS = "Americas"
    ASIA = "Asia"
    EUROPE = "Europe"
    OCEANIA = "Oceania"


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


class AreaTypes(models.TextChoices):
    """ Area Types for economic and political regions """
    EUROPEAN_UNION = "European Union"
    SCHENGEN = "Schengen Area"
    LATIN_AMERICA = "Latin America"


class AddressTypes(models.TextChoices):
    BILLING = "Billing"
    BUSINESS = "Business"
    CONTACT = "Contact"
    HOME = "Home"
    SHIPPING = "Shipping"


class LocationNameTypes(models.TextChoices):
    CITY = "CITY"
    COUNTY = "COUNTY"
    DEPARTMENT = "DEPARTMENT"
    DISTRICT = "DISTRICT"
    MUNICIPALITY = "MUNICIPALITY"
    PROVINCE = "PROVINCE"
    REGION = "REGION"
    STATE = "STATE"
    TOWN = "TOWN"
    VILLAGE = "VILLAGE"
