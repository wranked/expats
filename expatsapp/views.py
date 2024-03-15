from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from expatsapp.models import Company, Review
from expatsapp.serializers import CompanySerializer, ReviewSerializer


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


class CompanyReviewViewSet(ModelViewSet):
    """
    API endpoint that allows reviews to be viewed or edited by a given company.
    """
    permission_classes = (AllowAny,)
    queryset = Review.objects.all().select_related('company')
    serializer_class = ReviewSerializer

    def get_queryset(self, *args, **kwargs):
        company_id = self.kwargs.get("company_pk")
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise NotFound()
        return self.queryset.filter(company=company)
