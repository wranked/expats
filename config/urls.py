"""expats URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from companies.routers import router, company_router
from blog.routers import blog_router
from jobs.routers import jobs_router
from reviews.routers import reviews_router

# from companies.views import ReviewViewSet
from blog.urls import urlpatterns as blog_urlpatterns
from users.views import UserLogin, UserLogout, UserRegister, UserView

urlpatterns = ([
    path('admin/', admin.site.urls),

    path('', include(router.urls)),
    path('', include(company_router.urls)),
    path('', include(blog_router.urls)),
    path('', include(jobs_router.urls)),
    path('', include(reviews_router.urls)),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('register/', UserRegister.as_view(), name='register'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('users/', UserView.as_view(), name='users'),

    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
])  # + blog_urlpatterns)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
