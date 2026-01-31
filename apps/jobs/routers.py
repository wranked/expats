from rest_framework_nested import routers

from .views import JobViewSet


jobs_router = routers.DefaultRouter()

jobs_router.register(r'jobs', JobViewSet)
