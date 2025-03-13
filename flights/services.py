from django.conf import settings
import requests
from typing import Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

class FlightSearchService:
    def __init__(self):
        self.base_url = "https://booking-com15.p.rapidapi.com/api/v1/flights"
        self.headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }

    def search_destinations(self, query: str) -> Optional[dict]:
        """Search for airports/cities"""
        try:
            url = f"{self.base_url}/searchDestination"
            response = requests.get(
                url,
                headers=self.headers,
                params={"query": query}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error searching destinations: {str(e)}")
            return None

    def search_flights(
        self,
        from_id: str,
        to_id: str,
        depart_date: date,
        return_date: Optional[date] = None,
        adults: int = 1,
        children: str = "0,17",
        cabin_class: str = "ECONOMY",
        currency_code: str = "AED",
        sort: str = "BEST",
        page_no: int = 1
    ) -> Optional[dict]:
        """Search for flights"""
        try:
            url = f"{self.base_url}/searchFlights"
            
            querystring = {
                "fromId": from_id,
                "toId": to_id,
                "departDate": depart_date.strftime("%Y-%m-%d"),
                "pageNo": str(page_no),
                "adults": str(adults),
                "children": children,
                "sort": sort,
                "cabinClass": cabin_class,
                "currency_code": currency_code
            }
            
            if return_date:
                querystring["returnDate"] = return_date.strftime("%Y-%m-%d")

            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching flights: {str(e)}")
            return None