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
            "display_name",
        ]

        write_only_fields = [
            "password",
        ]

    def create(self, data):
        user = UserModel.objects.create_user(
            username=data.get("username", None),
            email=data["email"],
            password=data["password"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            picture=data["picture"],  # TODO: Make it optional
        )
        # user.save()  # TODO: Check if it is necessary this .save() call
        return user


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
