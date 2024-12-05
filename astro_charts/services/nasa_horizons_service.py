import requests
import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class NASAHorizonsService:
    """Service for interacting with NASA's Horizons API"""
    
    BASE_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
    
    # Map of planet names to NASA Horizons body IDs
    BODY_IDS = {
        'moon': '301',
        'sun': '10',
        'mercury': '199',
        'venus': '299',
        'mars': '499',
        'jupiter': '599',
        'saturn': '699',
        'uranus': '799',
        'neptune': '899',
        'pluto': '999',
        'chiron': '2001'
    }
    
    def __init__(self):
        """Initialize the NASA Horizons Service"""
        logger.info("Initializing NASA Horizons Service")
    
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
            body_id = self.BODY_IDS.get(body_name.lower())
            if not body_id:
                logger.error(f"Unknown body name: {body_name}")
                return None
                
            params = self._build_query_params(body_id, date, longitude, latitude)
            response = self._make_api_request(params)
            
            if response:
                declination = self._parse_declination(response)
                logger.info(f"Got declination for {body_name} on {date}: {declination}°")
                return declination
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting declination for {body_name}: {str(e)}")
            return None
    
    def _build_query_params(self, 
                          body_id: str, 
                          date: str, 
                          longitude: float, 
                          latitude: float) -> Dict[str, str]:
        """Build query parameters for the API request"""
        return {
            'format': 'json',
            'COMMAND': f"'{body_id}'",
            'EPHEM_TYPE': "'OBSERVER'",
            'CENTER': "'coord@399'",
            'SITE_COORD': f"'{longitude},{latitude},0'",
            'START_TIME': f"'{date}'",
            'STOP_TIME': f"'{date}'",
            'STEP_SIZE': "'1d'",
            'QUANTITIES': "'1'"
        }
    
    def _make_api_request(self, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Make request to NASA Horizons API"""
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None
    
    def _parse_declination(self, response: Dict[str, Any]) -> Optional[float]:
        """Parse declination from API response"""
        try:
            result = response.get('result', '')
            
            # Pattern looks for declination in format: DD MM SS.f
            pattern = r'R\.A\._{5}\(ICRF\)_{5}DEC\n\*{46}\n\$\$SOE\n.*?(-?\d+)\s+(\d+)\s+(\d+\.\d+)'
            match = re.search(pattern, result)
            
            if match:
                degrees = float(match.group(1))
                minutes = float(match.group(2))
                seconds = float(match.group(3))
                
                # Convert to decimal degrees
                declination = degrees + (minutes/60) + (seconds/3600)
                return round(declination, 4)
                
            logger.error("Could not parse declination from response")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing declination: {str(e)}")
            return None 