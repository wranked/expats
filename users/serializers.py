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
        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            "email",
            "username",
            "password",
        ]

    def create(self, clean_data):
        user_obj = UserModel.objects.create_user(
            email=clean_data["email"],
            username=clean_data["username"],
            password=clean_data["password"],
        )
        # user_obj.username = clean_data["username"]
        user_obj.save()
        return user_obj


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        user = authenticate(
            username=clean_data["username"],
            password=clean_data["password"],
        )
        if not user:
            raise ValidationError("User not found")
        return user
