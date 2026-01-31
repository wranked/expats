from django.db import models


class LanguageCodeTypes(models.TextChoices):
    """ Language codes based in ISO 639 standardized nomenclature """

    ENGLISH = "en"
    CROATIAN = "hr"
    GERMAN = "de"
    SPANISH = "es"
