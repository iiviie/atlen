from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.actions import delete_selected
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)  

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email',)  

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('id', 'email', 'is_verified', 'is_registered', 'date_joined', 'is_active', 'is_staff')
    list_filter = ('is_verified', 'is_registered', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'id')
    ordering = ('-date_joined',)
    actions = ['delete_selected'] 
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Verification', {'fields': ('is_verified', 'is_registered', 'otp', 'otp_created_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        return actions 