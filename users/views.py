from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
# from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from users.serializers import UserLoginSerializer, UserRegisterSerializer, UserSerializer, UserUpdateSerializer


class UserRegister(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        clean_data = request.data  # custom_validator(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                response_serializer = UserRegisterSerializer(user)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = [permissions.AllowAny]
    # authentication_classes = (SessionAuthentication, )

    def post(self, request):
        data = request.data
        # assert validate_email(data)
        # assert validate_password(data)
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid():
            # user = serializer.check_user(data)
            # login(request, user)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # logout(request)
        # return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    print("UserView.Apiview")
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = (JWTAuthentication, )

    def get(self, request):
        print("UserView.get")
        serializer = UserSerializer(request.user)
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)
    
    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
