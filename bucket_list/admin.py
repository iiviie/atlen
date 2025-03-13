from django.contrib import admin
from .models import BucketListItem

@admin.register(BucketListItem)
class BucketListItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'location', 'priority', 'status', 'target_date', 'completed_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('title', 'user__email', 'location__name')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    raw_id_fields = ('user', 'location', 'associated_trip')
    ordering = ('priority', '-created_at')
