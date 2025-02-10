from django.contrib import admin
from .models import Document, TripDocument

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'document_type', 'expiry_date', 'created_at')
    list_filter = ('document_type', 'created_at', 'expiry_date')
    search_fields = ('title', 'user__email', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)
    ordering = ('document_type', '-created_at')

@admin.register(TripDocument)
class TripDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip', 'document_type', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('title', 'trip__title', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('trip',)
    ordering = ('document_type', '-created_at')
