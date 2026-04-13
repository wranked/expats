import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from .constants import CategoryTypes
from .models import Branch, Company, CompanyAdmin
from .utils import clean_display_name
from apps.reviews.models import Review
from apps.users.models import CustomUser
from apps.locations.constants import BusinessRegionTypes, RegionTypes, SubRegionTypes
from apps.locations.models import Address, Country, Location
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
def api_client():
    return APIClient()


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
    country, _ = Country.objects.get_or_create(
        country_code="ES",
        defaults={
            "name": "Spain",
            "region": RegionTypes.EUROPE,
            "subregion": SubRegionTypes.SOUTHERN_EUROPE,
            "business_region": BusinessRegionTypes.EMEA,
        },
    )
    location, _ = Location.objects.get_or_create(
        name="Madrid",
        country=country,
    )
    primary_address = Address.objects.create(
        street="Gran Via",
        number="1",
        postal_code="28013",
        location=location,
        latitude=40.4168,
        longitude=-3.7038,
    )
    secondary_address = Address.objects.create(
        street="Alcala",
        number="2",
        postal_code="28014",
        location=location,
        latitude=40.4170,
        longitude=-3.7030,
    )

    Branch.objects.create(
        company=company,
        address=primary_address,
        name="HQ",
        is_primary=True,
    )

    with pytest.raises(ValidationError):
        Branch.objects.create(
            company=company,
            address=secondary_address,
            name="Secondary",
            is_primary=True,
        )


@pytest.mark.django_db
def test_branch_requires_address():
    company = Company.objects.create(
        display_name="Constraint Co",
        id_name="constraint-co",
        category=CategoryTypes.OTHER,
    )

    with pytest.raises(ValidationError, match="address"):
        Branch.objects.create(
            company=company,
            name="Missing place",
        )


@pytest.mark.django_db
def test_branch_allows_address():
    company = Company.objects.create(
        display_name="Address Only Co",
        id_name="address-only-co",
        category=CategoryTypes.OTHER,
    )
    country, _ = Country.objects.get_or_create(
        country_code="DE",
        defaults={
            "name": "Germany",
            "region": RegionTypes.EUROPE,
            "subregion": SubRegionTypes.WESTERN_EUROPE,
            "business_region": BusinessRegionTypes.EMEA,
        },
    )
    berlin, _ = Location.objects.get_or_create(name="Berlin", country=country)
    address = Address.objects.create(
        street="Unter den Linden",
        number="10",
        postal_code="10117",
        location=berlin,
        latitude=52.5200,
        longitude=13.4050,
    )

    branch = Branch.objects.create(
        company=company,
        address=address,
        name="Address only",
    )

    assert branch.address == address
    assert branch.resolved_location == berlin


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


@pytest.mark.django_db
def test_create_company_sets_created_by(api_client, dummy_user):
    api_client.force_authenticate(user=dummy_user)

    response = api_client.post(
        reverse("company-list"),
        {
            "display_name": "Created By User",
            "category": CategoryTypes.OTHER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    company = Company.objects.get(id=response.data["id"])
    assert company.created_by == dummy_user
    assert company.created_via == "API"


@pytest.mark.django_db
def test_create_company_requires_authentication(api_client):
    response = api_client.post(
        reverse("company-list"),
        {
            "display_name": "Anonymous Company",
            "category": CategoryTypes.OTHER,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_related_companies_are_bidirectional():
    company_a = Company.objects.create(
        display_name="Company A",
        id_name="company-a",
        category=CategoryTypes.OTHER,
    )
    company_b = Company.objects.create(
        display_name="Company B",
        id_name="company-b",
        category=CategoryTypes.OTHER,
    )

    company_a.related_companies.add(company_b)

    assert company_b in company_a.related_companies.all()
    assert company_a in company_b.related_companies.all()


@pytest.mark.django_db
def test_company_admin_can_update_related_companies(api_client, dummy_user):
    api_client.force_authenticate(user=dummy_user)

    main_company = Company.objects.create(
        display_name="Main Co",
        id_name="main-co",
        category=CategoryTypes.OTHER,
    )
    related_company = Company.objects.create(
        display_name="Related Co",
        id_name="related-co",
        category=CategoryTypes.OTHER,
    )
    CompanyAdmin.objects.create(
        company=main_company,
        user=dummy_user,
        role=CompanyAdmin.SUPERADMIN,
    )

    response = api_client.patch(
        reverse("company-admin", args=[main_company.id]),
        {
            "related_company_ids": [related_company.id],
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    main_company.refresh_from_db()
    related_company.refresh_from_db()
    assert related_company in main_company.related_companies.all()
    assert main_company in related_company.related_companies.all()


@pytest.mark.django_db
def test_company_primary_location_is_persisted_from_primary_branch():
    company = Company.objects.create(
        display_name="Persisted Primary Co",
        id_name="persisted-primary-co",
        category=CategoryTypes.OTHER,
    )
    country, _ = Country.objects.get_or_create(
        country_code="PT",
        defaults={
            "name": "Portugal",
            "region": RegionTypes.EUROPE,
            "subregion": SubRegionTypes.SOUTHERN_EUROPE,
            "business_region": BusinessRegionTypes.EMEA,
        },
    )
    lisbon, _ = Location.objects.get_or_create(name="Lisbon", country=country)

    address = Address.objects.create(
        street="Avenida da Liberdade",
        number="100",
        postal_code="1250-146",
        location=lisbon,
        latitude=38.7223,
        longitude=-9.1393,
    )

    Branch.objects.create(
        company=company,
        address=address,
        name="HQ",
        is_primary=True,
    )

    company.refresh_from_db()
    assert company.primary_location == str(lisbon)


@pytest.mark.django_db
def test_company_primary_location_clears_when_primary_branch_deleted():
    company = Company.objects.create(
        display_name="Delete Primary Co",
        id_name="delete-primary-co",
        category=CategoryTypes.OTHER,
    )
    country, _ = Country.objects.get_or_create(
        country_code="IT",
        defaults={
            "name": "Italy",
            "region": RegionTypes.EUROPE,
            "subregion": SubRegionTypes.SOUTHERN_EUROPE,
            "business_region": BusinessRegionTypes.EMEA,
        },
    )
    rome, _ = Location.objects.get_or_create(name="Rome", country=country)

    address = Address.objects.create(
        street="Via del Corso",
        number="1",
        postal_code="00186",
        location=rome,
        latitude=41.9028,
        longitude=12.4964,
    )

    branch = Branch.objects.create(
        company=company,
        address=address,
        name="HQ",
        is_primary=True,
    )
    branch.delete()

    company.refresh_from_db()
    assert company.primary_location is None
