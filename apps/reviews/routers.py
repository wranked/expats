from rest_framework_nested import routers

from .views import ReviewViewSet


reviews_router = routers.DefaultRouter()

reviews_router.register(r'reviews', ReviewViewSet)

