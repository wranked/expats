import pytest

from .constants import CategoryTypes
from .models import Branch, Company
from apps.reviews.models import Review
from apps.users.models import CustomUser
from apps.locations.constants import BusinessRegionTypes, RegionTypes, SubRegionTypes
from apps.locations.models import Country, Location
from django.core.exceptions import ValidationError


@pytest.fixture
def dummy_user():
    CustomUser.objects.create_user("user@test.com", "password")
    return CustomUser.objects.get(email="user@test.com")


@pytest.fixture
def dummy_user2():
    CustomUser.objects.create_user("user2@test.com", "password")
    return CustomUser.objects.get(email="user2@test.com")


@pytest.fixture
def dummy_company():
    Company.objects.create(
        display_name="Dummy Company",
        id_name="dummy_company",
        category=CategoryTypes.OTHER,
    )
    return Company.objects.get(id_name="dummy_company")


@pytest.mark.django_db
def test_create_review(dummy_company, dummy_user):
    Review.objects.create(
        rating=5,
        salary_range=0,
        salary_currency="",
        salary_frequency="",
        comment="",
        is_public=False,
        company=dummy_company,
        reviewer=dummy_user,
    )
    assert dummy_company.rating_summary == {1: 0, 2: 0, 3: 0, 4: 0, 5: 1}


@pytest.mark.django_db
def test_create_2_reviews(dummy_company, dummy_user, dummy_user2):
    Review.objects.create(
        rating=5,
        salary_range=0,
        salary_currency="",
        salary_frequency="",
        comment="",
        is_public=False,
        company=dummy_company,
        reviewer=dummy_user,
    )
    assert dummy_company.rating_summary == {1: 0, 2: 0, 3: 0, 4: 0, 5: 1}

    Review.objects.create(
        rating=2,
        salary_range=0,
        salary_currency="",
        salary_frequency="",
        comment="",
        is_public=False,
        company=dummy_company,
        reviewer=dummy_user2,
    )
    assert dummy_company.rating_summary == {1: 0, 2: 1, 3: 0, 4: 0, 5: 1}


@pytest.mark.django_db
def test_update_rating(dummy_company, dummy_user, dummy_user2):
    Review.objects.create(
        rating=5,
        salary_range=0,
        salary_currency="",
        salary_frequency="",
        comment="",
        is_public=False,
        company=dummy_company,
        reviewer=dummy_user,
    )
    Review.objects.create(
        rating=3,
        salary_range=0,
        salary_currency="",
        salary_frequency="",
        comment="",
        is_public=False,
        company=dummy_company,
        reviewer=dummy_user2,
    )

    dummy_company.update_rating()
    assert dummy_company.reviews_count == 2
    assert dummy_company.reviews_rating == 4


@pytest.mark.django_db
def test_branch_primary_constraint():
    company = Company.objects.create(
        display_name="Primary Co",
        id_name="primary-co",
        category=CategoryTypes.OTHER,
    )
    country = Country.objects.create(
        name="Spain",
        country_code="ES",
        region=RegionTypes.EUROPE,
        subregion=SubRegionTypes.SOUTHERN_EUROPE,
        business_region=BusinessRegionTypes.EMEA,
    )
    location = Location.objects.create(
        name="Madrid",
        country=country,
    )

    Branch.objects.create(
        company=company,
        location=location,
        name="HQ",
        is_primary=True,
    )

    with pytest.raises(ValidationError):
        Branch.objects.create(
            company=company,
            location=location,
            name="Secondary",
            is_primary=True,
        )
