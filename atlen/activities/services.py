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


    def search_nearby_places(self, latitude: float, longitude: float, radius: int = 5000, types: Optional[List[str]] = None) -> Optional[List[Dict]]:
        """Search for places near a location"""
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "*"
            }

            payload = {
                "includedTypes": types if types else ["restaurant"],
                 "maxResultCount": 10,
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": latitude, "longitude": longitude},
                        "radius": radius
                    }
                }
            }

            response = requests.post(self.nearby_url, json=payload, headers=headers)
            response.raise_for_status()

            return response.json().get("results", [])

        except Exception as e:
            logger.error(f"Error fetching nearby places: {str(e)}")
            return None

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a specific place"""
        try:
            base_url = self.details_url.format(place_id=place_id)
           
            params = {
                "key": self.api_key,
                "fields": "id,displayName,rating,websiteUri,priceLevel,photos,reviews,currentOpeningHours"
            }
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            return response.json().get('result')
        
        except requests.RequestException as e:
            logger.error(f"Error fetching place details: {str(e)}")
            return None

    def get_photo_url(self, photo_reference: str, max_width: int = 800) -> Optional[str]:
        """Get URL for a place photo"""
        try:
            params = {
                'maxwidth': max_width,
                'photo_reference': photo_reference,
                'key': self.api_key,
            }
            
            response = requests.get(self.photos_url, params=params)
            response.raise_for_status()

            return response.json().get('url')
            
        except Exception as e:
            logger.error(f"Error getting photo URL: {str(e)}")
            return None 