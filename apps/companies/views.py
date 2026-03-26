from django.db import IntegrityError
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import CompanyFilter
from .constants import CreatedViaTypes
from .models import Company, CompanyAdmin
from .permissions import IsCompanyAdmin, IsSuperAdmin
from .serializers import CompanySerializer, ManageCompanySerializer

from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer, JobDetailsSerializer
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Request conflicts with the current state of the resource."
    default_code = "conflict"


class CompanyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CompanyViewSet(ModelViewSet):
    """
    API endpoint that allows companies to be viewed or edited.
    """
    permission_classes = (AllowAny,)
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = CompanyPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CompanyFilter
    search_fields = ["display_name", "branches__name"]

    ordering_fields = ["reviews_rating", "-id"]
    ordering = ["-reviews_rating"]
    http_method_names = ["head", "options", "get", "post", "patch"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, created_via=CreatedViaTypes.API)

    @action(detail=False, methods=["get"], url_path="me")
    def my_companies(self, request, *args, **kwargs):
        """
        Endpoint to obtain all companies managed by an authenticated user.
        """
        queryset = self.get_queryset().filter(admins__user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "patch"], url_path="admin", permission_classes=[IsAuthenticated])
    def admin(self, request, pk=None):
        """
        This endpoint retrieves additional admin-specific details for a company.
        """
        company = self.get_object()

        if request.method == "GET":
            if not CompanyAdmin.objects.filter(company=company, user=request.user).exists():
                return Response({"detail": "You do not have permission to access this."}, status=403)

            serializer = ManageCompanySerializer(company)
            return Response(serializer.data)
        
        if request.method == "PATCH":
            serializer = ManageCompanySerializer(company, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CompanyReviewViewSet(ModelViewSet):
    """
    API endpoint that allows reviews to be viewed or edited by a given company.
    """
    authentication_classes = [TokenAuthentication]
    queryset = Review.objects.all().select_related('company')  # TODO: Check if this relationship is necessary
    serializer_class = ReviewSerializer
    pagination_class = ReviewPagination
    http_method_names = ["head", "options", "get", "post", "patch"]  # , "put", "delete", ]

    def get_permissions(self):
        if self.action in ["list"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self, *args, **kwargs):
        company_id = self.kwargs.get("company_pk")
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise NotFound()
        queryset = self.queryset.filter(company=company)
        if self.action in ["list", "other_reviews"]:
            return queryset.filter(approved_at__isnull=False)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        review_id = self.kwargs.get("pk")
        if review_id == "me":
            filters = dict(reviewer_id=self.request.user.id)
        else:
            filters = dict(id=review_id, approved_at__isnull=False)
        obj = get_object_or_404(queryset, **filters)
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # .exclude(reviewer_id=self.request.user.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        company_id = self.kwargs.get("company_pk")
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise NotFound()
        # TODO: Move IP storage to a logger or a separate model to avoid storing
        #  it in the review itself, which is not ideal for privacy reasons.
        ip = self.request.META.get("HTTP_X_FORWARDED_FOR", self.request.META.get("REMOTE_ADDR"))
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()
        try:
            serializer.save(
                reviewer=self.request.user,
                company=company,
                reviewer_ip=ip,
            )
        except IntegrityError as exc:
            raise ConflictError("You have already submitted a review for this company.") from exc

    def partial_update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.reviewer_id != request.user.id:
            return Response({"detail": "You can only edit your own review."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="others")
    def other_reviews(self, request, *args, **kwargs):
        queryset = self.get_queryset().exclude(reviewer_id=self.request.user.id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CompanyJobViewSet(ModelViewSet):
    """
    API endpoint that allows Jobs to be viewed or edited by a given company.
    """
    permission_classes = (AllowAny,)
    queryset = Job.objects.all().select_related('company')
    pagination_class = JobPagination
    http_method_names = ["head", "options", "get"]


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

    def perform_create(self, serializer):
        company_id = self.kwargs.get("company_pk")
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise NotFound()
        serializer.save(
            company=company,
        )


# class ManageCompanyViewSet(ModelViewSet):
#     """
#     ViewSet to manage company administrators.
#     Only company admins can see their own company admins, 
#     and super admins can see all.
#     """
#     queryset = Company.objects.all()
#     serializer_class = ManageCompanySerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_permissions(self):
#         """
#         Assign permissions dynamically:
#         - Super admins can access everything.
#         - Company admins can only see their company's admins.
#         """
#         if self.request.user.is_superuser:
#             self.permission_classes = [IsAuthenticated, IsSuperAdmin]
#         else:
#             self.permission_classes = [IsAuthenticated, IsCompanyAdmin]
        
#         return [permission() for permission in self.permission_classes]

#     def get_object(self):
#         queryset = self.get_queryset()
#         company_id = self.kwargs.get("pk")
#         obj = get_object_or_404(queryset, {id: company_id})
#         # self.check_object_permissions(self.request, obj)
#         return obj

    # def get_queryset(self):
    #     """
    #     - Super admins get all data.
    #     - Company admins only get their company's admins.
    #     """
    #     user = self.request.user
    #     if user.is_superuser:
    #         return CompanyAdmin.objects.all()
    #     company_id = self.kwargs.get("company_pk")
    #     queryset = CompanyAdmin.objects.filter(company=company_id)
    #     if queryset.filter(user=user).exists():
    #         return queryset
    #     return CompanyAdmin.objects.none()


# class CompanyAdminViewSet(ModelViewSet):
#     """
#     ViewSet to manage company administrators.
#     Only company admins can see their own company admins, 
#     and super admins can see all.
#     """
#     queryset = CompanyAdmin.objects.all()
#     serializer_class = CompanyAdminSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_permissions(self):
#         """
#         Assign permissions dynamically:
#         - Super admins can access everything.
#         - Company admins can only see their company's admins.
#         """
#         if self.request.user.is_superuser:
#             self.permission_classes = [IsAuthenticated, IsSuperAdmin]
#         else:
#             self.permission_classes = [IsAuthenticated, IsCompanyAdmin]
        
#         return [permission() for permission in self.permission_classes]

#     def get_queryset(self):
#         """
#         - Super admins get all data.
#         - Company admins only get their company's admins.
#         """
#         user = self.request.user
#         if user.is_superuser:
#             return CompanyAdmin.objects.all()
#         company_id = self.kwargs.get("company_pk")
#         queryset = CompanyAdmin.objects.filter(company=company_id)
#         if queryset.filter(user=user).exists():
#             return queryset
#         return CompanyAdmin.objects.none()

    # def perform_create(self, serializer):
    #     """Asegurar que el usuario agregando admins es un superadmin de la empresa."""
    #     company_id = self.kwargs["company_pk"]
    #     company = get_object_or_404(Company, id=company_id)

    #     if not CompanyAdmin.objects.filter(company=company, user=self.request.user, role=CompanyAdmin.SUPERADMIN).exists():
    #         return Response({"error": "You do not have permissions to add admins."}, status=403)

    #     serializer.save(company=company)
