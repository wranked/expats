import pytest

from expatsapp.constants import CategoryTypes
from expatsapp.models import Company, Review
from users.models import CustomUser


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
        is_anonymous=True,
        company=dummy_company,
        reviewer=dummy_user,
    )
    assert dummy_company.rating_summary == dict({1: 0, 2: 0, 3: 0, 4: 0, 5: 1, "count": 1, "media": 5})


@pytest.mark.django_db
def test_create_2_reviews(dummy_company, dummy_user, dummy_user2):
    Review.objects.create(
        rating=5,
        salary_range=0,
        salary_currency="",
        salary_frequency="",
        comment="",
        is_anonymous=True,
        company=dummy_company,
        reviewer=dummy_user,
    )
    assert dummy_company.rating_summary == dict({1: 0, 2: 0, 3: 0, 4: 0, 5: 1, "count": 1, "media": 5})

    Review.objects.create(
        rating=2,
        salary_range=0,
        salary_currency="",
        salary_frequency="",
        comment="",
        is_anonymous=True,
        company=dummy_company,
        reviewer=dummy_user2,
    )
    assert dummy_company.rating_summary == dict({1: 0, 2: 1, 3: 0, 4: 0, 5: 1, "count": 2, "media": 3.5})
