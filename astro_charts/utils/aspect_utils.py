from typing import Dict, List, Any
from datetime import datetime, timedelta

# Planet daily motions with retrograde adjustments
PLANET_DAILY_MOTION = {
    'sun': 1.0,
    'moon': 13.2,
    'mercury': 1.0,
    'venus': 1.0,
    'mars': 0.5,
    'jupiter': 0.083,
    'saturn': 0.034
}

def find_closest_aspect(current_pos: float, daily_motion: float, yogi_point: float, is_retrograde: bool = False, orb: float = 3.0) -> Dict[str, Any]:
    """Find the closest aspect (conjunction, opposition, trine, sextile, square) to the Yogi Point"""
    if daily_motion == 0:
        # Cannot predict aspects if there's no motion
        return {
            "type": "stationary",
            "point": yogi_point,
            "distance": abs(current_pos - yogi_point) % 360,
            "is_applying": False,
            "estimated_date": "N/A - planet is stationary",
            "estimated_days": 0,
            "duration": {
                "days": 0,
                "start_date": "N/A",
                "exact_date": "N/A",
                "end_date": "N/A",
                "description": "Cannot calculate duration as planet is stationary"
            }
        }
        
    aspect_points = {
        'conjunction': yogi_point,
        # 'trine1': (yogi_point + 120) % 360,
        # 'trine2': (yogi_point - 120) % 360,
        # 'sextile1': (yogi_point + 60) % 360,
        # 'sextile2': (yogi_point - 60) % 360,
        # 'square1': (yogi_point + 90) % 360,
        # 'square2': (yogi_point - 90) % 360,
        'opposition': (yogi_point + 180) % 360
    }
    
    closest_aspect = None
    shortest_distance = float('inf')
    today = datetime.now()
    
    # Define absolute maximum days - 3 years (1095 days)
    MAX_DAYS_FUTURE = 1095
    
    for aspect_name, aspect_point in aspect_points.items():
        direct_diff = (aspect_point - current_pos) % 360
        retro_diff = (current_pos - aspect_point) % 360
        
        # First check if we're already within orb of an aspect
        min_diff = min(direct_diff, retro_diff)
        if min_diff <= orb:
            # We're already within orb - this is the immediate aspect
            is_direct = direct_diff <= retro_diff
            
            closest_aspect = {
                'name': aspect_name.rstrip('12'),
                'point': aspect_point,
                'distance': min_diff,
                'is_direct': is_direct
            }
            
            # Set to a small value for today's date
            days_to_aspect = 0.25  # 6 hours from now - just to indicate very soon
            shortest_distance = min_diff
            break
        
        # If not in orb, calculate days until next exact aspect
        direction = -1 if is_retrograde else 1  # Direction of motion
        
        # For direct motion, we want the shortest way to reach the aspect
        # For retrograde motion, we need to consider the opposite direction
        if is_retrograde:
            diff = retro_diff if retro_diff < direct_diff else 360 - direct_diff
        else:
            diff = direct_diff if direct_diff < retro_diff else 360 - retro_diff
            
        # Calculate days until aspect
        days_to_aspect = diff / (daily_motion * abs(direction))
        
        # Cap at maximum future days
        if days_to_aspect > MAX_DAYS_FUTURE:
            continue
            
        if days_to_aspect < shortest_distance:
            shortest_distance = days_to_aspect
            
            closest_aspect = {
                'name': aspect_name.rstrip('12'),
                'point': aspect_point,
                'distance': diff,
                'is_direct': not is_retrograde
            }
    
    if not closest_aspect:
        # No aspect found within MAX_DAYS_FUTURE
        return {
            "type": "none",
            "point": 0,
            "distance": 0,
            "estimated_date": "N/A - no aspect within 3 years",
            "estimated_days": 0,
            "duration": {
                "days": 0,
                "start_date": "N/A",
                "exact_date": "N/A",
                "end_date": "N/A",
                "description": "No aspect found within 3 years"
            }
        }
        
    # Calculate the actual date
    estimated_date = today + timedelta(days=shortest_distance)
    
    # Calculate duration of aspect (how long the planet will be within orb)
    duration_days = int((2 * orb) / daily_motion)
    
    # Calculate when aspect begins (entering orb)
    start_date = estimated_date - timedelta(days=int(orb / daily_motion))
    
    # Calculate when aspect ends (leaving orb)
    end_date = estimated_date + timedelta(days=int(orb / daily_motion))
    
    # Create response with duration information
    return {
        "type": closest_aspect['name'],
        "point": closest_aspect['point'],
        "distance": closest_aspect['distance'],
        "is_applying": closest_aspect.get('is_direct', True),
        "estimated_date": estimated_date.strftime("%Y-%m-%d %H:%M"),
        "estimated_days": int(shortest_distance),
        "duration": {
            "days": duration_days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "exact_date": estimated_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "description": f"This aspect is active for approximately {duration_days} days, from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    }

def find_last_aspect(current_pos: float, daily_motion: float, yogi_point: float, is_retrograde: bool = False, orb: float = 3.0) -> Dict[str, Any]:
    """Find the most recent aspect (conjunction, opposition) to the Yogi Point"""
    if daily_motion == 0:
        # Cannot predict aspects if there's no motion
        return {
            "type": "stationary",
            "point": yogi_point,
            "distance": abs(current_pos - yogi_point) % 360,
            "estimated_date": "N/A - planet is stationary",
            "estimated_days_ago": 0,
            "duration": {
                "days": 0,
                "start_date": "N/A",
                "exact_date": "N/A",
                "end_date": "N/A",
                "description": "Cannot calculate duration as planet is stationary"
            }
        }
        
    aspect_points = {
        'conjunction': yogi_point,
        # 'trine1': (yogi_point + 120) % 360,
        # 'trine2': (yogi_point - 120) % 360,
        # 'sextile1': (yogi_point + 60) % 360,
        # 'sextile2': (yogi_point - 60) % 360,
        # 'square1': (yogi_point + 90) % 360,
        # 'square2': (yogi_point - 90) % 360,
        'opposition': (yogi_point + 180) % 360
    }
    
    closest_aspect = None
    shortest_distance = float('inf')
    today = datetime.now()
    
    # Define absolute maximum days - 3 years (1095 days)
    MAX_DAYS_PAST = 1095
    
    for aspect_name, aspect_point in aspect_points.items():
        direct_diff = (aspect_point - current_pos) % 360
        retro_diff = (current_pos - aspect_point) % 360
        
        # First check if we're already within orb of an aspect
        min_diff = min(direct_diff, retro_diff)
        if min_diff <= orb:
            # We're already within orb - this is the immediate aspect
            is_direct = direct_diff <= retro_diff
            
            closest_aspect = {
                'name': aspect_name.rstrip('12'),
                'point': aspect_point,
                'distance': min_diff,
                'is_direct': is_direct
            }
            
            # Set to a small value for today's date
            days_ago = 0.25  # 6 hours ago - just to indicate very recent
            shortest_distance = min_diff
            break
        
        # If not in orb, calculate days since last exact aspect
        # Flip the direction compared to find_closest_aspect
        direction = 1 if is_retrograde else -1  # Inverse direction of motion to go backwards in time
        
        # For direct motion looking backward, we want to know when the planet was at the aspect point
        # coming from beyond it. For retrograde motion, we want to know when it was at the aspect point
        # coming from before it.
        if (is_retrograde and direct_diff < retro_diff) or (not is_retrograde and retro_diff < direct_diff):
            # Look backward in the opposite direction the planet is currently moving
            diff = min(direct_diff, retro_diff)
        else:
            # Look backward the long way around
            diff = 360 - min(direct_diff, retro_diff)
            
        # Calculate days ago
        days_ago = abs(diff / (daily_motion * direction))
        
        # Cap at maximum past days
        if days_ago > MAX_DAYS_PAST:
            continue
            
        if days_ago < shortest_distance:
            shortest_distance = days_ago
            
            closest_aspect = {
                'name': aspect_name.rstrip('12'),
                'point': aspect_point,
                'distance': diff
            }
            
    if not closest_aspect:
        # No aspect found within MAX_DAYS_PAST
        return {
            "type": "none",
            "point": 0,
            "distance": 0,
            "estimated_date": "N/A - no aspect within past 3 years",
            "estimated_days_ago": 0,
            "duration": {
                "days": 0,
                "start_date": "N/A",
                "exact_date": "N/A",
                "end_date": "N/A",
                "description": "No aspect found within past 3 years"
            }
        }
        
    # Calculate the actual date
    estimated_date = today - timedelta(days=shortest_distance)
    
    # Calculate duration of aspect (how long the planet was within orb)
    duration_days = int((2 * orb) / daily_motion)
    
    # Calculate when aspect began (entering orb)
    start_date = estimated_date - timedelta(days=int(orb / daily_motion))
    
    # Calculate when aspect ended (leaving orb)
    end_date = estimated_date + timedelta(days=int(orb / daily_motion))
    
    # Create response with duration information
    return {
        "type": closest_aspect['name'],
        "point": closest_aspect['point'],
        "distance": closest_aspect['distance'],
        "estimated_date": estimated_date.strftime("%Y-%m-%d %H:%M"),
        "estimated_days_ago": int(shortest_distance),
        "duration": {
            "days": duration_days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "exact_date": estimated_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "description": f"This aspect was active for approximately {duration_days} days, from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    }

def calculate_alignment_duration(exact_time: datetime, slower_planet: str = None, alignment_type: str = "conjunction", orb: float = 3.0) -> Dict[str, Any]:
    """
    Calculate the duration of an alignment based on planet motion
    
    Args:
        exact_time: The exact time of alignment
        slower_planet: The slower-moving planet in the alignment
        alignment_type: The type of alignment (e.g., conjunction)
        orb: The orb (wiggle room) in degrees
        
    Returns:
        Dictionary with duration details
    """
    # Default to jupiter as a general relatively slow planet
    planet = slower_planet or "jupiter"
    
    # Get daily motion from constants
    daily_motion = PLANET_DAILY_MOTION.get(planet.lower(), 1.0)
    
    # Calculate days to travel through the orb (both sides of exact)
    days_for_orb = orb / daily_motion
    
    # Calculate start and end dates
    start_date = exact_time - timedelta(days=days_for_orb)
    end_date = exact_time + timedelta(days=days_for_orb)
    total_days = days_for_orb * 2
    
    # Format for output
    start_str = start_date.strftime("%Y-%m-%d")
    exact_str = exact_time.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    return {
        "days": int(total_days),
        "start_date": start_str,
        "exact_date": exact_str,
        "end_date": end_str,
        "description": f"This {alignment_type} lasts approximately {int(total_days)} days, from {start_str} to {end_str}"
    } 