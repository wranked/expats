from rest_framework import routers

from .views import BlogViewSet


blog_router = routers.DefaultRouter()

blog_router.register(r'articles', BlogViewSet)
