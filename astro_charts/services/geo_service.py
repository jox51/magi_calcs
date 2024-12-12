import logging
import requests

logger = logging.getLogger(__name__)

class GeoService:
    def __init__(self, username):
        if not username:
            raise ValueError("GeoNames username is required")
        self.username = username
        self.base_url = "https://geocoderdocked.commentking.net/geocode"
        logger.info(f"Initialized GeoService with username: {username[:3]}***")

    def get_coordinates(self, city, nation):
        """Get coordinates for a city and nation using custom geocoding API."""
        try:
            location = f"{city},{nation}"
            params = {
                'location': location
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0 and len(data[0]) > 0:
                location = data[0][0]
                lat = float(location['latitude'])
                lng = float(location['longitude'])
                logger.info(f"Found coordinates for {city}, {nation}: ({lat}, {lng})")
                return lat, lng
            else:
                logger.error(f"Could not find coordinates for {city}, {nation}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting coordinates for {city}, {nation}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting coordinates for {city}, {nation}: {str(e)}")
            return None 