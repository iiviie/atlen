from django.contrib import admin
from .models import FlightBooking, FlightSearch

@admin.register(FlightBooking)
class FlightBookingAdmin(admin.ModelAdmin):
    list_display = ('trip', 'from_location', 'to_location', 'departure_date', 'booking_status')
    list_filter = ('booking_status', 'departure_date', 'created_at')
    search_fields = ('trip__title', 'from_location', 'to_location')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('trip',)
    ordering = ('-departure_date',)

@admin.register(FlightSearch)
class FlightSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_location', 'to_location', 'search_date', 'created_at')
    list_filter = ('search_date', 'created_at')
    search_fields = ('user__email', 'from_location', 'to_location')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
