
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import AcademicQuestion, AcademicQuestionMedia, AcademicAnswer
from .serializers import AcademicQuestionSerializer, AcademicQuestionMediaSerializer, AcademicAnswerSerializer
from users.permissions import IsAdminUser, IsTeacher, IsStudent


class AcademicQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicQuestionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'subject']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        user = self.request.user
        # Admin can see all questions
        if user.is_staff or user.role == 'admin':
            return AcademicQuestion.objects.all()
        # Teachers can see assigned questions and unassigned (pending) questions
        elif user.role == 'teacher':
            return AcademicQuestion.objects.filter(teacher=user) | AcademicQuestion.objects.filter(teacher=None, status='pending')
        # Students can see only their own questions
        elif user.role == 'student':
            return AcademicQuestion.objects.filter(student=user)
        # Default empty queryset
        return AcademicQuestion.objects.none()
    
    def get_permissions(self):
        """
        Custom permissions based on action:
        - create: only students can create questions
        - assign: only teachers can assign questions to themselves
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsStudent]
        elif self.action in ['assign', 'update_status']:
            permission_classes = [permissions.IsAuthenticated, IsTeacher]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Endpoint for teachers to assign themselves to a question"""
        question = self.get_object()
        
        if question.teacher is not None:
            return Response(
                {"detail": "This question is already assigned."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if question.status != 'pending':
            return Response(
                {"detail": "Only pending questions can be assigned."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        question.teacher = request.user
        question.status = 'assigned'
        question.save()
        
        return Response(
            {"detail": f"Question '{question.title}' assigned to you successfully."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Endpoint to update the status of a question"""
        question = self.get_object()
        
        if question.teacher != request.user:
            return Response(
                {"detail": "You are not assigned to this question."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        allowed_statuses = ['answered', 'closed']
        
        if not new_status or new_status not in allowed_statuses:
            return Response(
                {"detail": f"Invalid status. Choose from {', '.join(allowed_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        question.status = new_status
        question.save()
        
        return Response(
            {"detail": f"Question status updated to: {new_status}"},
            status=status.HTTP_200_OK
        )


class AcademicQuestionMediaViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicQuestionMediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AcademicQuestionMedia.objects.filter(
            question__student=self.request.user
        ) | AcademicQuestionMedia.objects.filter(
            question__teacher=self.request.user
        )
    
    def perform_create(self, serializer):
        question = get_object_or_404(
            AcademicQuestion, 
            pk=self.request.data.get('question')
        )
        
        # Only allow the student who created the question or the assigned teacher to add media
        if question.student != self.request.user and question.teacher != self.request.user:
            raise permissions.exceptions.PermissionDenied(
                "You don't have permission to add media to this question."
            )
        
        serializer.save()


class AcademicAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Admin can see all answers
        if user.is_staff or user.role == 'admin':
            return AcademicAnswer.objects.all()
        # Teachers can see their own answers
        elif user.role == 'teacher':
            return AcademicAnswer.objects.filter(teacher=user)
        # Students can see answers to their questions
        elif user.role == 'student':
            return AcademicAnswer.objects.filter(question__student=user)
        # Default empty queryset
        return AcademicAnswer.objects.none()
    
    def perform_create(self, serializer):
        question = get_object_or_404(
            AcademicQuestion,
            pk=self.request.data.get('question')
        )
        
        # Only the assigned teacher can answer the question
        if question.teacher != self.request.user:
            raise permissions.exceptions.PermissionDenied(
                "You are not assigned to this question and cannot answer it."
            )
        
        answer = serializer.save(teacher=self.request.user)
        
        # Update question status to answered when teacher provides an answer
        if question.status == 'assigned':
            question.status = 'answered'
            question.save()
            
        # If there's a session fee, update teacher's earnings
        if question.session_fee and answer.teacher and hasattr(answer.teacher, 'profile'):
            profile = answer.teacher.profile
            profile.total_earnings += float(question.session_fee)
            profile.save()
    
    @action(detail=True, methods=['post'])
    def accept_answer(self, request, pk=None):
        """Endpoint for students to accept a teacher's answer"""
        answer = self.get_object()
        
        # Only the student who asked the question can accept the answer
        if answer.question.student != request.user:
            return Response(
                {"detail": "Only the student who asked the question can accept an answer."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark the answer as accepted
        answer.is_accepted = True
        answer.save()
        
        # Close the question
        question = answer.question
        question.status = 'closed'
        question.save()
        
        return Response(
            {"detail": "Answer accepted successfully."},
            status=status.HTTP_200_OK
        )
