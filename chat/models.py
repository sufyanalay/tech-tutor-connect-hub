
from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    """Model for chat rooms"""
    
    ROOM_TYPES = (
        ('repair', 'Repair Discussion'),
        ('academic', 'Academic Discussion'),
        ('general', 'General Discussion'),
    )
    
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Link to repair or academic question if applicable
    repair_request = models.ForeignKey('repairs.RepairRequest', on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='chat_room')
    academic_question = models.ForeignKey('academics.AcademicQuestion', on_delete=models.SET_NULL, 
                                        null=True, blank=True, related_name='chat_room')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Message(models.Model):
    """Model for chat messages"""
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.email} in {self.room.name}"
