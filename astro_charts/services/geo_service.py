import logging
import requests
import certifi
import os

logger = logging.getLogger(__name__)

class GeoService:
    def __init__(self, username):
        if not username:
            raise ValueError("GeoNames username is required")
        self.username = username
        self.base_url = "https://geocoder.commentking.net/geocode"

        # Allow disabling SSL verification for trusted internal services
        # This is safe because geocoder.commentking.net is a service we control
        # and the SSL issue is due to Coolify/Traefik internal certificate handling
        self.verify_ssl = os.getenv("GEOCODER_VERIFY_SSL", "false").lower() == "true"

        if not self.verify_ssl:
            logger.warning("SSL verification disabled for geocoder service (GEOCODER_VERIFY_SSL=false)")

        logger.info(f"Initialized GeoService with username: {username[:3]}***")

    def get_coordinates(self, city, nation):
        """Get coordinates for a city and nation using custom geocoding API."""
        try:
            location = f"{city},{nation}"
            params = {
                'location': location
            }

            # Determine SSL verification approach
            if self.verify_ssl:
                # Try with certifi bundle first
                cert_path = certifi.where()
                logger.info(f"Using certifi bundle: {cert_path}")

                try:
                    response = requests.get(self.base_url, params=params, verify=cert_path, timeout=10)
                    response.raise_for_status()
                except requests.exceptions.SSLError as ssl_error:
                    # If certifi fails, try with system default CA bundle
                    logger.warning(f"Certifi SSL verification failed: {ssl_error}")
                    logger.info("Retrying with system default CA bundle")
                    response = requests.get(self.base_url, params=params, verify=True, timeout=10)
                    response.raise_for_status()
            else:
                # SSL verification disabled for trusted internal service
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                response = requests.get(self.base_url, params=params, verify=False, timeout=10)
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