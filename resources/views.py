
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Resource, ResourceCategory
from .serializers import ResourceSerializer, ResourceCategorySerializer
from users.permissions import IsAdminUser


class ResourceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ResourceCategory.objects.all()
    serializer_class = ResourceCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Custom permissions:
        - List/retrieve: Any authenticated user
        - Create/update/delete: Admin only
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'category', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'view_count', 'title']
    
    def get_queryset(self):
        return Resource.objects.all()
    
    def get_permissions(self):
        """
        Custom permissions:
        - List/retrieve: Any authenticated user
        - Create: Teachers and technicians can create resources
        - Update/delete: Creator or admin
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """Track resource views"""
        resource = self.get_object()
        resource.view_count += 1
        resource.save()
        return Response({"detail": "View count incremented."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured resources"""
        featured = Resource.objects.filter(is_featured=True)
        page = self.paginate_queryset(featured)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
