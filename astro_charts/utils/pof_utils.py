from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from .yogi_point_utils import ZODIAC_SIGNS
from .chart_utils import determine_day_night_chart


def calculate_part_of_fortune_rahu_conjunctions(natal_data: Dict[str, Any], transit_data: Dict[str, Any], 
                                         lucky_dates: List[str]) -> List[Dict[str, Any]]:
    """
    Calculate when the Part of Fortune conjuncts Rahu on the specified lucky dates.
    
    The Part of Fortune (Fortuna) is an important Arabic Part in both Western and Vedic astrology,
    representing fortune, prosperity, and success. When it conjuncts Rahu (North Node), 
    it can amplify luck and create opportunities for growth and expansion.
    
    Args:
        natal_data: Natal chart data
        transit_data: Current transit data
        lucky_dates: List of dates to check for Part of Fortune-Rahu conjunctions
    
    Returns:
        List of dictionaries containing conjunction details for each date
    """
    results = []
    
    try:
        # Get current positions of Rahu (North Node)
        rahu_pos = None
        if "transit" in transit_data and "subject" in transit_data["transit"] and "planets" in transit_data["transit"]["subject"]:
            if "rahu" in transit_data["transit"]["subject"]["planets"]:
                rahu_pos = transit_data["transit"]["subject"]["planets"]["rahu"]["abs_pos"]
                rahu_is_retrograde = transit_data["transit"]["subject"]["planets"]["rahu"].get("retrograde", True)
            elif "north_node" in transit_data["transit"]["subject"]["planets"]:
                rahu_pos = transit_data["transit"]["subject"]["planets"]["north_node"]["abs_pos"]
                rahu_is_retrograde = transit_data["transit"]["subject"]["planets"]["north_node"].get("retrograde", True)
            else:
                # Improved astronomical calculation for Rahu based on the mean lunar node
                # The lunar nodes complete a cycle in approximately 18.6 years (6793.5 days)
                # This is a more accurate calculation based on standard astronomical formulas
                
                # First, get current time
                now = datetime.now()
                
                # Establish a known accurate reference point
                # On January 1, 2000, the mean lunar node was at approximately 3° Capricorn
                reference_date = datetime(2000, 1, 1)
                reference_rahu_pos = 273.0  # 3° Capricorn
                
                # Calculate days since reference date
                days_since_ref = (now - reference_date).total_seconds() / 86400  # Convert to days
                
                # Calculate Rahu's position
                # Mean motion of lunar node is approximately -0.053 degrees per day (retrograde)
                # Full cycle of 360° in 6793.5 days = 360 / 6793.5 = 0.053 degrees per day
                rahu_pos = (reference_rahu_pos + (days_since_ref * -0.053)) % 360
                
                # Rahu is always retrograde in mean motion
                rahu_is_retrograde = True
                
                print(f"Calculated Rahu position using improved astronomical formula: {rahu_pos:.2f}°")
        
        if rahu_pos is None:
            return [{"error": "Could not determine Rahu (North Node) position"}]
        
        rahu_daily_motion = 0.053  # Rahu moves about 0.053 degrees per day (retrograde)
        
        # Get current Ascendant position
        if "transit" in transit_data and "subject" in transit_data["transit"] and "houses" in transit_data["transit"]["subject"] and "ascendant" in transit_data["transit"]["subject"]["houses"]:
            current_asc_pos = transit_data["transit"]["subject"]["houses"]["ascendant"]["abs_pos"]
        else:
            # Fallback to natal Ascendant
            current_asc_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
        
        # Get current Sun and Moon positions
        current_sun_pos = transit_data["transit"]["subject"]["planets"]["sun"]["abs_pos"]
        current_moon_pos = transit_data["transit"]["subject"]["planets"]["moon"]["abs_pos"]
        
        # Calculate current Part of Fortune position using our helper method for day/night determination
        is_night_chart = determine_day_night_chart(current_sun_pos, current_asc_pos, transit_data["transit"], "Transit")
        
        if is_night_chart:
            current_pof = (current_asc_pos - current_moon_pos + current_sun_pos) % 360
        else:
            current_pof = (current_asc_pos + current_moon_pos - current_sun_pos) % 360
        
        # Sun's daily motion
        sun_daily_motion = 1.0  # 1 degree per day
        
        # Moon's daily motion
        moon_daily_motion = 13.2  # ~13.2 degrees per day
        
        # Loop through each lucky date
        now = datetime.now()
        
        for date_str in lucky_dates:
            try:
                if not date_str or not isinstance(date_str, str):
                    results.append({
                        "target_date": str(date_str) if date_str is not None else "None",
                        "error": f"Invalid date format: '{date_str}'. Expected format: 'YYYY-MM-DD HH:MM'"
                    })
                    continue
                
                # Handle different date formats
                try:
                    # Try standard format first
                    target_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    try:
                        # Try alternative format with seconds
                        target_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            # Try date only format and set time to noon
                            target_date = datetime.strptime(date_str, "%Y-%m-%d")
                            target_date = target_date.replace(hour=12, minute=0)
                        except ValueError:
                            # If all parsing attempts fail, add error and continue to next date
                            results.append({
                                "target_date": date_str,
                                "error": f"Could not parse date: '{date_str}'. Expected format: 'YYYY-MM-DD HH:MM'"
                            })
                            continue
                
                # Calculate days between now and target date
                days_diff = (target_date - now).total_seconds() / 86400  # Convert to days
                
                # Project positions of celestial bodies on the target date
                projected_sun_pos = (current_sun_pos + (days_diff * sun_daily_motion)) % 360
                projected_moon_pos = (current_moon_pos + (days_diff * moon_daily_motion)) % 360
                
                # Calculate the direction of Rahu's motion (usually retrograde)
                rahu_direction = -1 if rahu_is_retrograde else 1
                projected_rahu_pos = (rahu_pos + (days_diff * rahu_daily_motion * rahu_direction)) % 360
                
                # Ascendant at the target date
                # For simplicity, we'll use the current ascendant adjusted to the time of day
                # This is an approximation since the ascendant would depend on location and exact time
                hours_diff = target_date.hour - now.hour + (target_date.minute - now.minute) / 60
                asc_adjustment = (hours_diff % 24) * 15  # 15 degrees per hour
                projected_asc_pos = (current_asc_pos + asc_adjustment) % 360
                
                # Calculate Part of Fortune at target date
                # We need to recalculate day/night status for the projected date
                projected_is_night = determine_day_night_chart(projected_sun_pos, projected_asc_pos, None, f"Projected {date_str}")
                
                if projected_is_night:
                    projected_pof = (projected_asc_pos - projected_moon_pos + projected_sun_pos) % 360
                else:
                    projected_pof = (projected_asc_pos + projected_moon_pos - projected_sun_pos) % 360
                
                # Check for conjunction between Part of Fortune and Rahu (within 3° orb)
                angular_distance = abs(projected_pof - projected_rahu_pos) % 360
                if angular_distance > 180:
                    angular_distance = 360 - angular_distance
                    
                is_conjunct = angular_distance <= 3
                
                # Get sign information
                pof_sign_num = int(projected_pof / 30)
                pof_sign = list(ZODIAC_SIGNS.keys())[pof_sign_num]
                pof_degree = projected_pof % 30
                
                rahu_sign_num = int(projected_rahu_pos / 30)
                rahu_sign = list(ZODIAC_SIGNS.keys())[rahu_sign_num]
                rahu_degree = projected_rahu_pos % 30
                
                # Add result for this date
                result = {
                    "target_date": target_date.strftime("%Y-%m-%d %H:%M"),
                    "is_pof_rahu_conjunct": is_conjunct,
                    "angular_distance": round(angular_distance, 2),
                    "part_of_fortune": {
                        "position": round(projected_pof, 2),
                        "sign": pof_sign,
                        "degree": round(pof_degree, 2)
                    },
                    "rahu": {
                        "position": round(projected_rahu_pos, 2),
                        "sign": rahu_sign,
                        "degree": round(rahu_degree, 2),
                        "is_retrograde": rahu_is_retrograde,
                        "is_calculated": rahu_pos is not None and "rahu" not in transit_data.get("transit", {}).get("subject", {}).get("planets", {}) and "north_node" not in transit_data.get("transit", {}).get("subject", {}).get("planets", {})
                    }
                }
                
                # Add interpretation based on conjunction status
                if is_conjunct:
                    result["interpretation"] = (
                        f"The Part of Fortune conjuncts Rahu at {round(pof_degree, 2)}° {ZODIAC_SIGNS[pof_sign]} on {target_date.strftime('%Y-%m-%d %H:%M')}. "
                        f"This is a powerful alignment for manifestation, spiritual growth, and unexpected opportunities. "
                        f"This energy amplifies the existing auspicious qualities of this date."
                    )
                else:
                    result["interpretation"] = (
                        f"The Part of Fortune at {round(pof_degree, 2)}° {ZODIAC_SIGNS[pof_sign]} is {round(angular_distance, 2)}° "
                        f"away from Rahu at {round(rahu_degree, 2)}° {ZODIAC_SIGNS[rahu_sign]} on this date. "
                        f"The angular distance exceeds the 3° orb required for a conjunction."
                    )
                
                results.append(result)
                
            except Exception as e:
                print(f"Error processing date '{date_str}': {str(e)}")
                results.append({
                    "target_date": str(date_str) if date_str is not None else "None",
                    "error": f"Error calculating Part of Fortune-Rahu conjunction: {str(e)}"
                })
    
    except Exception as e:
        print(f"Critical error in calculate_part_of_fortune_rahu_conjunctions: {str(e)}")
        return [{"error": f"Critical error calculating Part of Fortune-Rahu conjunctions: {str(e)}"}]
        
    # If no results were processed successfully, return a general error
    if not results:
        return [{"error": "No valid dates could be processed for Part of Fortune-Rahu conjunctions"}]
        
    return results


