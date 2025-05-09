
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from users.permissions import IsAdminUser


class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(participants=user)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a new participant to a chat room"""
        room = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"detail": "User ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the user exists
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            new_participant = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Add the user to the room if not already a participant
        if new_participant not in room.participants.all():
            room.participants.add(new_participant)
        
        return Response(
            {"detail": f"{new_participant.full_name} added to the chat room."},
            status=status.HTTP_200_OK
        )


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(room__participants=user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get all unread messages for the current user"""
        user = request.user
        unread_messages = Message.objects.filter(
            room__participants=user,
            is_read=False
        ).exclude(sender=user)
        
        serializer = self.get_serializer(unread_messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a message as read"""
        message = self.get_object()
        
        # Only mark as read if the current user is a recipient
        if request.user in message.room.participants.all() and request.user != message.sender:
            message.is_read = True
            message.save()
            return Response({"detail": "Message marked as read."})
        return Response({"detail": "Cannot mark this message as read."}, status=status.HTTP_400_BAD_REQUEST)
