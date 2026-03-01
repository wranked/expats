from django.db import models


class CategoryTypes(models.TextChoices):
    ACCOMMODATION = "Accommodation"
    GASTRONOMY = "Gastronomy"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"


class SalaryFrequencyTypes(models.TextChoices):
    HOURLY = "Hourly"
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    ANNUALLY = "Annually"


class SalaryCurrencyTypes(models.TextChoices):
    USD = "USD"
    EUR = "EUR"


class HiringType(models.TextChoices):
    FREELANCE = "Freelance"  # Self-employed
    CONTRACT = "Contract"
    EMPLOYEE = "Employee"  # Change to Formal
    INTERNSHIP = "Internship"
    VOLUNTEER = "Volunteer"
    OTHER = "Other"


class JobHours(models.TextChoices):
    FULL_TIME = "Full-time"  # > 30 h/week
    PART_TIME = "Part-time"  # < 30 h/week
    FLEXIBLE = "Flexible"  # Variable hours
    OTHER = "Other"

class JobDuration(models.TextChoices):
    CASUAL = "Casual"  # 1 event or a couple of days
    SEASONAL = "Seasonal"  # 3 to 6 months
    LONG_TERM = "Long-term"  # More than 1 year
    OTHER = "Other"


class JobPlace(models.TextChoices):
    ON_SITE = "On-site"
    HYBRID = "Hybrid"
    REMOTE = "Remote"
