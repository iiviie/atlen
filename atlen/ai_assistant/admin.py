from django.contrib import admin
from trip.models import Itinerary, ItineraryItem

class ItineraryItemInline(admin.TabularInline):
    model = ItineraryItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Itinerary)
class AIGeneratedItineraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip', 'created_at')
    search_fields = ('title', 'trip__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('trip',)
    ordering = ('-created_at',)
    inlines = [ItineraryItemInline]
