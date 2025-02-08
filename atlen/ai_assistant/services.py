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
        
        try:
            response = await self.model.generate_content_async(prompt)
            
            # Extract the text content and clean it
            response_text = response.text.strip()
            
            # Try to find JSON content within the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                try:
                    itinerary_data = json.loads(json_str)
                    return itinerary_data
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {json_str}")
                    return None
            else:
                print(f"No JSON found in response: {response_text}")
                return None
            
        except Exception as e:
            print(f"Error generating itinerary: {str(e)}")
            return None
            
    def _create_itinerary_prompt(self, trip_data: Dict[str, Any]) -> str:
        return f"""
        Generate a detailed day-by-day itinerary for a trip to {trip_data['location']} 
        from {trip_data['start_date']} to {trip_data['end_date']}.
        
        Consider the following:
        - Number of travelers: {len(trip_data['companions']) + 1}
        - Trip duration: {(trip_data['end_date'] - trip_data['start_date']).days} days
        - Location: {trip_data['location']}
        
        IMPORTANT: Your response must be a valid JSON object with exactly this structure:
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
                            "type": "SIGHTSEEING"
                        }}
                    ]
                }}
            ]
        }}

        Do not include any additional text before or after the JSON object.
        All time values must be in 24-hour format (HH:MM).
        All dates must be in YYYY-MM-DD format.
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