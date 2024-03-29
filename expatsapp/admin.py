from django.contrib import admin

from .models import Company, Job, Review


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


# admin.site.register(Company, ParentModelAdmin)
# admin.site.register(Address, ChildModelAdmin)
# admin.site.register(Address)
admin.site.register(Company)
admin.site.register(Review)
admin.site.register(Job)
