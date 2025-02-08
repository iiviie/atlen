from typing import Optional, Dict, List
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
import logging

logger = logging.getLogger(__name__)


class HotelServices:
    def __init__(self):
        self.base_url = settings.HOTEL_BOOKING_BASE_URL
        self.headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": "booking-com15.p.rapidapi.com",
        }

    def search_hotels(self, query: str) -> Optional[dict]:
        """
        Fetch hotel data from Booking.com API based on a search query.
        """
        url = f"{self.base_url}/searchDestination"
        params = {"query": query}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error searching destinations: {str(e)}")
            return None

    def get_hotel_details(
        self, hotel_id: str, arrival_date: str, departure_date: str
    ) -> Optional[dict]:
        """
        Fetch hotel details from Booking.com API with required parameters.
        """
        url = f"{self.base_url}/getHotelDetails"

        params = {
            "hotel_id": hotel_id,
            "arrival_date": arrival_date,
            "departure_date": departure_date,
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error fetching hotel details: {str(e)}")
            return None

    def search_available_hotels(
        self,
        dest_id: str,
        adults: int,
        children_age: Optional[List[int]],
        arrival_date: str,
        departure_date: str,
    ) -> Optional[dict]:
        """Fetch hotels from Booking.com API."""
        url = f"{self.base_url}/searchHotels"
        params = {
            "dest_id": dest_id,
            "search_type": "CITY",
            "adults": adults,
            "children_age": ",".join(map(str, children_age)) if children_age else "0",
            "arrival_date": arrival_date,
            "departure_date": departure_date,
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching hotel data: {e}")
            return None
