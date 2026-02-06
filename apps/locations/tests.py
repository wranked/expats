import pytest

from .constants import BusinessRegionTypes, RegionTypes, SubRegionTypes
from .models import Country, Location


@pytest.mark.django_db
def test_location_str_with_parent():
	country = Country.objects.create(
		name="Germany",
		country_code="DE",
		region=RegionTypes.EUROPE,
		subregion=SubRegionTypes.WESTERN_EUROPE,
		business_region=BusinessRegionTypes.EMEA,
	)
	parent = Location.objects.create(
		name="Bavaria",
		country=country,
	)
	child = Location.objects.create(
		name="Munich",
		country=country,
		parent=parent,
	)

	assert str(child) == "Munich, Bavaria, Germany"
