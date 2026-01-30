from rest_framework.permissions import BasePermission

from companies.models import CompanyAdmin


class IsCompanyAdmin(BasePermission):
    """Allows access only to users who are admins of the company."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return CompanyAdmin.objects.filter(user=request.user, company=obj.company).exists()


class IsSuperAdmin(BasePermission):
    """Allows access only to super admins."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser
