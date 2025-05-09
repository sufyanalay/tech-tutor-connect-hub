
from django.contrib import admin
from .models import ChatRoom, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0

class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'created_at')
    list_filter = ('room_type', 'created_at')
    inlines = [MessageInline]
    search_fields = ('name', 'participants__email')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'room', 'timestamp')
    list_filter = ('timestamp', 'room')
    search_fields = ('content', 'sender__email', 'room__name')

admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(Message, MessageAdmin)
