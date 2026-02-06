import pytest

from apps.companies.constants import CategoryTypes
from apps.companies.models import Company
from apps.users.models import CustomUser

from .models import Review


@pytest.mark.django_db
def test_review_str_anonymous():
	company = Company.objects.create(
		display_name="Foo Bar",
		id_name="foo-bar",
		category=CategoryTypes.OTHER,
	)
	reviewer = CustomUser.objects.create_user(
		email="anon@test.com",
		password="password",
	)
	reviewer.display_name = ""
	reviewer.save()

	review = Review.objects.create(
		rating=4,
		salary_range=0,
		salary_currency="",
		salary_frequency="",
		comment="Nice place",
		is_public=True,
		company=company,
		reviewer=reviewer,
	)

	assert str(review) == "Foo Bar - Anonymous"
