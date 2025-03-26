import math
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .yogi_point_utils import ZODIAC_SIGNS
from .chart_utils import calculate_d9_chart

def calculate_bullseye_periods(natal_data: Dict[str, Any], transit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Calculate Bullseye periods - times when Saturn is within 2.5° of the D9 7th house cusp.
    
    A Bullseye period is an auspicious time for specific spiritual practices and important beginnings
    when transit Saturn aligns with the 7th house cusp in the D9 (Navamsa) chart.
    
    Args:
        natal_data: Natal chart data
        transit_data: Transit chart data
        
    Returns:
        List of dictionaries containing Bullseye period times and details
    """
    try:
        # Calculate D9 chart
        d9_chart = calculate_d9_chart(natal_data)
        print(f"D9 chart for bullseye calculation: {d9_chart}")
        
        # Check if we have the 7th house cusp in the D9 chart
        seventh_house_cusp = None
        if "houses" in d9_chart and "house_7" in d9_chart["houses"]:
            seventh_house_cusp = d9_chart["houses"]["house_7"]["d9_position"]
            print(f"Found 7th house cusp in D9 chart: {seventh_house_cusp}")
        else:
            # If 7th house cusp isn't directly available, calculate it from the Ascendant (Lagna)
            # The 7th house cusp is always 180° from the Ascendant
            if "lagna" in d9_chart and d9_chart["lagna"]:
                lagna_pos = d9_chart["lagna"]["d9_position"]
                seventh_house_cusp = (lagna_pos + 180) % 360
                print(f"Calculated 7th house cusp from lagna: {seventh_house_cusp}")
            else:
                # If neither is available, we can't calculate Bullseye periods
                print("Cannot calculate Bullseye periods - 7th house cusp information not available in the D9 chart")
                return [{
                    "error": "Cannot calculate Bullseye periods - 7th house cusp information not available in the D9 chart"
                }]
        
        # Get transit Saturn position
        saturn_pos = None
        saturn_retrograde = False
        
        # Check for Saturn in different possible locations in the transit data
        if "transit" in transit_data and "subject" in transit_data["transit"] and "planets" in transit_data["transit"]["subject"]:
            if "saturn" in transit_data["transit"]["subject"]["planets"]:
                saturn_pos = transit_data["transit"]["subject"]["planets"]["saturn"]["abs_pos"]
                saturn_retrograde = transit_data["transit"]["subject"]["planets"]["saturn"].get("retrograde", False)
                print(f"Found Saturn in transit data: {saturn_pos}")
        
        # If Saturn wasn't found in the primary location, check alternative locations
        if saturn_pos is None and "subject" in transit_data and "planets" in transit_data["subject"]:
            if "saturn" in transit_data["subject"]["planets"]:
                saturn_pos = transit_data["subject"]["planets"]["saturn"]["abs_pos"]
                saturn_retrograde = transit_data["subject"]["planets"]["saturn"].get("retrograde", False)
                print(f"Found Saturn in alternate location: {saturn_pos}")
        
        # If Saturn is still not found, we cannot calculate Bullseye periods
        if saturn_pos is None:
            print("Cannot calculate Bullseye periods - Saturn transit data not available")
            return [{
                "error": "Cannot calculate Bullseye periods - Saturn transit data not available",
                "d9_seventh_cusp": {
                    "position": round(seventh_house_cusp, 2) if seventh_house_cusp is not None else 0,
                    "sign": list(ZODIAC_SIGNS.keys())[int(seventh_house_cusp / 30)] if seventh_house_cusp is not None else "unknown",
                    "degree": round(seventh_house_cusp % 30, 2) if seventh_house_cusp is not None else 0
                }
            }]
        
        # Saturn's daily motion (slower when retrograde)
        saturn_daily_motion = 0.034 if not saturn_retrograde else 0.024
        
        # Calculate the D9 position of current transit Saturn
        from .chart_utils import calculate_d9_position
        transit_saturn_d9_pos = calculate_d9_position(saturn_pos)
        print(f"Saturn D9 position: {transit_saturn_d9_pos}")
        
        # Calculate current angular distance between transit Saturn D9 position and the 7th house cusp
        angular_distance = abs(transit_saturn_d9_pos - seventh_house_cusp) % 360
        if angular_distance > 180:
            angular_distance = 360 - angular_distance
        
        # Check if we're currently in a Bullseye period (within 2.5° orb)
        is_current_bullseye = angular_distance <= 2.5
        print(f"Current angular distance: {angular_distance}, Is current bullseye: {is_current_bullseye}")
        
        # Calculate when the next Bullseye period will occur
        # We need to find when Saturn will be at the 7th house cusp position
        # Since we're working with D9 positions, we need to find when Saturn will be at the right position
        # in the tropical zodiac that corresponds to the D9 7th house cusp
        
        # The Ascendant makes a full rotation every day, so the bullseye occurs daily
        # We need to determine at what time of day this happens
        
        now = datetime.now()
        bullseye_periods = []
        
        # Get current Ascendant position from transit data if available
        current_asc_pos = None
        if "transit" in transit_data and "subject" in transit_data["transit"] and "houses" in transit_data["transit"]["subject"] and "ascendant" in transit_data["transit"]["subject"]["houses"]:
            current_asc_pos = transit_data["transit"]["subject"]["houses"]["ascendant"]["abs_pos"]
            print(f"Found ascendant in transit data: {current_asc_pos}")
        elif "subject" in transit_data and "houses" in transit_data["subject"] and "ascendant" in transit_data["subject"]["houses"]:
            current_asc_pos = transit_data["subject"]["houses"]["ascendant"]["abs_pos"]
            print(f"Found ascendant in alternate location: {current_asc_pos}")
        else:
            # Fallback to natal Ascendant if transit Ascendant not available
            current_asc_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
            print(f"Using natal ascendant as fallback: {current_asc_pos}")
        
        # Check each hour of today and tomorrow to find when Saturn is within 2.5° of the 7th house cusp in D9
        for day_offset in range(2):  # Today and tomorrow
            check_date = now + timedelta(days=day_offset)
            
            for hour in range(24):
                # Set the time to check
                check_time = check_date.replace(hour=hour, minute=0, second=0)
                
                # Calculate approximate position of Ascendant at this time
                # Ascendant moves approximately 1° every 4 minutes, or 15° per hour
                hours_since_now = (check_time - now).total_seconds() / 3600
                
                # Calculate Ascendant position at check_time
                asc_pos_at_time = (current_asc_pos + (hours_since_now * 15)) % 360
                
                # Calculate 7th house cusp position at check_time
                seventh_cusp_at_time = (asc_pos_at_time + 180) % 360
                
                # Calculate D9 position of 7th house cusp at check_time
                d9_seventh_cusp_at_time = calculate_d9_position(seventh_cusp_at_time)
                
                # Saturn's position doesn't change much in a day, but we can calculate it for precision
                saturn_pos_at_time = (saturn_pos + (hours_since_now * saturn_daily_motion / 24)) % 360
                d9_saturn_pos_at_time = calculate_d9_position(saturn_pos_at_time)
                
                # Calculate angular distance between Saturn and 7th house cusp in D9
                angular_dist = abs(d9_saturn_pos_at_time - d9_seventh_cusp_at_time) % 360
                if angular_dist > 180:
                    angular_dist = 360 - angular_dist
                
                # If within orb, we have a Bullseye period
                if angular_dist <= 2.5:
                    # For more precision, check each 15-minute interval within this hour
                    for minute in [0, 15, 30, 45]:
                        precise_time = check_time.replace(minute=minute)
                        
                        # Recalculate with more precision
                        precise_hours_since_now = (precise_time - now).total_seconds() / 3600
                        precise_asc_pos = (current_asc_pos + (precise_hours_since_now * 15)) % 360
                        precise_seventh_cusp = (precise_asc_pos + 180) % 360
                        precise_d9_seventh_cusp = calculate_d9_position(precise_seventh_cusp)
                        
                        precise_saturn_pos = (saturn_pos + (precise_hours_since_now * saturn_daily_motion / 24)) % 360
                        precise_d9_saturn_pos = calculate_d9_position(precise_saturn_pos)
                        
                        precise_angular_dist = abs(precise_d9_saturn_pos - precise_d9_seventh_cusp) % 360
                        if precise_angular_dist > 180:
                            precise_angular_dist = 360 - precise_angular_dist
                        
                        if precise_angular_dist <= 2.5:
                            # Found a precise Bullseye time
                            d9_seventh_house_sign = list(ZODIAC_SIGNS.keys())[int(precise_d9_seventh_cusp / 30)]
                            d9_seventh_house_degree = precise_d9_seventh_cusp % 30
                            
                            d9_saturn_sign = list(ZODIAC_SIGNS.keys())[int(precise_d9_saturn_pos / 30)]
                            d9_saturn_degree = precise_d9_saturn_pos % 30
                            
                            bullseye_periods.append({
                                "time": precise_time.strftime("%Y-%m-%d %H:%M"),
                                "time_iso": precise_time.isoformat(),
                                "d9_seventh_cusp": {
                                    "position": round(precise_d9_seventh_cusp, 2),
                                    "sign": d9_seventh_house_sign,
                                    "degree": round(d9_seventh_house_degree, 2)
                                },
                                "d9_saturn": {
                                    "position": round(precise_d9_saturn_pos, 2),
                                    "sign": d9_saturn_sign,
                                    "degree": round(d9_saturn_degree, 2),
                                    "is_retrograde": saturn_retrograde
                                },
                                "angular_distance": round(precise_angular_dist, 2),
                                "is_current": (day_offset == 0 and now.hour == hour and 
                                             now.minute <= minute + 15 and now.minute >= minute)
                            })
        
        # If no Bullseye periods found in the next two days, provide an error message
        if not bullseye_periods:
            print("No Bullseye periods found in the next two days")
            
            # Calculate when the next Bullseye period will occur based on real-world dynamics
            # The key insight is that the 7th house cusp in D9 changes throughout the day as the Ascendant moves
            # This means we need to look further ahead to find when Saturn and the D9 7th house cusp will align
            
            # First get Saturn's projected position over the next few months
            # Saturn moves slowly (about 0.034° per day), so we can project forward
            
            # Looking ahead approach: Check every 5 days for the next 90 days
            lookahead_days = 90
            check_interval = 5  # Check every 5 days
            found_alignment = False
            days_to_alignment = None
            nearest_date = None
            proj_ang_dist = angular_distance  # Initialize with current angular distance
            
            # Define Saturn's motion direction
            motion_direction = -1 if saturn_retrograde else 1
            
            for day_offset in range(3, lookahead_days, check_interval):
                check_date = now + timedelta(days=day_offset)
                
                # Project Saturn's position at this future date
                projected_saturn_pos = (saturn_pos + (day_offset * saturn_daily_motion * motion_direction)) % 360
                projected_saturn_d9_pos = calculate_d9_position(projected_saturn_pos)
                
                # For each projection day, check different hours since 7th house cusp
                # cycles through zodiac every day
                for hour in [0, 6, 12, 18]:  # Check 4 times per day for efficiency
                    check_time = check_date.replace(hour=hour, minute=0, second=0)
                    
                    # Calculate projected Ascendant at this time
                    hours_since_now = (check_time - now).total_seconds() / 3600
                    projected_asc_pos = (current_asc_pos + (hours_since_now * 15)) % 360
                    
                    # Calculate projected 7th house cusp and its D9 position
                    projected_7th_cusp = (projected_asc_pos + 180) % 360
                    projected_d9_7th_cusp = calculate_d9_position(projected_7th_cusp)
                    
                    # Calculate angular distance between projected Saturn D9 and projected 7th house cusp D9
                    proj_ang_dist = abs(projected_saturn_d9_pos - projected_d9_7th_cusp) % 360
                    if proj_ang_dist > 180:
                        proj_ang_dist = 360 - proj_ang_dist
                    
                    # Check if this is a Bullseye period (within 2.5° orb)
                    if proj_ang_dist <= 2.5:
                        found_alignment = True
                        days_to_alignment = day_offset
                        nearest_date = check_time
                        
                        # Fine-tune to the nearest hour for better precision
                        for fine_hour in range(hour-2, hour+3):
                            if fine_hour < 0 or fine_hour > 23:
                                continue
                                
                            fine_time = check_date.replace(hour=fine_hour, minute=0, second=0)
                            fine_hours_since_now = (fine_time - now).total_seconds() / 3600
                            fine_asc_pos = (current_asc_pos + (fine_hours_since_now * 15)) % 360
                            fine_7th_cusp = (fine_asc_pos + 180) % 360
                            fine_d9_7th_cusp = calculate_d9_position(fine_7th_cusp)
                            
                            fine_ang_dist = abs(projected_saturn_d9_pos - fine_d9_7th_cusp) % 360
                            if fine_ang_dist > 180:
                                fine_ang_dist = 360 - fine_ang_dist
                            
                            if fine_ang_dist < proj_ang_dist:
                                proj_ang_dist = fine_ang_dist
                                nearest_date = fine_time
                        
                        break
                
                if found_alignment:
                    break
            
            # If no alignment found in lookahead period, provide an estimate based on Saturn's motion
            if not found_alignment:
                # Make sure motion_direction is defined in this path too
                if 'motion_direction' not in locals():
                    motion_direction = -1 if saturn_retrograde else 1
                    
                # Fallback method (original method)
                # For D9 patterns, the cycle repeats every 3° of regular zodiac movement
                days_to_pattern_repeat = 3 / saturn_daily_motion
                days_to_alignment = days_to_pattern_repeat * (angular_distance / 20)
                
                # Adjust for reasonable timeframes
                if days_to_alignment < 3:
                    days_to_alignment = 3
                days_to_alignment = min(days_to_alignment, 120)  # Extend to 120 days for fallback
                nearest_date = now + timedelta(days=days_to_alignment)
                
                description = f"Next potential Bullseye period estimated in approximately {round(days_to_alignment)} days based on Saturn's movement pattern. Due to the complex nature of D9 chart calculations, this is an approximate estimate."
            else:
                description = f"Next Bullseye period found in {round(days_to_alignment)} days when Saturn aligns with your D9 7th house cusp. At that time, Saturn will be at approximately {round(projected_saturn_d9_pos % 30, 1)}° {list(ZODIAC_SIGNS.keys())[int(projected_saturn_d9_pos / 30)]} in the D9 chart."
            
            # Format the response with the estimated next Bullseye period
            return [{
                "message": "No Bullseye periods found in the next two days",
                "next_estimated_bullseye": {
                    "estimated_date": nearest_date.strftime("%Y-%m-%d %H:%M"),
                    "days_away": round(days_to_alignment),
                    "description": description,
                    "projected_angular_distance": round(proj_ang_dist if found_alignment else angular_distance, 2)
                },
                "d9_seventh_cusp": {
                    "position": round(seventh_house_cusp, 2),
                    "sign": list(ZODIAC_SIGNS.keys())[int(seventh_house_cusp / 30)],
                    "degree": round(seventh_house_cusp % 30, 2)
                },
                "current_saturn_d9": {
                    "position": round(transit_saturn_d9_pos, 2),
                    "sign": list(ZODIAC_SIGNS.keys())[int(transit_saturn_d9_pos / 30)],
                    "degree": round(transit_saturn_d9_pos % 30, 2),
                    "is_retrograde": saturn_retrograde
                },
                "current_angular_distance": round(angular_distance, 2)
            }]
        
        # Sort by time
        bullseye_periods.sort(key=lambda x: x["time"])
        
        return bullseye_periods
        
    except Exception as e:
        print(f"Error in calculate_bullseye_periods: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a properly formatted error response
        return [{
            "error": f"Error calculating Bullseye periods: {str(e)}",
            "message": "Could not calculate Bullseye periods due to an error",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")  # Add a time field
        }] 