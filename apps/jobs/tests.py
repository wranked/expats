import pytest

from apps.companies.constants import CategoryTypes
from apps.companies.models import Company
from apps.locations.constants import BusinessRegionTypes, RegionTypes, SubRegionTypes
from apps.locations.models import Country, Location

from .models import Job


@pytest.mark.django_db
def test_job_str():
	company = Company.objects.create(
		display_name="Acme Inc",
		id_name="acme-inc",
		category=CategoryTypes.OTHER,
	)
	country = Country.objects.create(
		name="Portugal",
		country_code="PT",
		region=RegionTypes.EUROPE,
		subregion=SubRegionTypes.SOUTHERN_EUROPE,
		business_region=BusinessRegionTypes.EMEA,
	)
	location = Location.objects.create(
		name="Lisbon",
		country=country,
	)
	job = Job.objects.create(
		title="Backend Developer",
		description="Django developer role",
		company=company,
		location=location,
	)

	assert str(job) == "Acme Inc - Backend Developer"
