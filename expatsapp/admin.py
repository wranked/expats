from django.contrib import admin

from .models import User, Company, Review


admin.site.register(User)
admin.site.register(Company)
admin.site.register(Review)
