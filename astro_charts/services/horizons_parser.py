import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class HorizonsParser:
    """Parser for NASA Horizons API responses"""
    
    def __init__(self):
        # Regex to match the line containing coordinates and capture the declination components
        # Format: YYYY-MMM-DD HH:MM m HH MM SS.fff sDD MM SS.fff
        self.dec_pattern = re.compile(
            r'\d{4}-[A-Za-z]+-\d+\s+\d+:\d+\s+[m ]\s+\d+\s+\d+\s+[\d.]+\s+([-+]?\d+)\s+(\d+)\s+([\d.]+)',
            re.MULTILINE
        )
    
    def parse_declination(self, response: Dict[str, Any]) -> Optional[float]:
        """
        Parse declination from NASA Horizons API response
        
        Args:
            response: Raw API response dictionary
            
        Returns:
            float: Declination in decimal degrees, or None if parsing fails
        """
        try:
            data = response.get('result', '')
            print("Data: " + str(data))
            if not data:
                logger.error("Empty response data")
                return None

            match = self.dec_pattern.search(data)
            if not match:
                logger.error("Could not find declination pattern in response")
                return None

            # Extract and convert components to decimal degrees
            degrees = int(match.group(1))
            minutes = int(match.group(2))
            seconds = float(match.group(3))
            
            # Convert to decimal degrees
            dec_degrees = abs(degrees) + minutes/60.0 + seconds/3600.0
            if degrees < 0:
                dec_degrees = -dec_degrees
                
            return round(dec_degrees, 4)
            
        except Exception as e:
            logger.error(f"Error parsing Horizons response: {str(e)}")
            return None