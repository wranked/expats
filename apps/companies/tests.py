import pytest

from .constants import CategoryTypes
from .models import Branch, Company
from .utils import clean_display_name
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


def test_clean_display_name_with_doo():
    """Test removal of d.o.o. (limited liability company) suffix."""
    result = clean_display_name("PRIMUM d.o.o. za usluge")
    assert result == "PRIMUM"


def test_clean_display_name_with_jdoo():
    """Test removal of j.d.o.o. (limited liability company) suffix."""
    result = clean_display_name("SB TRADE j.d.o.o. za prijevoz i usluge")
    assert result == "SB TRADE"


def test_clean_display_name_with_comma():
    """Test removal of content after comma."""
    result = clean_display_name("MORENO, obrt za trgovinu i ugostiteljstvo, vl. Miroslav Bilić, Knin, Marulićev trg 5")
    assert result == "MORENO"


def test_clean_display_name_with_obrt():
    """Test removal of obrt (craft business) suffix."""
    result = clean_display_name("My Business obrt")
    assert result == "My Business"


def test_clean_display_name_with_za():
    """Test removal of za (for) preposition."""
    result = clean_display_name("Company Name za nesto")
    assert result == "Company Name"


def test_clean_display_name_no_separator():
    """Test that names without separators are returned unchanged."""
    result = clean_display_name("Simple Company Name")
    assert result == "Simple Company Name"


def test_clean_display_name_empty_string():
    """Test handling of empty string."""
    result = clean_display_name("")
    assert result == ""


def test_clean_display_name_none():
    """Test handling of None input."""
    result = clean_display_name(None)
    assert result is None


def test_clean_display_name_with_whitespace():
    """Test that leading/trailing whitespace is removed."""
    result = clean_display_name("  Company Name j.d.o.o.  ")
    assert result == "Company Name"


def test_clean_display_name_case_insensitive():
    """Test that separator matching is case-insensitive."""
    result = clean_display_name("Company Name D.O.O. something")
    assert result == "Company Name"
