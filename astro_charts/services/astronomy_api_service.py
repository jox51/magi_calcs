import os
import requests
import logging
from typing import Optional
from base64 import b64encode
from datetime import datetime

logger = logging.getLogger(__name__)

class AstronomyAPIService:
    """Service for interacting with the Astronomy API"""
    
    BASE_URL = "https://api.astronomyapi.com/api/v2"
    
    # Map of planet names to Astronomy API body IDs
    BODY_IDS = {
        'moon': 'moon',
        'sun': 'sun',
        'mercury': 'mercury',
        'venus': 'venus',
        'mars': 'mars',
        'jupiter': 'jupiter',
        'saturn': 'saturn',
        'uranus': 'uranus',
        'neptune': 'neptune',
        'pluto': 'pluto',
        'chiron': 'chiron'
    }
    
    def __init__(self):
        """Initialize the Astronomy API Service"""
        self.app_id = os.getenv('ASTRONOMY_APP_ID')
        self.app_secret = os.getenv('ASTRONOMY_APP_SECRET')
        
        if not self.app_id or not self.app_secret:
            raise ValueError("Missing ASTRONOMY_APP_ID or ASTRONOMY_APP_SECRET environment variables")
            
        self.auth_header = self._create_auth_header()
        logger.info("Initialized Astronomy API Service")
    
    def _create_auth_header(self) -> str:
        """Create the Authorization header for API requests"""
        credentials = f"{self.app_id}:{self.app_secret}"
        encoded = b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def get_declination(self, 
                       body_name: str, 
                       date: str, 
                       longitude: float, 
                       latitude: float) -> Optional[float]:
        """
        Get declination for a celestial body at a specific date and location
        
        Args:
            body_name (str): Name of the celestial body
            date (str): Date in YYYY-MM-DD format
            longitude (float): Observer longitude
            latitude (float): Observer latitude
            
        Returns:
            Optional[float]: Declination in degrees or None if error
        """
        try:
            # Skip API call for Chiron since it's not supported
            if body_name.lower() == 'chiron':
                logger.info(f"Skipping API call for {body_name} - not supported")
                return None
            
            body_id = self.BODY_IDS.get(body_name.lower())
            if not body_id:
                logger.error(f"Unknown body name: {body_name}")
                return None
            
            # Format date and time for API
            dt = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = dt.strftime('%Y-%m-%d')
            
            # Build request parameters
            params = {
                'longitude': longitude,
                'latitude': latitude,
                'elevation': 0,
                'from_date': formatted_date,
                'to_date': formatted_date,
                'time': '00:00:00',
                'bodies': body_id
            }
            
            # Make API request
            headers = {'Authorization': self.auth_header}
            response = requests.get(
                f"{self.BASE_URL}/bodies/positions",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Navigate through the nested structure
            if 'data' in data and 'table' in data['data']:
                for row in data['data']['table']['rows']:
                    if row['entry']['id'] == body_id:
                        for cell in row['cells']:
                            if cell['id'] == body_id:
                                declination = float(cell['position']['equatorial']['declination']['degrees'])
                                logger.info(f"Got declination for {body_name} on {date}: {declination}°")
                                return declination
            
            logger.error(f"Could not find declination for {body_name} in response")
            return None
            
        except Exception as e:
            logger.error(f"Error getting declination for {body_name}: {str(e)}")
            return None 