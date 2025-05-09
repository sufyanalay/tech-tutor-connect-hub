
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserBasicSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(),
        write_only=True,
        source='participants'
    )
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'participants', 'participant_ids', 'room_type', 
                 'repair_request', 'academic_question', 'created_at']
        read_only_fields = ['created_at']
    
    def validate(self, attrs):
        """Ensure at least 2 participants in the chat room"""
        participants = attrs.get('participants', [])
        if len(participants) < 2:
            raise serializers.ValidationError("A chat room must have at least 2 participants.")
        return attrs
    
    def create(self, validated_data):
        participants = validated_data.pop('participants', [])
        room = ChatRoom.objects.create(**validated_data)
        
        # Ensure the current user is a participant
        current_user = self.context['request'].user
        if current_user not in participants:
            participants.append(current_user)
        
        room.participants.set(participants)
        return room


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.full_name')
    sender_role = serializers.ReadOnlyField(source='sender.role')
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'sender_name', 'sender_role', 
                 'content', 'attachment', 'is_read', 'timestamp']
        read_only_fields = ['sender', 'timestamp']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)
