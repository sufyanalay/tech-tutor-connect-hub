
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourceViewSet, ResourceCategoryViewSet

router = DefaultRouter()
router.register('categories', ResourceCategoryViewSet)
router.register('resources', ResourceViewSet, basename='resource')

urlpatterns = [
    path('', include(router.urls)),
]
