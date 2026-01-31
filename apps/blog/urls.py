from django.urls import path

from .views import BlogListView, BlogViewSet

urlpatterns = [
    # path("blog/", BlogListView.as_view(), name='blog_list'),
    path("articles/", BlogViewSet.as_view({'get': 'list'})),
]