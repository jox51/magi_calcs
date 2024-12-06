import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class HorizonsParser:
    """Parser for NASA Horizons API responses"""
    
    def __init__(self):
        # Original pattern for natal/transit format
        self.dec_pattern1 = re.compile(
            r'\d{4}-[A-Za-z]+-\d+\s+\d+:\d+\s+\*?[A-Za-z]?\s+'  # Date and time part
            r'\d+\s+\d+\s+[\d.]+\s+'                            # RA part
            r'([-+]?\d+)\s+(\d+)\s+([\d.]+)',                   # DEC part
            re.MULTILINE
        )
        
        # New pattern for synastry format
        self.dec_pattern2 = re.compile(
            r'R\.A\._+\([\w-]+\)_+DEC\s*=\s*'           # Header part
            r'\d+\s+\d+\s+[\d.]+\s*'                    # RA part
            r'([-+]?\d+)\s+(\d+)\s+([\d.]+)',           # DEC part
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
            logger.debug(f"Parsing data: {data[:200]}...")  # Log first 200 chars for debugging
            
            if not data:
                logger.error("Empty response data")
                return None

            # Try first pattern
            match = self.dec_pattern1.search(data)
            if match:
                logger.debug("Found match with pattern 1")
            else:
                # Try second pattern if first one fails
                match = self.dec_pattern2.search(data)
                if match:
                    logger.debug("Found match with pattern 2")

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