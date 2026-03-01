from django.db import models


class CategoryTypes(models.TextChoices):
    AGENCY = "Agency"
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
    REGULAR = "Regular"         # Standard permanent employment with ongoing responsibilities
    CONTRACT = "Contract"       # Fixed-term or project-based employment
    FREELANCE = "Freelance"     # Self-employed
    INTERNSHIP = "Internship"   # Temporary position for students or recent graduates
    VOLUNTEER = "Volunteer"     # Unpaid position, often for non-profits or community organizations
    OTHER = "Other"


class JobHours(models.TextChoices):
    FULL_TIME = "Full-time"     # > 30 h/week
    PART_TIME = "Part-time"     # < 30 h/week
    FLEXIBLE = "Flexible"       # Variable hours
    OTHER = "Other"

class JobDuration(models.TextChoices):
    CASUAL = "Casual"           # 1 event or a couple of days
    SEASONAL = "Seasonal"       # 3 to 6 months
    LONG_TERM = "Long-term"     # More than 1 year
    OTHER = "Other"


class JobPlace(models.TextChoices):
    ON_SITE = "On-site"       # Work is performed at the employer's location, requiring physical presence.
    HYBRID = "Hybrid"         # Combination of on-site and remote work.
    REMOTE = "Remote"         # Work is performed entirely from a remote location.
