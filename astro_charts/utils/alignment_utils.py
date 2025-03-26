from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from .yogi_point_utils import ZODIAC_SIGNS
from .aspect_utils import PLANET_DAILY_MOTION, find_closest_aspect, calculate_alignment_duration


def find_mutual_yogi_ruler_alignments(yogi_point: float, duplicate_yogi_planet: str, duplicate_yogi_pos: float, 
                                   ascendant_pos: float, transit_data: Dict[str, Any], num_forecasts: int = 3) -> List[Dict[str, Any]]:
    """
    Calculate when the Yogi Point and its ruler (Duplicate Yogi) form a mutual aspect (conjunction or opposition)
    while one of them is aligned with the Ascendant. This is a rare and powerful alignment.
    
    Args:
        yogi_point: The absolute position of the Yogi Point (0-360°)
        duplicate_yogi_planet: The planet name of the Yogi Point ruler
        duplicate_yogi_pos: The current absolute position of the Duplicate Yogi (the ruler planet)
        ascendant_pos: The current absolute position of the Ascendant
        transit_data: The transit chart data for additional calculations 
        num_forecasts: Number of forecasts to return (default 3)
        
    Returns:
        A list of dictionaries containing information about each powerful alignment
    """
    try:
        # Get planetary motion for the duplicate yogi (ruler planet)
        daily_motion = PLANET_DAILY_MOTION.get(duplicate_yogi_planet, 1.0)
        is_retrograde = transit_data["transit"]["subject"]["planets"][duplicate_yogi_planet]["retrograde"]
        direction = -1 if is_retrograde else 1
        
        # Starting time for calculations
        now = datetime.now()
        
        # Aspects to check
        aspects = [0, 180]  # Conjunction and opposition
        
        # List to store results
        powerful_alignments = []
        
        # Calculate days until ruler aspects Yogi Point
        # This is the first condition - they must be in mutual aspect
        
        # Check each aspect (conjunction or opposition)
        for aspect in aspects:
            # Target position for the aspect
            target_pos = (yogi_point + aspect) % 360
            
            # Calculate angular distance
            angular_distance = (target_pos - duplicate_yogi_pos) % 360
            if angular_distance > 180:
                angular_distance = 360 - angular_distance
            
            # If already in aspect (within 8 degrees), skip
            if angular_distance <= 8:
                continue
            
            # Calculate days until this aspect forms
            days_to_aspect = angular_distance / (daily_motion * direction)
            if days_to_aspect < 0:
                days_to_aspect += 360 / (daily_motion * abs(direction))
            
            # Get date when aspect occurs
            aspect_date = now + timedelta(days=days_to_aspect)
            
            # For this date, calculate when ascendant aligns with either point
            # The ascendant moves through the entire zodiac every day
            aspect_pos = (duplicate_yogi_pos + (days_to_aspect * daily_motion * direction)) % 360
            
            # For each hour of this day (and the next day to be safe)
            for hour_offset in range(48):
                # Calculate current hour
                current_hour = aspect_date + timedelta(hours=hour_offset)
                
                # Ascendant position (moves ~15° per hour, full circle in 24 hours)
                hours_passed = hour_offset
                asc_pos = (ascendant_pos + (hours_passed * 15)) % 360
                
                # Check if ascendant aligns with Yogi Point
                asc_yogi_angle = (asc_pos - yogi_point) % 360
                if asc_yogi_angle > 180:
                    asc_yogi_angle = 360 - asc_yogi_angle
                
                # Check if ascendant aligns with ruler planet
                asc_ruler_angle = (asc_pos - aspect_pos) % 360
                if asc_ruler_angle > 180:
                    asc_ruler_angle = 360 - asc_ruler_angle
                
                # If either alignment is within 3°
                if asc_yogi_angle <= 3 or abs(asc_yogi_angle - 180) <= 3 or \
                   asc_ruler_angle <= 3 or abs(asc_ruler_angle - 180) <= 3:
                    
                    # Determine type of alignment
                    aspect_name = "conjunction" if aspect == 0 else "opposition" 
                    
                    alignment_type = f"Yogi Point {aspect_name} {duplicate_yogi_planet.capitalize()} with "
                    if asc_yogi_angle <= 3:
                        alignment_type += "Ascendant conjunct Yogi Point"
                    elif abs(asc_yogi_angle - 180) <= 3:
                        alignment_type += "Ascendant opposite Yogi Point"
                    elif asc_ruler_angle <= 3:
                        alignment_type += f"Ascendant conjunct {duplicate_yogi_planet.capitalize()}"
                    else:
                        alignment_type += f"Ascendant opposite {duplicate_yogi_planet.capitalize()}"
                    
                    days_away = (current_hour - now).days
                    seconds_away = (current_hour - now).seconds
                    hours_away = seconds_away // 3600
                    minutes_away = (seconds_away % 3600) // 60
                    total_minutes_away = days_away * 1440 + hours_away * 60 + minutes_away
                    
                    powerful_alignments.append({
                        "type": f"Powerful Alignment: {alignment_type}",
                        "time": current_hour.strftime("%Y-%m-%d %H:%M"),
                        "days_away": days_away,
                        "hours_away": hours_away,
                        "minutes_away": total_minutes_away,
                        "formatted_time": current_hour.strftime("%Y-%m-%d %H:%M"),
                        "time_iso": current_hour.isoformat(),
                        "power_level": "Extremely Powerful",
                        "aspect_degree": aspect
                    })
                    
                    # Once we find an alignment for this hour, move to next hour
                    break
        
        # Sort alignments by time and limit to requested number
        powerful_alignments.sort(key=lambda x: x["minutes_away"])
        
        return powerful_alignments[:num_forecasts]
    
    except Exception as e:
        print(f"Error in find_mutual_yogi_ruler_alignments: {str(e)}")
        return []


