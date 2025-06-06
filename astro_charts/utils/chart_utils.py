from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from datetime import timedelta
from .yogi_point_utils import ZODIAC_SIGNS

def sanitize_response_for_json(response: Dict[str, Any]) -> Dict[str, Any]:
    """Convert any datetime objects to strings and ensure the response is JSON serializable
    
    Args:
        response: The dictionary to sanitize
        
    Returns:
        JSON serializable dictionary
    """
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetime(item) for item in obj]
        else:
            return obj
            
    return convert_datetime(response)

def calculate_d9_chart(natal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate navamsa (D9) chart positions from the natal chart
    
    Args:
        natal_data: The natal chart data dictionary
        
    Returns:
        Dictionary containing D9 chart positions
    """
    d9_chart = {
        "planets": {},
        "houses": {}
    }
    
    # Calculate D9 positions for planets
    for planet_name, planet_data in natal_data["subject"]["planets"].items():
        # Get absolute position
        abs_pos = planet_data.get("abs_pos", 0)
        
        # Calculate D9 position
        d9_pos = calculate_d9_position(abs_pos)
        
        # Add to D9 chart
        d9_chart["planets"][planet_name] = {
            "natal_pos": abs_pos,
            "d9_pos": d9_pos,
            "d9_sign_num": int(d9_pos / 30),
            "d9_sign": list(ZODIAC_SIGNS.keys())[int(d9_pos / 30)],
            "d9_degree": d9_pos % 30,
            "retrograde": planet_data.get("retrograde", False)
        }
    
    # Calculate D9 positions for houses if available
    if "houses" in natal_data["subject"]:
        for house_name, house_data in natal_data["subject"]["houses"].items():
            if "abs_pos" in house_data:
                abs_pos = house_data["abs_pos"]
                
                # Calculate D9 position
                d9_pos = calculate_d9_position(abs_pos)
                
                # Add to D9 chart
                d9_chart["houses"][house_name] = {
                    "natal_pos": abs_pos,
                    "d9_pos": d9_pos,
                    "d9_sign_num": int(d9_pos / 30),
                    "d9_sign": list(ZODIAC_SIGNS.keys())[int(d9_pos / 30)],
                    "d9_degree": d9_pos % 30
                }
    
    return d9_chart

def calculate_d9_position(zodiac_position: float) -> float:
    """
    Calculate navamsa (D9) position from zodiacal position
    
    Args:
        zodiac_position: Position in degrees (0-360)
        
    Returns:
        D9 position in degrees (0-360)
    """
    sign = int(zodiac_position / 30)
    degree_in_sign = zodiac_position % 30
    
    # Calculate navamsa (3.33 degrees per division)
    navamsa = int(degree_in_sign / 3.33333)
    
    # Calculate D9 position based on starting sign and navamsa
    if sign % 3 == 0:  # Fire signs (Aries, Leo, Sagittarius)
        d9_sign = (navamsa + 0) % 12
    elif sign % 3 == 1:  # Earth signs (Taurus, Virgo, Capricorn)
        d9_sign = (navamsa + 8) % 12
    else:  # Air and Water signs (Gemini, Libra, Aquarius, Cancer, Scorpio, Pisces)
        d9_sign = (navamsa + 4) % 12
    
    # Return the D9 position in degrees
    return d9_sign * 30 + (degree_in_sign % 3.33333) * 9

# Zodiac signs mapping - needed for D9 calculations
def find_stacked_alignments(all_dates_list: List[Dict[str, Any]], 
                     pof_rahu_data: List[Dict[str, Any]] = None,
                     pof_regulus_data: List[Dict[str, Any]] = None,
                     pof_lord_lagna_data: List[Dict[str, Any]] = None,
                     time_window_hours: int = 12) -> List[Dict[str, Any]]:
    """
    Find dates with multiple astrological alignments occurring within a short time window
    
    Args:
        all_dates_list: List of all alignment dates to check
        pof_rahu_data: Optional list of Part of Fortune - Rahu alignment dates
        pof_regulus_data: Optional list of Part of Fortune - Regulus alignment dates
        pof_lord_lagna_data: Optional list of Part of Fortune - Lord Lagna alignment dates
        time_window_hours: Time window in hours to consider alignments as "stacked"
        
    Returns:
        List of stacked alignment dates
    """
    # If no dates provided, return empty list
    if not all_dates_list:
        return []
    
    # Convert all date strings to datetime objects for comparison
    date_objects = []
    
    # Process main dates list
    for date_item in all_dates_list:
        if "date" in date_item and date_item["date"]:
            try:
                date_obj = datetime.strptime(date_item["date"], "%Y-%m-%d %H:%M")
                date_objects.append({
                    "date_obj": date_obj,
                    "type": date_item.get("type", "Unknown Alignment"),
                    "original_data": date_item
                })
            except ValueError:
                # Skip dates that can't be parsed
                continue
    
    # Add optional POF-Rahu dates if provided
    if pof_rahu_data:
        for item in pof_rahu_data:
            if "date" in item and item["date"]:
                try:
                    date_obj = datetime.strptime(item["date"], "%Y-%m-%d %H:%M")
                    date_objects.append({
                        "date_obj": date_obj,
                        "type": "POF-Rahu Conjunction",
                        "original_data": item
                    })
                except ValueError:
                    continue
    
    # Add optional POF-Regulus dates if provided
    if pof_regulus_data:
        for item in pof_regulus_data:
            if "date" in item and item["date"]:
                try:
                    date_obj = datetime.strptime(item["date"], "%Y-%m-%d %H:%M")
                    date_objects.append({
                        "date_obj": date_obj,
                        "type": "POF-Regulus Conjunction",
                        "original_data": item
                    })
                except ValueError:
                    continue
    
    # Add optional POF-Lord Lagna dates if provided
    if pof_lord_lagna_data:
        for item in pof_lord_lagna_data:
            if "date" in item and item["date"]:
                try:
                    date_obj = datetime.strptime(item["date"], "%Y-%m-%d %H:%M")
                    date_objects.append({
                        "date_obj": date_obj,
                        "type": "POF-Lord Lagna Conjunction",
                        "original_data": item
                    })
                except ValueError:
                    continue
    
    # Sort all dates chronologically
    date_objects.sort(key=lambda x: x["date_obj"])
    
    # Find stacked dates (dates close together)
    stacked_dates = []
    time_window = timedelta(hours=time_window_hours)
    
    # Start with the earliest date and find all dates within the time window
    i = 0
    while i < len(date_objects):
        current_date = date_objects[i]["date_obj"]
        
        # Find all dates within the time window of the current date
        stack = []
        for j in range(len(date_objects)):
            if abs((date_objects[j]["date_obj"] - current_date).total_seconds()) <= time_window.total_seconds():
                stack.append(date_objects[j])
        
        # If we found multiple dates in the stack
        if len(stack) >= 2:
            # Create a stacked date entry
            stacked_entry = {
                "primary_date": current_date.strftime("%Y-%m-%d %H:%M"),
                "alignments": [item["type"] for item in stack],
                "count": len(stack),
                "power_level": f"Very Powerful ({len(stack)} alignments)",
                "original_data": [item["original_data"] for item in stack]
            }
            
            # Add to results if not duplicate
            if not any(entry["primary_date"] == stacked_entry["primary_date"] for entry in stacked_dates):
                stacked_dates.append(stacked_entry)
        
        # Move to the next date outside the current time window
        next_i = i + 1
        while next_i < len(date_objects) and abs((date_objects[next_i]["date_obj"] - current_date).total_seconds()) <= time_window.total_seconds():
            next_i += 1
        
        if next_i == i + 1:
            i += 1
        else:
            i = next_i
    
    # Sort stacked dates by count (most alignments first)
    stacked_dates.sort(key=lambda x: x["count"], reverse=True)
    
    return stacked_dates

def find_internally_stacked_dates(all_dates_list: List[Dict[str, Any]], 
                          exclude_same_type: bool = True) -> List[Dict[str, Any]]:
    """
    Find dates with multiple alignments of different types occurring within a short time window
    
    Args:
        all_dates_list: List of all alignment dates to check
        exclude_same_type: Whether to exclude stacking of the same alignment type
        
    Returns:
        List of stacked alignment dates
    """
    # If no dates provided, return empty list
    if not all_dates_list:
        return []
    
    # Convert all date strings to datetime objects for comparison
    date_objects = []
    
    # Process dates list
    for date_item in all_dates_list:
        if "date" in date_item and date_item["date"]:
            try:
                date_obj = datetime.strptime(date_item["date"], "%Y-%m-%d %H:%M")
                date_objects.append({
                    "date_obj": date_obj,
                    "type": date_item.get("type", "Unknown Alignment"),
                    "power": date_item.get("power_level", "Normal"),
                    "original_data": date_item
                })
            except ValueError:
                # Skip dates that can't be parsed
                continue
    
    # Sort all dates chronologically
    date_objects.sort(key=lambda x: x["date_obj"])
    
    # Find stacked dates (dates close together)
    stacked_dates = []
    time_window = timedelta(hours=12)  # 12-hour window
    
    # Start with the earliest date and find all dates within the time window
    i = 0
    while i < len(date_objects):
        current_date = date_objects[i]["date_obj"]
        
        # Find all dates within the time window of the current date
        stack = []
        for j in range(len(date_objects)):
            if abs((date_objects[j]["date_obj"] - current_date).total_seconds()) <= time_window.total_seconds():
                # If we're excluding same type alignments, check if this is a different type
                if not exclude_same_type or date_objects[j]["type"] != date_objects[i]["type"]:
                    stack.append(date_objects[j])
        
        # If we found multiple dates in the stack
        if len(stack) >= 2:
            # Create a stacked date entry
            stacked_entry = {
                "primary_date": current_date.strftime("%Y-%m-%d %H:%M"),
                "alignments": [item["type"] for item in stack],
                "count": len(stack),
                "power_level": f"Very Powerful ({len(stack)} alignments)",
                "original_data": [item["original_data"] for item in stack]
            }
            
            # Add to results if not duplicate
            if not any(entry["primary_date"] == stacked_entry["primary_date"] for entry in stacked_dates):
                stacked_dates.append(stacked_entry)
        
        # Move to the next date
        i += 1
    
    # Sort stacked dates by count (most alignments first)
    stacked_dates.sort(key=lambda x: x["count"], reverse=True)
    
    return stacked_dates


def get_nearest_future_date(dates_array: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Get the nearest future date from a list of date entries
    
    Args:
        dates_array: List of date entries with 'date' field
        
    Returns:
        The nearest future date entry or None if no future dates
    """
    if not dates_array:
        return None
    
    now = datetime.now()
    future_dates = []
    
    for date_entry in dates_array:
        if "date" in date_entry:
            try:
                date_obj = datetime.strptime(date_entry["date"], "%Y-%m-%d %H:%M")
                if date_obj > now:
                    future_dates.append({
                        "date_obj": date_obj,
                        "entry": date_entry
                    })
            except (ValueError, TypeError):
                continue
    
    if not future_dates:
        return None
    
    # Sort by nearest future date
    future_dates.sort(key=lambda x: x["date_obj"])
    
    return future_dates[0]["entry"] 


def determine_day_night_chart(self, sun_pos: float, asc_pos: float, natal_data: Dict[str, Any] = None, 
                            label: str = "") -> bool:
        """
        Determine if a chart is a day chart (Sun above horizon) or night chart (Sun below horizon).
        
        Args:
            sun_pos: The Sun's absolute position in degrees (0-360)
            asc_pos: The Ascendant's absolute position in degrees (0-360)
            natal_data: Optional natal chart data with additional information
            label: Optional label for logging (useful when determining day/night for multiple charts)
        
        Returns:
            is_night_chart: True if it's a night chart, False if it's a day chart
        """
        prefix = f"[{label}] " if label else ""
        is_night_chart = False
        sun_house_determined = False
        
        # Method 1: Try to get Sun's house directly from the data if available
        if natal_data is not None and "subject" in natal_data and "planets" in natal_data["subject"] and "sun" in natal_data["subject"]["planets"]:
            sun_data = natal_data["subject"]["planets"]["sun"]
            if "house" in sun_data:
                try:
                    sun_house = sun_data["house"]
                    sun_house_num = int(sun_house.replace("house_", ""))
                    # Houses 1-6 are below horizon (night), 7-12 are above horizon (day)
                    is_night_chart = 1 <= sun_house_num <= 6
                    sun_house_determined = True
                    print(f"{prefix}Determined day/night status directly from Sun's house: {sun_house} (Night: {is_night_chart})")
                except (ValueError, AttributeError):
                    # If house isn't in expected format, fall through to method 2
                    pass
        
        # Method 2: Calculate Sun's house from scratch if Method 1 failed
        if not sun_house_determined:
            # Normalize positions to 0-360°
            sun_pos_norm = sun_pos % 360
            asc_pos_norm = asc_pos % 360
            
            # Calculate the angle from Ascendant to Sun (counterclockwise)
            angle_from_asc = (sun_pos_norm - asc_pos_norm) % 360
            
            # Determine the house (each house spans 30° in equal house system)
            sun_house_num = int(angle_from_asc / 30) + 1  # +1 because houses are 1-indexed
            
            # Houses 1-6 are below horizon (night), 7-12 are above horizon (day)
            is_night_chart = 1 <= sun_house_num <= 6
            print(f"{prefix}Calculated Sun's house position: {sun_house_num} (Night: {is_night_chart})")
            
            # Method 3: Validate with birth time if available (sanity check)
            if natal_data is not None and "subject" in natal_data and "date_utc" in natal_data["subject"]:
                try:
                    birth_time_str = natal_data["subject"]["date_utc"].split('T')[1]
                    birth_hour = int(birth_time_str.split(':')[0])
                    
                    # Basic sanity check: if birth hour is between 6 AM and 6 PM, it's likely a day chart
                    is_likely_day = 6 <= birth_hour < 18
                    
                    if is_likely_day == is_night_chart:
                        print(f"{prefix}WARNING: Calculated day/night status conflicts with birth hour {birth_hour}. " +
                            f"Birth hour suggests {'day' if is_likely_day else 'night'} but calculation shows {'night' if is_night_chart else 'day'}")
                except Exception as e:
                    print(f"{prefix}Could not validate day/night status against birth time: {str(e)}")
        
        # Log the final determination
        print(f"{prefix}Chart determined to be a {'night' if is_night_chart else 'day'} chart. " +
            f"Part of Fortune formula: {'Asc - Moon + Sun' if is_night_chart else 'Asc + Moon - Sun'}")
        
        return is_night_chart
