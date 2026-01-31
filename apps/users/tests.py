import pytest
from django.urls import reverse

from .models import CustomUser


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.mark.django_db
def test_user_create():
    CustomUser.objects.create_user(
        email="lennon@thebeatles.com",
        password="johnpassword",
        username=None,
        first_name="John",
        last_name="Lennon",
    )
    test_user = CustomUser.objects.get(email="lennon@thebeatles.com")
    assert test_user.username.startswith("john-lennon-")
    assert test_user.email == "lennon@thebeatles.com"
    assert test_user.password != "johnpassword"
    assert test_user.first_name == "John"
    assert test_user.last_name == "Lennon"
    assert test_user.display_name == "John Lennon"


@pytest.mark.django_db
def test_user_create_no_names():
    CustomUser.objects.create_user(
        email="lennon@thebeatles.com",
        password="johnpassword",
    )
    test_user = CustomUser.objects.get(email="lennon@thebeatles.com")
    assert test_user.username.startswith("user-")
    assert test_user.email == "lennon@thebeatles.com"
    assert test_user.password != "johnpassword"
    assert test_user.first_name == ""
    assert test_user.last_name == ""
    assert test_user.display_name == "user"


@pytest.mark.django_db
def test_api_user_create(api_client):
    url = reverse('register')
    paylaod = {
        "email": "gustavo@tempel.com",
        "password": "123456",
        "username": "gustavo1000",
        "first_name": "Gustavo",
        "last_name": "Tempel",
        "picture": ""
    }
    response = api_client.post(url, paylaod)
    assert response.status_code == 201
    test_user = CustomUser.objects.get(email="gustavo@tempel.com")
    assert test_user.username == "gustavo1000"

