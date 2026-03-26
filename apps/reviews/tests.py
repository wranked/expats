import pytest
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.constants import CategoryTypes
from apps.companies.models import Company
from apps.users.models import CustomUser

from .models import Review


@pytest.fixture
def api_client():
	return APIClient()


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


@pytest.mark.django_db
def test_review_content_update_resets_approval():
	company = Company.objects.create(
		display_name="Foo Bar",
		id_name="foo-bar-update",
		category=CategoryTypes.OTHER,
	)
	reviewer = CustomUser.objects.create_user(
		email="reviewer@test.com",
		password="password",
	)

	review = Review.objects.create(
		rating=4,
		salary_range=0,
		salary_currency="",
		salary_frequency="",
		comment="Good place",
		is_public=True,
		company=company,
		reviewer=reviewer,
		approved_at=timezone.now(),
	)

	review.comment = "Updated comment"
	review.save()
	review.refresh_from_db()

	assert review.approved_at is None


@pytest.mark.django_db
def test_review_approval_update_keeps_approval_date():
	company = Company.objects.create(
		display_name="Foo Bar",
		id_name="foo-bar-approval",
		category=CategoryTypes.OTHER,
	)
	reviewer = CustomUser.objects.create_user(
		email="reviewer2@test.com",
		password="password",
	)

	review = Review.objects.create(
		rating=4,
		salary_range=0,
		salary_currency="",
		salary_frequency="",
		comment="Good place",
		is_public=True,
		company=company,
		reviewer=reviewer,
	)

	approved_at = timezone.now()
	review.approved_at = approved_at
	review.save()
	review.refresh_from_db()

	assert review.approved_at == approved_at


@pytest.mark.django_db
def test_create_duplicate_review_returns_handled_error(api_client):
	company = Company.objects.create(
		display_name="Unique Review Co",
		id_name="unique-review-co",
		category=CategoryTypes.OTHER,
	)
	reviewer = CustomUser.objects.create_user(
		email="duplicate-reviewer@test.com",
		password="password",
	)
	api_client.force_authenticate(user=reviewer)

	payload = {
		"rating": 4,
		"comment": "First review",
		"start_date": None,
		"end_date": None,
		"is_public": True,
	}
	url = reverse("company-reviews-list", kwargs={"company_pk": company.id})

	first_response = api_client.post(url, payload, format="json")
	assert first_response.status_code == status.HTTP_201_CREATED

	second_response = api_client.post(url, payload, format="json")
	assert second_response.status_code == status.HTTP_409_CONFLICT
	assert second_response.data["detail"] == "You have already submitted a review for this company."


@pytest.mark.django_db
def test_patch_my_review(api_client):
	company = Company.objects.create(
		display_name="Patch Review Co",
		id_name="patch-review-co",
		category=CategoryTypes.OTHER,
	)
	reviewer = CustomUser.objects.create_user(
		email="patch-owner@test.com",
		password="password",
	)
	review = Review.objects.create(
		rating=4,
		salary_range=0,
		salary_currency="",
		salary_frequency="",
		comment="Old comment",
		is_public=True,
		company=company,
		reviewer=reviewer,
	)

	api_client.force_authenticate(user=reviewer)
	url = reverse("company-reviews-detail", kwargs={"company_pk": company.id, "pk": "me"})
	response = api_client.patch(url, {"comment": "Updated from patch"}, format="json")

	assert response.status_code == status.HTTP_200_OK
	review.refresh_from_db()
	assert review.comment == "Updated from patch"


@pytest.mark.django_db
def test_patch_review_forbidden_for_other_user(api_client):
	company = Company.objects.create(
		display_name="Patch Forbidden Co",
		id_name="patch-forbidden-co",
		category=CategoryTypes.OTHER,
	)
	owner = CustomUser.objects.create_user(
		email="patch-owner2@test.com",
		password="password",
	)
	other_user = CustomUser.objects.create_user(
		email="patch-other@test.com",
		password="password",
	)
	review = Review.objects.create(
		rating=4,
		salary_range=0,
		salary_currency="",
		salary_frequency="",
		comment="Original",
		is_public=True,
		company=company,
		reviewer=owner,
		approved_at=timezone.now(),
	)

	api_client.force_authenticate(user=other_user)
	url = reverse("company-reviews-detail", kwargs={"company_pk": company.id, "pk": review.id})
	response = api_client.patch(url, {"comment": "Should fail"}, format="json")

	assert response.status_code == status.HTTP_403_FORBIDDEN
	assert response.data["detail"] == "You can only edit your own review."
