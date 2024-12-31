from django.contrib import admin
from .models import OTPVerification

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_type', 'is_verified', 'created_at', 'verified_at')
    list_filter = ('verification_type', 'is_verified', 'created_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'verified_at')
    ordering = ('-created_at',)