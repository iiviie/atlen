import google.generativeai as genai
from django.conf import settings
from typing import List, Dict, Any
import json

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GOOGLE_GEMINI_MODEL)
        
    async def generate_itinerary(self, trip_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._create_itinerary_prompt(trip_data)
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            itinerary_data = json.loads(response.text)
            return itinerary_data
        except json.JSONDecodeError:
            return None
            
    def _create_itinerary_prompt(self, trip_data: Dict[str, Any]) -> str:
        return f"""
        Generate a detailed day-by-day itinerary for a trip to {trip_data['location']} 
        from {trip_data['start_date']} to {trip_data['end_date']}.
        
        Consider the following:
        - Number of travelers: {len(trip_data['companions']) + 1}
        - Trip duration: {(trip_data['end_date'] - trip_data['start_date']).days} days
        - Location: {trip_data['location']}
        
        Please provide the response in the following JSON format:
        {{
            "days": [
                {{
                    "day": 1,
                    "date": "YYYY-MM-DD",
                    "activities": [
                        {{
                            "time": "HH:MM",
                            "activity": "Description",
                            "location": "Place name",
                            "duration": "X hours",
                            "type": "SIGHTSEEING|FOOD|TRANSPORT|REST"
                        }}
                    ]
                }}
            ]
        }}
        """
    
    async def chat_with_assistant(self, message: str, chat_history: List[Dict[str, str]]) -> str:
        formatted_history = "\n".join([
            f"User: {msg['user']}\nAssistant: {msg['assistant']}"
            for msg in chat_history[-5:] 
        ])
        
        prompt = f"""
        Previous conversation:
        {formatted_history}
        
        User: {message}
        
        You are a travel assistant. Provide helpful, concise responses about travel-related queries.
        """
        
        response = await self.model.generate_content_async(prompt)
        return response.text 