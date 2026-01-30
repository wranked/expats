import django_filters
from django.db.models import Q

from .models import Company

class CompanyFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(field_name="branches__location__country__country_code", lookup_expr="icontains")
    location = django_filters.CharFilter(method="filter_by_location")


    class Meta:
        model = Company
        fields = [
            "country",
            "location",
            ]

    def filter_by_location(self, queryset, name, value):
        """
        Custom filter to search by location. It filters by name and any parent location recursively.
        """
        return queryset.filter(
            Q(branches__location__name__icontains=value) |
            Q(branches__location__parent__name__icontains=value) |
            Q(branches__location__parent__parent__name__icontains=value) |
            Q(branches__location__parent__parent__parent__name__icontains=value) |
            Q(branches__location__parent__parent__parent__parent__name__icontains=value) |
            Q(branches__location__parent__parent__parent__parent__parent__name__icontains=value)
        )

    def filter_queryset(self, queryset):
        """
        Override filter_queryset to ensure distinct results when filtering by country.
        """
        queryset = super().filter_queryset(queryset)
        return queryset.distinct()