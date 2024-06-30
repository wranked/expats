from django.db import models

from common.constants import LanguageCodeTypes
from common.models import BaseModel


class CategoryType(models.Choices):
    BLOG = "Blog"
    UTILS = "Utils"


class Post(BaseModel):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    # categories = models.CharField(CategoryType)
    content = models.TextField()
    # author = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    language_code = models.CharField(max_length=10, choices=LanguageCodeTypes.choices, default=LanguageCodeTypes.ENGLISH)
    # country = models.ForeignKey("locations.Country", on_delete=models.CASCADE, blank=True, null=True)
    # tags

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'language_code'], name="unique_post_by_language"),
        ]

    @property
    def name_lang(self):
        return "-".join([self.name, self.language_code])

    def __str__(self):
        return " - ".join([self.name, self.language_code, self.title])
