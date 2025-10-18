import logging
import requests
import certifi
import os
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

logger = logging.getLogger(__name__)

class SSLAdapter(HTTPAdapter):
    """Custom SSL adapter that accepts self-signed certificates"""
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

class GeoService:
    def __init__(self, username):
        if not username:
            raise ValueError("GeoNames username is required")
        self.username = username

        # Allow using HTTP for internal service communication
        # This bypasses SSL issues when services are on the same network
        use_http = os.getenv("GEOCODER_USE_HTTP", "false").lower() == "true"

        if use_http:
            self.base_url = "http://geocoder.commentking.net/geocode"
            logger.warning("Using HTTP for geocoder service (GEOCODER_USE_HTTP=true)")
        else:
            self.base_url = "https://geocoder.commentking.net/geocode"
            # Allow disabling SSL verification for trusted internal services
            self.verify_ssl = os.getenv("GEOCODER_VERIFY_SSL", "false").lower() == "true"

            if not self.verify_ssl:
                logger.warning("SSL verification disabled for geocoder service (GEOCODER_VERIFY_SSL=false)")

        logger.info(f"Initialized GeoService with username: {username[:3]}***")
        logger.info(f"Geocoder base URL: {self.base_url}")

    def get_coordinates(self, city, nation):
        """Get coordinates for a city and nation using custom geocoding API."""
        try:
            location = f"{city},{nation}"
            params = {
                'location': location
            }

            # Make request based on URL scheme
            if self.base_url.startswith("http://"):
                # HTTP - no SSL verification needed
                logger.info(f"Making HTTP request to {self.base_url}")
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
            elif hasattr(self, 'verify_ssl') and self.verify_ssl:
                # HTTPS with SSL verification
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
                # HTTPS without SSL verification (trusted internal service)
                # Use custom SSL adapter for proper TLS handshake with self-signed certs
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                logger.info(f"Making HTTPS request without SSL verification to {self.base_url}")

                session = requests.Session()
                session.mount('https://', SSLAdapter())

                response = session.get(self.base_url, params=params, timeout=10)
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