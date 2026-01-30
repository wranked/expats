from rest_framework_nested import routers

from jobs.views import JobViewSet


jobs_router = routers.DefaultRouter()

jobs_router.register(r'jobs', JobViewSet)
