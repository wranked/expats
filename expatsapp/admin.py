from django.contrib import admin

from .models import Company, Country, Location, Review


class ChildModelFormInline(admin.TabularInline):
    model = Location
    extra = 0


class ParentModelAdmin(admin.ModelAdmin):
    inlines = (ChildModelFormInline, )


class ChildModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(Company, ParentModelAdmin)
admin.site.register(Location, ChildModelAdmin)
admin.site.register(Country)
admin.site.register(Review)
