from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import Company, Branch, CompanyAdmin


# class ChildModelFormInline(admin.TabularInline):
#     model = Address
#     extra = 0
#
#
# class ParentModelAdmin(admin.ModelAdmin):
#     inlines = (ChildModelFormInline, )
#
#
# class ChildModelAdmin(admin.ModelAdmin):
#     pass


# class ReviewAdmin(admin.ModelAdmin):
#     formfield_overrides = {
#         models.TextField: {"widget": Textarea(attrs={"rows": 10, "cols": 80})},
#     }

# admin.site.register(Company, ParentModelAdmin)
# admin.site.register(Address, ChildModelAdmin)
# admin.site.register(Address)
admin.site.register(Company)
admin.site.register(Branch)
admin.site.register(CompanyAdmin)
# admin.site.register(Review)
# admin.site.register(Job, JobAdmin)
