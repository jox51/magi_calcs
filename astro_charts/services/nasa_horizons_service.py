import requests
import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from .horizons_parser import HorizonsParser


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
        'chiron': '2060'
    }
    
    def __init__(self):
        """Initialize the NASA Horizons Service"""
        logger.info("Initializing NASA Horizons Service")
        self.parser = HorizonsParser()
    
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
                declination = self.parser.parse_declination(response)

                if declination is not None:
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
        try:
            dt = datetime.strptime(date, '%Y-%m-%d')
            start_time = dt.strftime('%Y-%m-%d %H:%M')
            stop_time = (dt.replace(hour=23, minute=59)).strftime('%Y-%m-%d %H:%M')
            
            return {
                'format': 'json',
                'COMMAND': f"'{body_id}'",
                'EPHEM_TYPE': "'OBSERVER'",
                'CENTER': "'coord@399'",
                'SITE_COORD': f"'{longitude},{latitude},0'",
                'START_TIME': f"'{start_time}'",
                'STOP_TIME': f"'{stop_time}'",
                'STEP_SIZE': "'1d'",
                'QUANTITIES': "'1,2'",
                'CAL_FORMAT': "'CAL'",
                'TIME_DIGITS': "'MINUTES'",
                'ANG_FORMAT': "'HMS'",
                'EXTRA_PREC': "'YES'",
                'CSV_FORMAT': "'NO'"
            }
        except Exception as e:
            logger.error(f"Error building query parameters: {str(e)}")
            raise
    
    def _make_api_request(self, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Make request to NASA Horizons API"""
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None 