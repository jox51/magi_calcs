import datetime
from datetime import datetime as dt
import logging

logger = logging.getLogger(__name__)

def calculate_obliquity(t):
    """
    Calculate Earth's obliquity using IAU 2000 model
    
    Args:
        t (float): Time in Julian centuries since J2000.0
    Returns:
        float: Obliquity in degrees
    """
    # Constants from IAU 2000 model
    epsilon_0 = 84381.448  # Obliquity at J2000.0 in arcseconds
    
    # Calculate mean obliquity in arcseconds
    epsilon_A = (epsilon_0 - 
                46.84024 * t - 
                0.00059 * t**2 + 
                0.001813 * t**3)
    
    # Convert from arcseconds to degrees
    return epsilon_A / 3600.0

def julian_centuries_since_j2000(date_str):
    """
    Calculate Julian centuries since J2000.0 from date string
    
    Args:
        date_str (str): Date in format 'YYYY-MM-DD'
    Returns:
        float: Julian centuries since J2000.0
    """
    try:
        # Parse date string
        date = dt.strptime(date_str, '%Y-%m-%d')
        
        # J2000.0 epoch (noon on January 1, 2000)
        j2000 = dt(2000, 1, 1, 12, 0, 0)
        
        # Calculate difference in days
        delta = date - j2000
        
        # Convert to Julian centuries (36525 days per Julian century)
        t = delta.days / 36525.0
        
        return t
    except Exception as e:
        logger.error(f"Error calculating Julian centuries: {str(e)}")
        return 0.0

def get_ecliptic_tilt(date_str):
    """
    Calculate ecliptic tilt for a given date using IAU 2000 model
    
    Args:
        date_str (str): Date in format 'YYYY-MM-DD'
    Returns:
        float: Ecliptic tilt in degrees
    """
    try:
        # Calculate Julian centuries since J2000.0
        t = julian_centuries_since_j2000(date_str)
        
        # Calculate obliquity
        tilt = calculate_obliquity(t)
        
        logger.info(f"Calculated ecliptic tilt for {date_str}: {tilt:.6f}°")
        return tilt
        
    except Exception as e:
        logger.error(f"Error calculating ecliptic tilt: {str(e)}")
        # Fallback to mean value if calculation fails
        return 23.43929111 