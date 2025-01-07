from django.urls import path
from .views import CheckAuthView

app_name = 'accounts'

urlpatterns = [
   path('check-auth/', CheckAuthView.as_view(), name='check-auth'),
]
