from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from .models import Job
from .serializers import JobSerializer, JobDetailsSerializer


class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class JobViewSet(ModelViewSet):
    """
    API endpoint that allows Jobs to be viewed or edited.
    """
    permission_classes = (AllowAny,)
    queryset = Job.objects.all()
    pagination_class = JobPagination

    def get_serializer_class(self):
        if self.action in ["list"]:
            return JobSerializer
        return JobDetailsSerializer
