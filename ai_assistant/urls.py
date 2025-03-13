from django.urls import path
from .views import AIAssistantViewSet

app_name = 'ai_assistant'

urlpatterns = [
    path(
        'trips/<uuid:trip_pk>/ai/chat/',
        AIAssistantViewSet.as_view({'post': 'chat'}),
        name='trip-ai-chat'
    ),
    path(
        'trips/<uuid:trip_pk>/ai/generate_itinerary/',
        AIAssistantViewSet.as_view({'post': 'generate_itinerary'}),
        name='trip-ai-itinerary'
    ),
]