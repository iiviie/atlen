from django.contrib import admin
from .models import LocationUpdate

@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('trip', 'user', 'latitude', 'longitude', 'timestamp')
    list_filter = ('trip', 'user', 'timestamp')
    search_fields = ('trip__title', 'user__email')
    readonly_fields = ('id', 'timestamp')
    date_hierarchy = 'timestamp'
