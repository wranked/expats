from django.contrib import admin

from django.db import models
from django.forms import Textarea

from .models import Job

class JobAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": Textarea(
            attrs={"rows": 20,
                   "cols": 80,
                   })},
    }

admin.site.register(Job, JobAdmin)
