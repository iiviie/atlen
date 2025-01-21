from typing import Optional, Dict, List
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
import logging

logger = logging.getLogger(__name__)

class GooglePlacesService:
    def __init__(self):
        self.api_key = settings.GOOGLE_PLACES_API_KEY
        self.nearby_url = settings.GOOGLE_PLACES_NEARBY_URL
        self.details_url = settings.GOOGLE_PLACES_DETAILS_URL
        self.photos_url = settings.GOOGLE_PLACES_PHOTOS_URL

    def search_nearby_places(
        self,
        location: Point,
        radius: int = 5000,
        type: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """Search for places near a location"""
        try:
            params = {
                'location': f"{location.y},{location.x}",  
                'radius': radius,
                'key': self.api_key
            }
            
            if type:
                params['type'] = type
            if keyword:
                params['keyword'] = keyword

            response = requests.get(self.nearby_url, params=params)
            response.raise_for_status()
            return response.json().get('results', [])
            
        except Exception as e:
            logger.error(f"Error searching nearby places: {str(e)}")
            return None

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a specific place"""
        try:
            params = {
                'place_id': place_id,
                'key': self.api_key,
                'fields': 'name,rating,formatted_phone_number,website,price_level,photos,reviews,opening_hours'
            }

            response = requests.get(self.details_url, params=params)
            response.raise_for_status()
            return response.json().get('result')
            
        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")
            return None

    def get_photo_url(self, photo_reference: str, max_width: int = 800) -> Optional[str]:
        """Get URL for a place photo"""
        try:
            params = {
                'photoreference': photo_reference,
                'key': self.api_key,
                'maxwidth': max_width
            }

            response = requests.get(self.photos_url, params=params)
            return response.url if response.status_code == 200 else None
            
        except Exception as e:
            logger.error(f"Error getting photo URL: {str(e)}")
            return None 