def calculate_part_of_fortune_regulus_conjunctions(natal_data: Dict[str, Any], transit_data: Dict[str, Any], 
                                             lucky_dates: List[str]) -> List[Dict[str, Any]]:
    """
    Calculate when the Part of Fortune conjuncts Regulus on the specified lucky dates.
    
    Regulus is one of the four Royal Stars of Persia and is considered a star of success,
    ambition, and power. When the Part of Fortune conjuncts Regulus, it can indicate
    periods of recognition, achievement, and favorable outcomes.
    
    Args:
        natal_data: Natal chart data
        transit_data: Current transit data
        lucky_dates: List of dates to check for Part of Fortune-Regulus conjunctions
    
    Returns:
        List of dictionaries containing conjunction details for each date
    """
    results = []
    
    try:
        # Calculate current Regulus position
        # Regulus entered 0° Virgo in 2012
        reference_date = datetime(2012, 1, 1)
        reference_regulus_pos = 150.0  # 0° Virgo
        
        # Regulus moves about 1° every 72 years (very slow)
        regulus_daily_motion = 1.0 / (72 * 365.25)  # Degrees per day
        
        # Get current time
        now = datetime.now()
        
        # Calculate days since reference date
        days_since_ref = (now - reference_date).total_seconds() / 86400  # Convert to days
        
        # Calculate current Regulus position
        current_regulus_pos = (reference_regulus_pos + (days_since_ref * regulus_daily_motion)) % 360
        
        # Get current Ascendant position
        if "transit" in transit_data and "subject" in transit_data["transit"] and "houses" in transit_data["transit"]["subject"] and "ascendant" in transit_data["transit"]["subject"]["houses"]:
            current_asc_pos = transit_data["transit"]["subject"]["houses"]["ascendant"]["abs_pos"]
        else:
            # Fallback to natal Ascendant
            current_asc_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
        
        # Get current Sun and Moon positions
        current_sun_pos = transit_data["transit"]["subject"]["planets"]["sun"]["abs_pos"]
        current_moon_pos = transit_data["transit"]["subject"]["planets"]["moon"]["abs_pos"]
        
        # Calculate current Part of Fortune position using our helper method for day/night determination
        is_night_chart = determine_day_night_chart(current_sun_pos, current_asc_pos, transit_data["transit"], "Transit")
        
        if is_night_chart:
            current_pof = (current_asc_pos - current_moon_pos + current_sun_pos) % 360
        else:
            current_pof = (current_asc_pos + current_moon_pos - current_sun_pos) % 360
        
        # Sun's daily motion
        sun_daily_motion = 1.0  # 1 degree per day
        
        # Moon's daily motion
        moon_daily_motion = 13.2  # ~13.2 degrees per day
        
        # Loop through each lucky date
        for date_str in lucky_dates:
            try:
                if not date_str or not isinstance(date_str, str):
                    results.append({
                        "target_date": str(date_str) if date_str is not None else "None",
                        "error": f"Invalid date format: '{date_str}'. Expected format: 'YYYY-MM-DD HH:MM'"
                    })
                    continue
                
                # Parse the date string
                try:
                    target_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    try:
                        target_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            target_date = datetime.strptime(date_str, "%Y-%m-%d")
                            target_date = target_date.replace(hour=12, minute=0)
                        except ValueError:
                            results.append({
                                "target_date": date_str,
                                "error": f"Could not parse date: '{date_str}'. Expected format: 'YYYY-MM-DD HH:MM'"
                            })
                            continue
                
                # Calculate days between now and target date
                days_diff = (target_date - now).total_seconds() / 86400
                
                # Project positions for the target date
                projected_sun_pos = (current_sun_pos + (days_diff * sun_daily_motion)) % 360
                projected_moon_pos = (current_moon_pos + (days_diff * moon_daily_motion)) % 360
                projected_regulus_pos = (current_regulus_pos + (days_diff * regulus_daily_motion)) % 360
                
                # Calculate ascendant at target date
                hours_diff = target_date.hour - now.hour + (target_date.minute - now.minute) / 60
                asc_adjustment = (hours_diff % 24) * 15  # 15 degrees per hour
                projected_asc_pos = (current_asc_pos + asc_adjustment) % 360
                
                # Calculate Part of Fortune at target date
                # We need to recalculate day/night status for the projected date
                projected_is_night = determine_day_night_chart(projected_sun_pos, projected_asc_pos, None, f"Projected {date_str}")
                
                if projected_is_night:
                    projected_pof = (projected_asc_pos - projected_moon_pos + projected_sun_pos) % 360
                else:
                    projected_pof = (projected_asc_pos + projected_moon_pos - projected_sun_pos) % 360
                
                # Check for conjunction between Part of Fortune and Regulus (within 3° orb)
                angular_distance = abs(projected_pof - projected_regulus_pos) % 360
                if angular_distance > 180:
                    angular_distance = 360 - angular_distance
                    
                is_conjunct = angular_distance <= 3
                
                # Get sign information
                pof_sign_num = int(projected_pof / 30)
                pof_sign = list(ZODIAC_SIGNS.keys())[pof_sign_num]
                pof_degree = projected_pof % 30
                
                regulus_sign_num = int(projected_regulus_pos / 30)
                regulus_sign = list(ZODIAC_SIGNS.keys())[regulus_sign_num]
                regulus_degree = projected_regulus_pos % 30
                
                # Add result for this date
                result = {
                    "target_date": target_date.strftime("%Y-%m-%d %H:%M"),
                    "is_pof_regulus_conjunct": is_conjunct,
                    "angular_distance": round(angular_distance, 2),
                    "part_of_fortune": {
                        "position": round(projected_pof, 2),
                        "sign": pof_sign,
                        "degree": round(pof_degree, 2)
                    },
                    "regulus": {
                        "position": round(projected_regulus_pos, 2),
                        "sign": regulus_sign,
                        "degree": round(regulus_degree, 2)
                    }
                }
                
                # Add interpretation based on conjunction status
                if is_conjunct:
                    result["interpretation"] = (
                        f"The Part of Fortune conjuncts Regulus at {round(pof_degree, 2)}° {ZODIAC_SIGNS[pof_sign]} on {target_date.strftime('%Y-%m-%d %H:%M')}. "
                        f"This is a powerful alignment for success, recognition, and achievement. "
                        f"Regulus bestows honors and favors from authority figures when well aspected."
                    )
                else:
                    result["interpretation"] = (
                        f"The Part of Fortune at {round(pof_degree, 2)}° {ZODIAC_SIGNS[pof_sign]} is {round(angular_distance, 2)}° "
                        f"away from Regulus at {round(regulus_degree, 2)}° {ZODIAC_SIGNS[regulus_sign]} on this date. "
                        f"The angular distance exceeds the 3° orb required for a conjunction."
                    )
                
                results.append(result)
                
            except Exception as e:
                print(f"Error processing date '{date_str}': {str(e)}")
                results.append({
                    "target_date": str(date_str) if date_str is not None else "None",
                    "error": f"Error calculating Part of Fortune-Regulus conjunction: {str(e)}"
                })
    
    except Exception as e:
        print(f"Critical error in calculate_part_of_fortune_regulus_conjunctions: {str(e)}")
        return [{"error": f"Critical error calculating Part of Fortune-Regulus conjunctions: {str(e)}"}]
        
    # If no results were processed successfully, return a general error
    if not results:
        return [{"error": "No valid dates could be processed for Part of Fortune-Regulus conjunctions"}]
        
    return results 