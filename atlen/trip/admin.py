from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Location, Trip, ChecklistItem, Itinerary, ItineraryItem

@admin.register(Location)
class LocationAdmin(OSMGeoAdmin):
    list_display = ('name', 'city', 'country', 'created_at')
    list_filter = ('country', 'city')
    search_fields = ('name', 'address', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'location', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date', 'created_at')
    search_fields = ('title', 'description', 'creator__email', 'location__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('creator', 'location', 'companions')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('creator', 'location')

@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'trip', 'is_checked', 'created_at')
    list_filter = ('is_checked', 'created_at')
    search_fields = ('item', 'trip__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('trip',)
    ordering = ('-created_at',)

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip', 'created_at')
    search_fields = ('title', 'trip__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('trip',)
    ordering = ('-created_at',)

@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_display = ('activity', 'time', 'itinerary', 'created_at')
    list_filter = ('time', 'created_at')
    search_fields = ('activity', 'itinerary__title', 'itinerary__trip__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('itinerary',)
    ordering = ('time',)
