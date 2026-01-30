from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from reviews.models import Review
from reviews.serializers import MyReviewSerializer



class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ReviewViewSet(ModelViewSet):
    """
    API endpoint that allows reviews to be viewed or edited.
    """
    permission_classes = (AllowAny,)
    queryset = Review.objects.all()
    serializer_class = MyReviewSerializer
    pagination_class = ReviewPagination
    
    @action(detail=False, methods=["get"], url_path="me")
    def my_reviews(self, request, *args, **kwargs):
        """
        Endpoint para obtener todas las reviews del usuario autenticado.
        """
        queryset = self.get_queryset().filter(reviewer_id=request.user.id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
