from django.views.generic import ListView
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from .models import Post
from .serializers import PostSerializer


class BlogListView(ListView):
    model = Post
    template_name = "post_list.html"


class BlogViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name", "language_code"]

    def get_object(self):
        queryset = self.get_queryset()
        post_id = self.kwargs.get("pk")
        if len(post_id) > 3:
            name = post_id[:-3]
            lang = post_id[-2:]
        else:
            raise NotFound()
        filters = dict(name=name, language_code=lang)
        obj = get_object_or_404(queryset, **filters)
        self.check_object_permissions(self.request, obj)
        return obj
