from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from users.models import CustomUser


UserModel = CustomUser  # get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
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

    def validate(self, data):
        user = authenticate(
            email=data["email"],
            password=data["password"],
        )
        if user is None:
            raise serializers.ValidationError("Credenciales incorrectas.")
        
        if not user.is_active:
            raise serializers.ValidationError("Esta cuenta está inactiva.")

        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        return {"user": user_data, "token": token.key}

        try:
            user = CustomUser.objects.get(email=data['email'])
            if user.check_password(data['password']):
                # Si las credenciales son correctas, se devuelve el token
                token, created = Token.objects.get_or_create(user=user)
                return {'token': token.key}
            else:
                raise serializers.ValidationError('Invalid credentials')
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')
        
    def check_user(self, clean_data):
        user = authenticate(
            email=clean_data["email"],
            password=clean_data["password"],
        )
        if not user:
            raise ValidationError("User not found")
        token, created = Token.objects.get_or_create(user=user)
        print("---------------TOKEN:", token)
        return {"user": user, "token": token.key}


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "display_name",
            "first_name",
            "last_name",
            "email",
            "picture",
        ]
        extra_kwargs = {
            "username": {"required": False},
            "display_name": {"required": False},
            "email": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "picture": {"required": False},
        }

    def validate_username(self, value):
        """Verifica si el username ya está en uso por otro usuario"""
        if CustomUser.objects.filter(username=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Este username ya está en uso.")
        return value

    def validate_email(self, value):
        """Verifica si el email ya está en uso por otro usuario"""
        if CustomUser.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Este email ya está en uso.")
        return value
