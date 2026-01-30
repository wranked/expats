from rest_framework_nested import routers

from companies.views import CompanyReviewViewSet, CompanyViewSet, CompanyJobViewSet


router = routers.SimpleRouter()
router.register(r'companies', CompanyViewSet)


company_router = routers.NestedSimpleRouter(router, r'companies', lookup='company')
company_router.register(r'reviews', CompanyReviewViewSet, basename='company-reviews')
company_router.register(r'jobs', CompanyJobViewSet, basename='company-jobs')
# company_router.register(r'admin', CompanyManageViewSet, basename='company-manage')