def find_yearly_power_alignments(yogi_point: float, duplicate_yogi_planet: str, 
                             duplicate_yogi_pos: float, is_retrograde: bool,
                             ascendant_pos: float, orb: float = 3.0) -> List[Dict[str, Any]]:
    """
    Find dates when the Yogi Point and its ruler (Duplicate Yogi) form a mutual aspect (conjunction or opposition)
    while also being aligned with the Ascendant.
    
    This rare and powerful configuration occurs approximately once per year.
    
    Args:
        yogi_point: The absolute position of the Yogi Point (0-360°)
        duplicate_yogi_planet: The planet name of the Yogi Point ruler
        duplicate_yogi_pos: The current absolute position of the Duplicate Yogi (the ruler planet)
        is_retrograde: Whether the duplicate yogi planet is retrograde
        ascendant_pos: The current absolute position of the Ascendant
        orb: The orb to use for calculations (default: 3.0°)
        
    Returns:
        A list of dictionaries containing information about each powerful alignment
    """
    try:
        # Validate inputs
        if not isinstance(yogi_point, (int, float)) or not isinstance(duplicate_yogi_pos, (int, float)) or not isinstance(ascendant_pos, (int, float)):
            print(f"Warning: Invalid parameters in find_yearly_power_alignments: yogi_point={yogi_point}, duplicate_yogi_pos={duplicate_yogi_pos}, ascendant_pos={ascendant_pos}")
            # Convert to float or use defaults for invalid inputs
            yogi_point = float(yogi_point) if isinstance(yogi_point, (int, float)) else 0.0
            duplicate_yogi_pos = float(duplicate_yogi_pos) if isinstance(duplicate_yogi_pos, (int, float)) else 0.0
            ascendant_pos = float(ascendant_pos) if isinstance(ascendant_pos, (int, float)) else 0.0
        
        alignments = []
        now = datetime.now()
        
        # If duplicate_yogi_planet is missing or invalid, default to Venus (most common ruler of Libra/Taurus)
        if not duplicate_yogi_planet or not isinstance(duplicate_yogi_planet, str):
            duplicate_yogi_planet = "venus"
            print(f"Warning: Invalid duplicate_yogi_planet in find_yearly_power_alignments, defaulting to {duplicate_yogi_planet}")
        
        # Get daily motion of the ruler planet
        daily_motion = PLANET_DAILY_MOTION.get(duplicate_yogi_planet, 1.0)
        motion_direction = -1 if is_retrograde else 1
        
        # Calculate the timeframe when the ruler planet will aspect the Yogi Point
        angle = abs(yogi_point - duplicate_yogi_pos) % 360
        if angle > 180:
            angle = 360 - angle
            
        # If already in aspect (conjunction or opposition), look for next aspect
        if angle < 5 or abs(angle - 180) < 5:
            # Already in aspect - estimate when Ascendant will align
            if angle < 5:  # Conjunction
                aspect_type = "conjunction"
            else:  # Opposition
                aspect_type = "opposition"
                
            # Find next time Ascendant aligns with them (happens once per day)
            # Calculate hours until Ascendant aligns with Yogi Point
            degrees_to_yogi = (yogi_point - ascendant_pos) % 360
            hours_to_yogi = degrees_to_yogi / 15  # Ascendant moves ~15° per hour
            
            yogi_alignment_time = now + timedelta(hours=hours_to_yogi)
            
            # Calculate the duration of this alignment
            alignment_duration = calculate_alignment_duration(
                exact_time=yogi_alignment_time,
                slower_planet=duplicate_yogi_planet,
                alignment_type=f"Yearly Power Alignment: Yogi Point {aspect_type} {duplicate_yogi_planet.capitalize()}",
                orb=orb
            )
            
            alignments.append({
                "type": f"Powerful Alignment: Yogi Point {aspect_type} {duplicate_yogi_planet.capitalize()} with Ascendant conjunct Yogi Point",
                "time": yogi_alignment_time.strftime("%Y-%m-%d %H:%M"),
                "days_away": int(hours_to_yogi / 24),
                "formatted_time": yogi_alignment_time.strftime("%Y-%m-%d %H:%M"),
                "time_iso": yogi_alignment_time.isoformat(),
                "power_level": "Extremely Powerful - Occurs Today",
                "duration": alignment_duration
            })
            
            # Also check alignment with ruler planet
            degrees_to_ruler = (duplicate_yogi_pos - ascendant_pos) % 360
            hours_to_ruler = degrees_to_ruler / 15
            
            ruler_alignment_time = now + timedelta(hours=hours_to_ruler)
            
            # Calculate the duration of this alignment
            ruler_alignment_duration = calculate_alignment_duration(
                exact_time=ruler_alignment_time,
                slower_planet=duplicate_yogi_planet,
                alignment_type=f"Yearly Power Alignment: Ascendant conjunct {duplicate_yogi_planet.capitalize()}",
                orb=orb
            )
            
            alignments.append({
                "type": f"Powerful Alignment: Yogi Point {aspect_type} {duplicate_yogi_planet.capitalize()} with Ascendant conjunct {duplicate_yogi_planet.capitalize()}",
                "time": ruler_alignment_time.strftime("%Y-%m-%d %H:%M"),
                "days_away": int(hours_to_ruler / 24),
                "formatted_time": ruler_alignment_time.strftime("%Y-%m-%d %H:%M"),
                "time_iso": ruler_alignment_time.isoformat(),
                "power_level": "Extremely Powerful - Occurs Today",
                "duration": ruler_alignment_duration
            })
            
        else:
            # Not currently in aspect - calculate next conjunction and opposition
            # First the conjunction
            conj_diff = angle
            days_to_conj = conj_diff / (daily_motion * abs(motion_direction))
            
            # Then the opposition
            opp_diff = abs(180 - angle)
            days_to_opp = opp_diff / (daily_motion * abs(motion_direction))
            
            # Determine which comes first
            if days_to_conj < days_to_opp:
                aspect_type = "conjunction"
                days_to_aspect = days_to_conj
            else:
                aspect_type = "opposition"
                days_to_aspect = days_to_opp
            
            # Cap days to aspect at a reasonable value based on planet speed
            if daily_motion >= 0.5:  # Mars or faster
                days_to_aspect = min(days_to_aspect, 120)  # Cap at 4 months
            elif daily_motion >= 0.08:  # Jupiter
                days_to_aspect = min(days_to_aspect, 180)  # Cap at 6 months
            else:  # Saturn or slower
                days_to_aspect = min(days_to_aspect, 365)  # Cap at 1 year
            
            # Calculate position of the ruler when aspect occurs
            aspect_date = now + timedelta(days=days_to_aspect)
            
            # Calculate when the Ascendant will align with either point
            # Look at each hour of that day
            alignments_found = False
            for hour in range(24):
                try:
                    aspect_time = aspect_date.replace(hour=hour, minute=0, second=0)
                    
                    # Position of Ascendant at this hour
                    # Ascendant moves through all 360° in a day (15° per hour)
                    hours_since_now = (aspect_time - now).total_seconds() / 3600
                    asc_pos_at_time = (ascendant_pos + (hours_since_now * 15)) % 360
                    
                    # Check if Ascendant is aligned with Yogi Point or ruler
                    yogi_angle = abs(asc_pos_at_time - yogi_point) % 360
                    if yogi_angle > 180:
                        yogi_angle = 360 - yogi_angle
                        
                    ruler_pos_at_time = (duplicate_yogi_pos + (days_to_aspect * daily_motion * motion_direction)) % 360
                    ruler_angle = abs(asc_pos_at_time - ruler_pos_at_time) % 360
                    if ruler_angle > 180:
                        ruler_angle = 360 - ruler_angle
                    
                    # If Ascendant is within orb of either point
                    if yogi_angle <= orb or ruler_angle <= orb:
                        alignment_type = ""
                        if yogi_angle <= orb:
                            alignment_type = f"Powerful Alignment: Yogi Point {aspect_type} {duplicate_yogi_planet.capitalize()} with Ascendant conjunct Yogi Point"
                            
                            # Calculate duration for this alignment
                            alignment_duration = calculate_alignment_duration(
                                exact_time=aspect_time,
                                slower_planet=duplicate_yogi_planet,
                                alignment_type="Yearly Power Alignment",
                                orb=orb
                            )
                        else:
                            alignment_type = f"Powerful Alignment: Yogi Point {aspect_type} {duplicate_yogi_planet.capitalize()} with Ascendant conjunct {duplicate_yogi_planet.capitalize()}"
                            
                            # Calculate duration for this alignment
                            alignment_duration = calculate_alignment_duration(
                                exact_time=aspect_time,
                                slower_planet=duplicate_yogi_planet,
                                alignment_type="Yearly Power Alignment",
                                orb=orb
                            )
                        
                        alignments.append({
                            "type": alignment_type,
                            "time": aspect_time.strftime("%Y-%m-%d %H:%M"),
                            "days_away": int(days_to_aspect),
                            "formatted_time": aspect_time.strftime("%Y-%m-%d %H:%M"),
                            "time_iso": aspect_time.isoformat(),
                            "power_level": "Extremely Powerful - Once Yearly Event",
                            "duration": alignment_duration
                        })
                        alignments_found = True
                        break
                except Exception as e:
                    print(f"Error in hour calculation {hour}: {str(e)}")
                    continue
            
            # If no alignments found through hourly calculation, add a default one
            if not alignments_found:
                default_aspect_time = aspect_date.replace(hour=12, minute=0)
                
                # Calculate a default duration
                default_duration = calculate_alignment_duration(
                    exact_time=default_aspect_time,
                    slower_planet=duplicate_yogi_planet,
                    alignment_type="Yearly Power Alignment (Approximate)",
                    orb=orb
                )
                
                alignments.append({
                    "type": f"Powerful Alignment: Yogi Point {aspect_type} {duplicate_yogi_planet.capitalize()} (approximate)",
                    "time": default_aspect_time.strftime("%Y-%m-%d %H:%M"),
                    "days_away": int(days_to_aspect),
                    "formatted_time": default_aspect_time.strftime("%Y-%m-%d %H:%M"),
                    "time_iso": default_aspect_time.isoformat(),
                    "power_level": "Powerful - Approximate Time",
                    "duration": default_duration
                })
        
        return sorted(alignments, key=lambda x: x["days_away"])
    
    except Exception as e:
        print(f"Error in find_yearly_power_alignments: {str(e)}")
        # Return at least one alignment as a fallback
        fallback_date = datetime.now() + timedelta(days=30)  # Fallback to 30 days from now
        
        # Create a fallback duration
        fallback_duration = calculate_alignment_duration(
            exact_time=fallback_date.replace(hour=12, minute=0),
            slower_planet=duplicate_yogi_planet if isinstance(duplicate_yogi_planet, str) else "venus",
            alignment_type="Yearly Power Alignment (Estimated)",
            orb=orb
        )
        
        return [{
            "type": f"Powerful Alignment: Yogi Point - {duplicate_yogi_planet.capitalize() if isinstance(duplicate_yogi_planet, str) else 'Venus'} (estimated)",
            "time": fallback_date.strftime("%Y-%m-%d %H:%M"),
            "days_away": 30,
            "formatted_time": fallback_date.strftime("%Y-%m-%d %H:%M"),
            "time_iso": fallback_date.replace(hour=12, minute=0).isoformat(),
            "power_level": "Powerful - Estimated Time",
            "note": f"Error in calculation: {str(e)}",
            "duration": fallback_duration
        }] 