from rest_framework.routers import DefaultRouter
from .views import PDFDocumentViewSet, ExtractedDataViewSet

router = DefaultRouter()
router.register(r'pdf-documents', PDFDocumentViewSet, basename='pdf-document')
router.register(r'extracted-data', ExtractedDataViewSet, basename='extracted-data')

urlpatterns = router.urls
