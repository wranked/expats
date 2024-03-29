from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import CustomUser


UserModel = CustomUser  # get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            "email",
            "username",
            "display_name",
            "picture",
        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "picture",
        ]

        write_only_fields = [
            "password",
        ]

    def create(self, data):
        user_obj = UserModel.objects.create_user(
            username="dummy_username",  # TODO: Make it optional
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            picture=data["picture"],
        )
        # user_obj.username = clean_data["username"]
        user_obj.save()
        return user_obj


class UserLoginSerializer(serializers.Serializer):
    # username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        user = authenticate(
            email=clean_data["email"],
            password=clean_data["password"],
        )
        if not user:
            raise ValidationError("User not found")
        return user
