from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'trip', 'message', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('message', 'response', 'user__email', 'trip__title')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'trip')
    ordering = ('-created_at',)

