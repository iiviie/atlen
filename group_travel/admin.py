from django.contrib import admin
from .models import GroupChat, Message, Bill, BillSplit

@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('trip', 'created_at')
    search_fields = ('trip__title',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('trip',)
    ordering = ('-created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'sender__email', 'chat__trip__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('chat', 'sender')
    ordering = ('-created_at',)

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip', 'amount', 'currency', 'paid_by', 'created_at')
    list_filter = ('currency', 'created_at')
    search_fields = ('title', 'trip__title', 'paid_by__email')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('trip', 'paid_by')
    ordering = ('-created_at',)

@admin.register(BillSplit)
class BillSplitAdmin(admin.ModelAdmin):
    list_display = ('bill', 'user', 'amount', 'is_paid', 'paid_at')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('bill__title', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('bill', 'user')
    ordering = ('-created_at',)
