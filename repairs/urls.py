
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepairRequestViewSet, RepairMediaViewSet, RepairCommentViewSet

router = DefaultRouter()
router.register('requests', RepairRequestViewSet, basename='repair-request')
router.register('media', RepairMediaViewSet, basename='repair-media')
router.register('comments', RepairCommentViewSet, basename='repair-comment')

urlpatterns = [
    path('', include(router.urls)),
]
