from rest_framework import routers

from users import views


user_router = routers.DefaultRouter()
user_router.register(r'register', views.UserRegister)
# user_router.register(r'login', views.UserLogin, basename="api")
# user_router.register(r'logout', views.UserLogout, basename="api")
# user_router.register(r'user', views.UserSerializer, basename="api")
