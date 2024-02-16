from rest_framework import routers

from expatsapp import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'companies', views.CompanyViewSet)
router.register(r'reviews', views.ReviewViewSet)
