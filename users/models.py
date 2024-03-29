from django.contrib.auth.models import AbstractUser
from django.db import models, IntegrityError
from django.utils.text import slugify
from random import random


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True, blank=True)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    picture = models.URLField(blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        self.display_name = " ".join([self.first_name, self.last_name])
        if not self.username:
            self.username = slugify(self.display_name + str(int(random()*10**12)))
        super(CustomUser, self).save(*args, **kwargs)

