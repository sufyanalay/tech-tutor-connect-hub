
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import RepairRequest, RepairMedia, RepairComment
from .serializers import RepairRequestSerializer, RepairMediaSerializer, RepairCommentSerializer
from users.permissions import IsAdminUser, IsTechnician, IsStudent


class RepairRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RepairRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'device_type']
    search_fields = ['title', 'description', 'device_model']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        user = self.request.user
        # Admin can see all repair requests
        if user.is_staff or user.role == 'admin':
            return RepairRequest.objects.all()
        # Technicians can see assigned repairs and unassigned (pending) repairs
        elif user.role == 'technician':
            return RepairRequest.objects.filter(technician=user) | RepairRequest.objects.filter(technician=None, status='pending')
        # Students can see only their own repairs
        elif user.role == 'student':
            return RepairRequest.objects.filter(student=user)
        # Default empty queryset
        return RepairRequest.objects.none()
    
    def get_permissions(self):
        """
        Custom permissions based on action:
        - create: only students can create repair requests
        - assign: only technicians can assign repair requests to themselves
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsStudent]
        elif self.action in ['assign', 'update_status']:
            permission_classes = [permissions.IsAuthenticated, IsTechnician]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Endpoint for technicians to assign themselves to a repair request"""
        repair_request = self.get_object()
        
        if repair_request.technician is not None:
            return Response(
                {"detail": "This repair request is already assigned."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if repair_request.status != 'pending':
            return Response(
                {"detail": "Only pending repair requests can be assigned."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repair_request.technician = request.user
        repair_request.status = 'assigned'
        repair_request.save()
        
        return Response(
            {"detail": f"Repair request '{repair_request.title}' assigned to you successfully."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Endpoint to update the status of a repair request"""
        repair_request = self.get_object()
        
        if repair_request.technician != request.user:
            return Response(
                {"detail": "You are not assigned to this repair request."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        allowed_statuses = ['in_progress', 'completed', 'cancelled']
        
        if not new_status or new_status not in allowed_statuses:
            return Response(
                {"detail": f"Invalid status. Choose from {', '.join(allowed_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repair_request.status = new_status
        
        # If completed, require final cost
        if new_status == 'completed':
            final_cost = request.data.get('final_cost')
            if not final_cost:
                return Response(
                    {"detail": "Final cost is required when marking as completed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            repair_request.final_cost = final_cost
            
            # Update technician's total earnings
            if repair_request.technician and hasattr(repair_request.technician, 'profile'):
                profile = repair_request.technician.profile
                profile.total_earnings += float(final_cost)
                profile.save()
        
        repair_request.save()
        
        return Response(
            {"detail": f"Repair request status updated to: {new_status}"},
            status=status.HTTP_200_OK
        )


class RepairMediaViewSet(viewsets.ModelViewSet):
    serializer_class = RepairMediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RepairMedia.objects.filter(
            repair_request__student=self.request.user
        ) | RepairMedia.objects.filter(
            repair_request__technician=self.request.user
        )
    
    def perform_create(self, serializer):
        repair_request = get_object_or_404(
            RepairRequest, 
            pk=self.request.data.get('repair_request')
        )
        
        # Only allow the student who created the request or the assigned technician to add media
        if repair_request.student != self.request.user and repair_request.technician != self.request.user:
            raise permissions.exceptions.PermissionDenied(
                "You don't have permission to add media to this repair request."
            )
        
        serializer.save()


class RepairCommentViewSet(viewsets.ModelViewSet):
    serializer_class = RepairCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RepairComment.objects.filter(
            repair_request__student=self.request.user
        ) | RepairComment.objects.filter(
            repair_request__technician=self.request.user
        )
    
    def perform_create(self, serializer):
        repair_request = get_object_or_404(
            RepairRequest, 
            pk=self.request.data.get('repair_request')
        )
        
        # Only allow the student who created the request or the assigned technician to add comments
        if repair_request.student != self.request.user and repair_request.technician != self.request.user:
            raise permissions.exceptions.PermissionDenied(
                "You don't have permission to comment on this repair request."
            )
        
        serializer.save(user=self.request.user)
