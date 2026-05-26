from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImportBatchViewSet

router = DefaultRouter()
router.register(r"batches", ImportBatchViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
