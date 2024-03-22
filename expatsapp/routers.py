from rest_framework_nested import routers

from expatsapp.views import CompanyReviewViewSet, CompanyViewSet, ReviewViewSet, JobViewSet, CompanyJobViewSet


router = routers.SimpleRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'jobs', JobViewSet)

company_router = routers.NestedSimpleRouter(router, r'companies', lookup='company')
company_router.register(r'reviews', CompanyReviewViewSet, basename='company-reviews')
company_router.register(r'jobs', CompanyJobViewSet, basename='company-jobs')
