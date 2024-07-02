import pytest

from users.models import CustomUser


@pytest.mark.django_db
def test_user_create():
    CustomUser.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")
    test_user = CustomUser.objects.get(username="john")
    assert test_user.username == "john"
    assert test_user.email == "lennon@thebeatles.com"
    assert test_user.password != "johnpassword"
