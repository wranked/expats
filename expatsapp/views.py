from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from expatsapp.models import Company, Review, Job
from expatsapp.serializers import CompanySerializer, ReviewSerializer, JobSerializer, JobDetailsSerializer


class CompanyViewSet(ModelViewSet):
    """
    API endpoint that allows companies to be viewed or edited.
    """
    permission_classes = (AllowAny,)
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    http_method_names = ["head", "options", "get", "put", "patch", "delete", "post", ]


class ReviewViewSet(ModelViewSet):
    """
    API endpoint that allows reviews to be viewed or edited.
    """
    permission_classes = (AllowAny,)
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class CompanyReviewViewSet(ModelViewSet):
    """
    API endpoint that allows reviews to be viewed or edited by a given company.
    """
    permission_classes = (AllowAny,)
    queryset = Review.objects.all().select_related('company')  # TODO: Check if this relationship is necessary
    serializer_class = ReviewSerializer

    def get_queryset(self, *args, **kwargs):
        company_id = self.kwargs.get("company_pk")
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise NotFound()
        return self.queryset.filter(company=company)

    def get_object(self):
        queryset = self.get_queryset()
        review_id = self.kwargs.get("pk")
        if review_id == "me":
            filters = dict(reviewer_id=self.request.user.id)
        else:
            filters = dict(id=review_id)
        obj = get_object_or_404(queryset, **filters)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        company_id = self.kwargs.get("company_pk")
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise NotFound()
        serializer.save(
            reviewer=self.request.user,
            company=company,
        )


class JobViewSet(ModelViewSet):
    """
    API endpoint that allows Jobs to be viewed or edited.
    """
    permission_classes = (AllowAny,)
    queryset = Job.objects.all()

    def get_serializer_class(self):
        if self.action in ["list"]:
            return JobSerializer
        return JobDetailsSerializer


class CompanyJobViewSet(ModelViewSet):
    """
    API endpoint that allows Jobs to be viewed or edited by a given company.
    """
    permission_classes = (AllowAny,)
    queryset = Job.objects.all().select_related('company')

    def get_serializer_class(self):
        if self.action in ["list"]:
            return JobSerializer
        return JobDetailsSerializer

    def get_queryset(self, *args, **kwargs):
        company_id = self.kwargs.get("company_pk")
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise NotFound()
        return self.queryset.filter(company=company)
