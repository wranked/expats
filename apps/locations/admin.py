from django.contrib import admin
from django.contrib.admin.filters import RelatedOnlyFieldListFilter

from .models import Address, Country, Location


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["street", "number", "postal_code", "location"]
    search_fields = ["street", "number", "postal_code", "location__name", "location__country__name"]


class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "postal_code", "country",  "level_type", "parent"]
    list_filter = [
        "level_type",
        ("country", RelatedOnlyFieldListFilter),
        ]
    search_fields = ["name", "country__name"]
    # autocomplete_fields = ["country"]


admin.site.register(Location, LocationAdmin)
admin.site.register(Country)
