from django.contrib import admin
from .models import OTPVerification
from django.contrib.admin.actions import delete_selected


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_type', 'is_verified', 'created_at', 'verified_at')
    list_filter = ('verification_type', 'is_verified', 'created_at')
    search_fields = ('user__email',)  
    readonly_fields = ('created_at', 'verified_at')
    ordering = ('-created_at',)
    actions = ['delete_selected'] 

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' not in actions:
            actions['delete_selected'] = (
                OTPVerificationAdmin.delete_selected,
                'delete_selected',
                'Delete selected OTP verifications'
            )
        return actions