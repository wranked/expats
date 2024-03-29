from django.contrib import admin

from .models import Address, Country, Location

admin.site.register(Location)
admin.site.register(Country)
