from django.contrib import admin
from .models import Activity, ActivityPhoto

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_type', 'location', 'rating', 'price_level', 'created_at')
    list_filter = ('activity_type', 'rating', 'price_level', 'created_at')
    search_fields = ('name', 'description', 'location__name', 'location__city', 'location__country', 'google_place_id')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('location',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('location')

@admin.register(ActivityPhoto)
class ActivityPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'photo_url', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('activity__name', 'photo_reference')
    readonly_fields = ('created_at',)
    raw_id_fields = ('activity',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('activity')