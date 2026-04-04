from django.contrib import admin

from .models import Company, Branch, CompanyAdmin


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0
    fields = ["name", "location", "address", "is_primary"]
    # raw_id_fields = ["location", "address"]


@admin.register(Company)
class CompanyModelAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'legal_name', 'legal_id', 'blacklisted_at', 'last_blacklisted_at']  # , 'reviews_rating', 'reviews_count', 'blacklisted_at']
    # list_filter = ['category', 'blacklisted_at']
    search_fields = ['display_name', 'legal_name', 'legal_id', 'id_name', 'description']
    readonly_fields = ['reviews_rating', 'reviews_count', 'id_name', 'blacklisted_at', 'last_blacklisted_at']
    filter_horizontal = ['related_companies']
    inlines = [BranchInline]


admin.site.register(Branch)
admin.site.register(CompanyAdmin)
