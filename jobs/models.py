from django.db import models

from common.models import BaseModel
from companies.models import Company
from jobs.constants import (
    HiringType,
    JobHours,
    JobDuration,
    JobPlace,
)

class Job(BaseModel):
    """

    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    expires_on = models.DateTimeField(null=True, blank=True)
    hiring_type = models.CharField(max_length=100, choices=HiringType.choices, default=HiringType.EMPLOYEE)
    hours = models.CharField(max_length=100, choices=JobHours.choices, default=JobHours.FULL_TIME)
    duration = models.CharField(max_length=100, choices=JobDuration.choices, default=JobDuration.SEASONAL)
    place = models.CharField(max_length=100, choices=JobPlace.choices, default=JobPlace.ON_SITE)
    has_sponsorship = models.BooleanField(default=False)
    has_accommodation = models.BooleanField(default=False)
    has_meal = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    location = models.ForeignKey("locations.Location", on_delete=models.CASCADE, related_name="jobs", null=True, blank=True)
    # admin = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.location and self.company.locations.first():
            self.location = self.company.locations.first()
        super(Job, self).save(*args, **kwargs)

    def __str__(self):
        return " - ".join([self.company.display_name, self.title])
