from rest_framework_nested import routers

from expatsapp.views import CompanyReviewViewSet, CompanyViewSet, ReviewViewSet


router = routers.SimpleRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'reviews', ReviewViewSet)

company_router = routers.NestedSimpleRouter(router, r'companies', lookup='company')
company_router.register(r'reviews', CompanyReviewViewSet, basename='company-reviews')
