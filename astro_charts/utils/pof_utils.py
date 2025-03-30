from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from .yogi_point_utils import ZODIAC_SIGNS
from .chart_utils import determine_day_night_chart


def calculate_part_of_fortune_rahu_conjunctions(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any], 
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
            # --- Determine the reference time for projections ---
            reference_time = None
            try:
                # Attempt 1: Get precise UTC time from transit data
                if ("transit" in transit_data and isinstance(transit_data['transit'], dict) and
                    "subject" in transit_data['transit'] and isinstance(transit_data['transit']['subject'], dict) and
                    "date_utc" in transit_data["transit"]["subject"]):
                    date_utc_str = transit_data["transit"]["subject"]["date_utc"]
                    if date_utc_str:
                        if date_utc_str.endswith('Z'): date_utc_str = date_utc_str[:-1] + '+00:00'
                        if '.' in date_utc_str:
                             parts = date_utc_str.split('.')
                             date_utc_str = parts[0] + '.' + parts[1][:6]
                             if '+' not in date_utc_str and '-' not in date_utc_str[10:]: date_utc_str += '+00:00'
                        reference_time = datetime.fromisoformat(date_utc_str)
                        print(f"[PoF-Rahu] SUCCESS: Using reference time from transit.subject.date_utc: {reference_time}")
            
                # Attempt 2: Reconstruct from transit subject birth_data
                if reference_time is None:
                     if ("transit" in transit_data and isinstance(transit_data['transit'], dict) and
                         "subject" in transit_data['transit'] and isinstance(transit_data['transit']['subject'], dict) and
                         "birth_data" in transit_data["transit"]["subject"] and isinstance(transit_data['transit']['subject']['birth_data'], dict)):
                         t_info = transit_data["transit"]["subject"]["birth_data"]
                         required_keys = ["date", "time"]
                         if all(k in t_info for k in required_keys) and t_info["date"] and t_info["time"]:
                             datetime_str = f"{t_info['date']} {t_info['time']}"
                             try:
                                 reference_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                                 print(f"[PoF-Rahu] SUCCESS: Using reference time reconstructed from transit.subject.birth_data: {reference_time} (Assumed Local)")
                             except ValueError as parse_error:
                                 print(f"[PoF-Rahu] DEBUG: Attempt 2 Error parsing date/time string '{datetime_str}': {parse_error}")

                # Attempt 3: Reconstruct from top-level transit info
                if reference_time is None:
                    required_keys = ["transit_year", "transit_month", "transit_day", "transit_hour", "transit_minute"]
                    if all(k in transit_data for k in required_keys):
                        reference_time = datetime(
                            int(transit_data["transit_year"]), int(transit_data["transit_month"]), int(transit_data["transit_day"]),
                            int(transit_data["transit_hour"]), int(transit_data["transit_minute"])
                        )
                        print(f"[PoF-Rahu] SUCCESS: Using reference time reconstructed from top-level transit_data keys: {reference_time} (Assumed Local)")

            except Exception as e:
                print(f"[PoF-Rahu] ERROR: Exception during reference time extraction: {e}")

            # Fallback if no time could be extracted
            if reference_time is None:
                reference_time = datetime.now() # Keep existing fallback but log warning
                print(f"[PoF-Rahu] WARNING: Could not extract reference time from transit_data. Falling back to datetime.now(). Results may drift.")

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
            is_night_chart = self.determine_day_night_chart(current_sun_pos, current_asc_pos, transit_data["transit"], "Transit")
            
            if is_night_chart:
                current_pof = (current_asc_pos - current_moon_pos + current_sun_pos) % 360
            else:
                current_pof = (current_asc_pos + current_moon_pos - current_sun_pos) % 360
            
            # Sun's daily motion
            sun_daily_motion = 1.0  # 1 degree per day
            
            # Moon's daily motion
            moon_daily_motion = 13.2  # ~13.2 degrees per day
            
            # Loop through each lucky date
            # Use the determined reference_time instead of datetime.now()
            
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
                    days_diff = (target_date - reference_time).total_seconds() / 86400  # Convert to days
                    
                    # Project positions of celestial bodies on the target date
                    projected_sun_pos = (current_sun_pos + (days_diff * sun_daily_motion)) % 360
                    projected_moon_pos = (current_moon_pos + (days_diff * moon_daily_motion)) % 360
                    
                    # Calculate the direction of Rahu's motion (usually retrograde)
                    rahu_direction = -1 if rahu_is_retrograde else 1
                    projected_rahu_pos = (rahu_pos + (days_diff * rahu_daily_motion * rahu_direction)) % 360
                    
                    # Ascendant at the target date
                    # For simplicity, we'll use the current ascendant adjusted to the time of day
                    # This is an approximation since the ascendant would depend on location and exact time
                    hours_diff = target_date.hour - reference_time.hour + (target_date.minute - reference_time.minute) / 60
                    asc_adjustment = (hours_diff % 24) * 15  # 15 degrees per hour
                    projected_asc_pos = (current_asc_pos + asc_adjustment) % 360
                    
                    # Calculate Part of Fortune at target date
                    # We need to recalculate day/night status for the projected date
                    projected_is_night = self.determine_day_night_chart(projected_sun_pos, projected_asc_pos, None, f"Projected {date_str}")
                    
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

def calculate_part_of_fortune_regulus_conjunctions(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any], 
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
            # --- Determine the reference time for projections ---
            reference_time = None
            try:
                # Attempt 1: Get precise UTC time from transit data
                if ("transit" in transit_data and isinstance(transit_data['transit'], dict) and
                    "subject" in transit_data['transit'] and isinstance(transit_data['transit']['subject'], dict) and
                    "date_utc" in transit_data["transit"]["subject"]):
                    date_utc_str = transit_data["transit"]["subject"]["date_utc"]
                    if date_utc_str:
                        if date_utc_str.endswith('Z'): date_utc_str = date_utc_str[:-1] + '+00:00'
                        if '.' in date_utc_str:
                             parts = date_utc_str.split('.')
                             date_utc_str = parts[0] + '.' + parts[1][:6]
                             if '+' not in date_utc_str and '-' not in date_utc_str[10:]: date_utc_str += '+00:00'
                        reference_time = datetime.fromisoformat(date_utc_str)
                        print(f"[PoF-Regulus] SUCCESS: Using reference time from transit.subject.date_utc: {reference_time}")
            
                # Attempt 2: Reconstruct from transit subject birth_data
                if reference_time is None:
                     if ("transit" in transit_data and isinstance(transit_data['transit'], dict) and
                         "subject" in transit_data['transit'] and isinstance(transit_data['transit']['subject'], dict) and
                         "birth_data" in transit_data["transit"]["subject"] and isinstance(transit_data['transit']['subject']['birth_data'], dict)):
                         t_info = transit_data["transit"]["subject"]["birth_data"]
                         required_keys = ["date", "time"]
                         if all(k in t_info for k in required_keys) and t_info["date"] and t_info["time"]:
                             datetime_str = f"{t_info['date']} {t_info['time']}"
                             try:
                                 reference_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                                 print(f"[PoF-Regulus] SUCCESS: Using reference time reconstructed from transit.subject.birth_data: {reference_time} (Assumed Local)")
                             except ValueError as parse_error:
                                 print(f"[PoF-Regulus] DEBUG: Attempt 2 Error parsing date/time string '{datetime_str}': {parse_error}")

                # Attempt 3: Reconstruct from top-level transit info
                if reference_time is None:
                    required_keys = ["transit_year", "transit_month", "transit_day", "transit_hour", "transit_minute"]
                    if all(k in transit_data for k in required_keys):
                        reference_time = datetime(
                            int(transit_data["transit_year"]), int(transit_data["transit_month"]), int(transit_data["transit_day"]),
                            int(transit_data["transit_hour"]), int(transit_data["transit_minute"])
                        )
                        print(f"[PoF-Regulus] SUCCESS: Using reference time reconstructed from top-level transit_data keys: {reference_time} (Assumed Local)")

            except Exception as e:
                print(f"[PoF-Regulus] ERROR: Exception during reference time extraction: {e}")

            # Fallback if no time could be extracted
            if reference_time is None:
                reference_time = datetime.now() # Keep existing fallback but log warning
                print(f"[PoF-Regulus] WARNING: Could not extract reference time from transit_data. Falling back to datetime.now(). Results may drift.")

            # Calculate current Regulus position
            # Regulus entered 0° Virgo in 2012
            regulus_reference_date = datetime(2012, 1, 1)
            reference_regulus_pos = 150.0  # 0° Virgo
            
            # Regulus moves about 1° every 72 years (very slow)
            regulus_daily_motion = 1.0 / (72 * 365.25)  # Degrees per day
            
            # Use reference_time instead of now
            
            # Calculate days since reference date
            days_since_ref = (reference_time - regulus_reference_date).total_seconds() / 86400  # Convert to days
            
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
            is_night_chart = self.determine_day_night_chart(current_sun_pos, current_asc_pos, transit_data["transit"], "Transit")
            
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
                    days_diff = (target_date - reference_time).total_seconds() / 86400
                    
                    # Project positions for the target date
                    projected_sun_pos = (current_sun_pos + (days_diff * sun_daily_motion)) % 360
                    projected_moon_pos = (current_moon_pos + (days_diff * moon_daily_motion)) % 360
                    projected_regulus_pos = (current_regulus_pos + (days_diff * regulus_daily_motion)) % 360
                    
                    # Calculate ascendant at target date
                    hours_diff = target_date.hour - reference_time.hour + (target_date.minute - reference_time.minute) / 60
                    asc_adjustment = (hours_diff % 24) * 15  # 15 degrees per hour
                    projected_asc_pos = (current_asc_pos + asc_adjustment) % 360
                    
                    # Calculate Part of Fortune at target date
                    # We need to recalculate day/night status for the projected date
                    projected_is_night = self.determine_day_night_chart(projected_sun_pos, projected_asc_pos, None, f"Projected {date_str}")
                    
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

def calculate_part_of_fortune_lord_lagna_conjunctions(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any], 
                                                 lucky_dates: List[str]) -> List[Dict[str, Any]]:
        """
        Calculate when the Part of Fortune conjuncts the Lord of the Ascendant (Lagna) on the specified lucky dates.
        
        The Part of Fortune represents prosperity and success, while the Lord of the Ascendant represents
        one's self, physical body, and overall life direction. When these points conjunct, it creates
        an auspicious time for personal empowerment, success, and aligning one's actions with prosperity.
        
        Args:
            natal_data: Natal chart data
            transit_data: Current transit data
            lucky_dates: List of dates to check for Part of Fortune-Lord Lagna conjunctions
        
        Returns:
            List of dictionaries containing conjunction details for each date
        """
        results = []
        
        try:
            # Determine the Lord of the Ascendant (Lagna)
            ascendant_sign = natal_data["subject"]["houses"]["ascendant"]["sign"]
            lord_lagna_planet = self.get_ascendant_ruler(ascendant_sign, zodiac_type="Sidereal")
            
            # Check if the Lord of Lagna is available in the transit data
            if lord_lagna_planet not in transit_data["transit"]["subject"]["planets"]:
                return [{
                    "error": f"Cannot calculate Part of Fortune-Lord Lagna conjunctions - {lord_lagna_planet.capitalize()} (Lord of Ascendant) transit data not available"
                }]
            
            # Get current Ascendant position
            if "houses" in transit_data["transit"]["subject"] and "ascendant" in transit_data["transit"]["subject"]["houses"]:
                current_asc_pos = transit_data["transit"]["subject"]["houses"]["ascendant"]["abs_pos"]
            else:
                # Fallback to natal Ascendant
                current_asc_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
            
            # Get current Sun and Moon positions
            current_sun_pos = transit_data["transit"]["subject"]["planets"]["sun"]["abs_pos"]
            current_moon_pos = transit_data["transit"]["subject"]["planets"]["moon"]["abs_pos"]
            
            # Get current Lord Lagna position and motion
            current_lord_pos = transit_data["transit"]["subject"]["planets"][lord_lagna_planet]["abs_pos"]
            is_lord_retrograde = transit_data["transit"]["subject"]["planets"][lord_lagna_planet]["retrograde"]
            
            # Get daily motion for Lord Lagna planet
            lord_daily_motion = PLANET_DAILY_MOTION.get(lord_lagna_planet, 1.0)
            if is_lord_retrograde:
                lord_daily_motion *= 0.8  # Slower when retrograde
            
            # Calculate current Part of Fortune position using our helper method for day/night determination
            is_night_chart = self.determine_day_night_chart(current_sun_pos, current_asc_pos, transit_data["transit"], "Transit")
            
            # Calculate current Part of Fortune position
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
                    
                    # Parse the date string, handling different formats
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
                    
                    # Calculate Lord Lagna movement direction
                    lord_direction = -1 if is_lord_retrograde else 1
                    projected_lord_pos = (current_lord_pos + (days_diff * lord_daily_motion * lord_direction)) % 360
                    
                    # Calculate ascendant at target date (approximation)
                    hours_diff = target_date.hour - now.hour + (target_date.minute - now.minute) / 60
                    asc_adjustment = (hours_diff % 24) * 15  # 15 degrees per hour
                    projected_asc_pos = (current_asc_pos + asc_adjustment) % 360
                    
                    # Calculate Part of Fortune at target date
                    # We need to recalculate day/night status for the projected date
                    projected_is_night = self.determine_day_night_chart(projected_sun_pos, projected_asc_pos, None, f"Projected {date_str}")
                    
                    if projected_is_night:
                        projected_pof = (projected_asc_pos - projected_moon_pos + projected_sun_pos) % 360
                    else:
                        projected_pof = (projected_asc_pos + projected_moon_pos - projected_sun_pos) % 360
                    
                    # Check for conjunction between Part of Fortune and Lord Lagna (within 3° orb)
                    angular_distance = abs(projected_pof - projected_lord_pos) % 360
                    if angular_distance > 180:
                        angular_distance = 360 - angular_distance
                        
                    is_conjunct = angular_distance <= 3
                    
                    # Get sign information
                    pof_sign_num = int(projected_pof / 30)
                    pof_sign = list(ZODIAC_SIGNS.keys())[pof_sign_num]
                    pof_degree = projected_pof % 30
                    
                    lord_sign_num = int(projected_lord_pos / 30)
                    lord_sign = list(ZODIAC_SIGNS.keys())[lord_sign_num]
                    lord_degree = projected_lord_pos % 30
                    
                    # Add result for this date
                    result = {
                        "target_date": target_date.strftime("%Y-%m-%d %H:%M"),
                        "is_pof_lord_lagna_conjunct": is_conjunct,
                        "angular_distance": round(angular_distance, 2),
                        "part_of_fortune": {
                            "position": round(projected_pof, 2),
                            "sign": pof_sign,
                            "degree": round(pof_degree, 2)
                        },
                        "lord_lagna": {
                            "planet": lord_lagna_planet,
                            "position": round(projected_lord_pos, 2),
                            "sign": lord_sign,
                            "degree": round(lord_degree, 2),
                            "is_retrograde": is_lord_retrograde
                        }
                    }
                    
                    # Add interpretation based on conjunction status
                    if is_conjunct:
                        result["interpretation"] = (
                            f"The Part of Fortune conjuncts {lord_lagna_planet.capitalize()} (Lord of your Ascendant) at {round(pof_degree, 2)}° {ZODIAC_SIGNS[pof_sign]} on {target_date.strftime('%Y-%m-%d %H:%M')}. "
                            f"This is a powerful alignment for personal empowerment, success, and aligning your actions with prosperity. "
                            f"The Lord of your Ascendant represents your physical self and life direction, while the Part of Fortune represents good fortune and prosperity."
                        )
                    else:
                        result["interpretation"] = (
                            f"The Part of Fortune at {round(pof_degree, 2)}° {ZODIAC_SIGNS[pof_sign]} is {round(angular_distance, 2)}° "
                            f"away from {lord_lagna_planet.capitalize()} (Lord of your Ascendant) at {round(lord_degree, 2)}° {ZODIAC_SIGNS[lord_sign]} on this date. "
                            f"The angular distance exceeds the 3° orb required for a conjunction."
                        )
                    
                    results.append(result)
                    
                except Exception as e:
                    print(f"Error processing date '{date_str}': {str(e)}")
                    results.append({
                        "target_date": str(date_str) if date_str is not None else "None",
                        "error": f"Error calculating Part of Fortune-Lord Lagna conjunction: {str(e)}"
                    })
        
        except Exception as e:
            print(f"Critical error in calculate_part_of_fortune_lord_lagna_conjunctions: {str(e)}")
            return [{"error": f"Critical error calculating Part of Fortune-Lord Lagna conjunctions: {str(e)}"}]
            
        # If no results were processed successfully, return a general error
        if not results:
            return [{"error": "No valid dates could be processed for Part of Fortune-Lord Lagna conjunctions"}]
            
        return results

def calculate_part_of_fortune_regulus_conjunctions(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any], 
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

def calculate_ascendant_part_of_fortune_conjunctions(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any], 
                                                 num_days: int = 7, orb: float = 3.0) -> List[Dict[str, Any]]:
        """
        Calculate when the transiting ascendant will conjunct the natal Part of Fortune over a specified period.
        Since this happens once per day, we calculate it for a default period of 7 days.
        
        Args:
            natal_data: Natal chart data
            transit_data: Current transit data
            num_days: Number of days to calculate conjunctions for (default: 7)
            orb: The orb value to use for aspects in degrees (default: 3.0)
            
        Returns:
            List of dictionaries containing conjunction details for each day
        """
        conjunctions = []
        
        try:
           #  Calculate the natal Part of Fortune position
            # Formula: Asc + Moon - Sun (day chart) or Asc - Moon + Sun (night chart)
            natal_sun_pos = natal_data["subject"]["planets"]["sun"]["abs_pos"]
            natal_moon_pos = natal_data["subject"]["planets"]["moon"]["abs_pos"]
            natal_asc_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
            
            # Determine if it's a day or night chart using the helper method
            is_night_chart = self.determine_day_night_chart(natal_sun_pos, natal_asc_pos, natal_data, "Natal")
            
            # Calculate Part of Fortune using the appropriate formula
            if is_night_chart:
                natal_pof = (natal_asc_pos - natal_moon_pos + natal_sun_pos) % 360
            else:
                natal_pof = (natal_asc_pos + natal_moon_pos - natal_sun_pos) % 360
                
            ayanamsha_offset = 24 # TODO: Get ayanamsha from settings or chart data
            natal_pof = (natal_pof + ayanamsha_offset) % 360
            print(f"NATAL POF: {natal_pof}")
            
            # Get current ascendant position from transit_data
            current_asc_pos = None
            estimation_method = "unknown"
            
            # Log the transit data structure to help with debugging
            print("DEBUG: Finding transit ascendant position")
            
            # =====================================================================
            # PRIORITY 1: Direct access to transit ascendant (most accurate)
            # =====================================================================
            if ("transit" in transit_data and 
                "subject" in transit_data["transit"] and 
                "houses" in transit_data["transit"]["subject"] and 
                "ascendant" in transit_data["transit"]["subject"]["houses"]):
                
                current_asc_pos = transit_data["transit"]["subject"]["houses"]["ascendant"]["abs_pos"]
                current_asc_pos = (current_asc_pos + ayanamsha_offset) % 360
                estimation_method = "transit_ascendant"
                print(f"SUCCESS: Found exact transit ascendant position: {round(current_asc_pos, 2)}°")
            
            # =====================================================================
            # PRIORITY 2: Calculate from Midheaven (MC) if available
            # =====================================================================
            elif ("transit" in transit_data and 
                 "subject" in transit_data["transit"] and 
                 "houses" in transit_data["transit"]["subject"] and 
                 "midheaven" in transit_data["transit"]["subject"]["houses"]):
                
                midheaven_pos = transit_data["transit"]["subject"]["houses"]["midheaven"]["abs_pos"]
                # Ascendant is approximately midheaven - 90° (depends on location, but this is a reasonable approximation)
                current_asc_pos = (midheaven_pos - 90 + ayanamsha_offset) % 360 # Apply ayanamsha
                estimation_method = "from_midheaven"
                print(f"APPROXIMATION: Estimated ascendant from midheaven: {round(current_asc_pos, 2)}°")
            
            # Check if MC is stored as house_10 instead
            elif ("transit" in transit_data and 
                 "subject" in transit_data["transit"] and 
                 "houses" in transit_data["transit"]["subject"] and 
                 "house_10" in transit_data["transit"]["subject"]["houses"]):
                
                mc_pos = transit_data["transit"]["subject"]["houses"]["house_10"]["abs_pos"]
                current_asc_pos = (mc_pos - 90 + ayanamsha_offset) % 360 # Apply ayanamsha
                estimation_method = "from_house_10"
                print(f"APPROXIMATION: Estimated ascendant from house_10: {round(current_asc_pos, 2)}°")
            
            # =====================================================================
            # PRIORITY 3: Calculate from transit Sun position and time (Less reliable for precise Asc)
            # =====================================================================
            # Note: This method is less accurate for Ascendant position needed for this specific calculation.
            # It's kept here for potential fallback but marked as less preferred.
            # elif (...) # Existing sun position logic - consider removing or lowering priority further if unused
            
            # =====================================================================
            # PRIORITY 4: Use time-based estimation from natal chart as fallback (Least reliable)
            # =====================================================================
            # else: # Existing time-based estimation logic - consider removing or lowering priority

            # If we still don't have an ascendant position after trying direct/MC methods, raise error
            if current_asc_pos is None:
                # Try getting ascendant from natal data as a last resort (may not be accurate for transit)
                if "houses" in natal_data["subject"] and "ascendant" in natal_data["subject"]["houses"]:
                     current_asc_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
                     current_asc_pos = (current_asc_pos + ayanamsha_offset) % 360 # Apply ayanamsha
                     estimation_method = "natal_fallback"
                     print(f"WARNING: Using natal ascendant as fallback: {round(current_asc_pos, 2)}°")
                else:
                     raise ValueError("Could not determine ascendant position using transit or natal data")

            # --- Determine the reference time for the calculation ---
            reference_time = None
            try:
                # --- Enhanced Logging for Debugging Reference Time Extraction ---
                print(f"DEBUG: Attempting to extract reference time from transit_data.")
                print(f"DEBUG: Top-level transit_data keys: {list(transit_data.keys())}")

                # Attempt 1: Get precise UTC time from transit data if available
                if "transit" in transit_data and isinstance(transit_data['transit'], dict):
                    print(f"DEBUG: Found 'transit' key. Keys inside: {list(transit_data['transit'].keys())}")
                    if "subject" in transit_data['transit'] and isinstance(transit_data['transit']['subject'], dict):
                        print(f"DEBUG: Found 'subject' key inside 'transit'. Keys inside: {list(transit_data['transit']['subject'].keys())}")
                        if "date_utc" in transit_data["transit"]["subject"]:
                            date_utc_str = transit_data["transit"]["subject"]["date_utc"]
                            print(f"DEBUG: Attempt 1: Found date_utc: {date_utc_str}")
                            if date_utc_str:
                                if date_utc_str.endswith('Z'):
                                   date_utc_str = date_utc_str[:-1] + '+00:00'
                                if '.' in date_utc_str:
                                     parts = date_utc_str.split('.')
                                     date_utc_str = parts[0] + '.' + parts[1][:6] # Truncate microseconds
                                     if '+' not in date_utc_str and '-' not in date_utc_str[10:]:
                                         date_utc_str += '+00:00'

                                reference_time = datetime.fromisoformat(date_utc_str)
                                print(f"SUCCESS: Using reference time from transit_data.transit.subject.date_utc: {reference_time}")
                            else:
                                print("DEBUG: Attempt 1: date_utc field was empty.")
                        else:
                             print("DEBUG: Attempt 1: 'date_utc' key not found in transit.subject.")
                    else:
                        print("DEBUG: 'subject' key not found or not a dict in transit.")
                else:
                    print("DEBUG: 'transit' key not found or not a dict at top level.")

                # Attempt 2: Reconstruct from transit subject birth_data (often used for transit time/location)
                if reference_time is None:
                    if ("transit" in transit_data and isinstance(transit_data['transit'], dict) and
                        "subject" in transit_data['transit'] and isinstance(transit_data['transit']['subject'], dict) and
                        "birth_data" in transit_data["transit"]["subject"] and isinstance(transit_data['transit']['subject']['birth_data'], dict)):
                        
                        t_info = transit_data["transit"]["subject"]["birth_data"]
                        print(f"DEBUG: Attempt 2: Found transit.subject.birth_data. Keys: {list(t_info.keys())}")
                        # --- MODIFIED --- Look for 'date' and 'time' keys instead of year, month, etc.
                        required_keys = ["date", "time"]
                        if all(k in t_info for k in required_keys) and t_info["date"] and t_info["time"]:
                             date_str = t_info["date"] # e.g., "2025-03-29"
                             time_str = t_info["time"] # e.g., "12:00"
                             datetime_str = f"{date_str} {time_str}"
                             try:
                                 # Combine and parse the date and time strings
                                 reference_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                                 print(f"SUCCESS: Using reference time reconstructed from transit.subject.birth_data (date='{date_str}', time='{time_str}'): {reference_time} (Assumed Local)")
                             except ValueError as parse_error:
                                 print(f"DEBUG: Attempt 2: Error parsing date/time string '{datetime_str}': {parse_error}")
                        else:
                            print(f"DEBUG: Attempt 2: Missing or empty 'date' or 'time' keys in birth_data.")
                    else:
                        print("DEBUG: Attempt 2: Path transit.subject.birth_data not found or is not a dictionary.")

                # Attempt 3: Reconstruct from top-level transit info (another common pattern)
                if reference_time is None:
                     required_keys = ["transit_year", "transit_month", "transit_day", "transit_hour", "transit_minute"]
                     if all(k in transit_data for k in required_keys):
                         print(f"DEBUG: Attempt 3: Found top-level transit time keys.")
                         reference_time = datetime(
                             int(transit_data["transit_year"]), int(transit_data["transit_month"]), int(transit_data["transit_day"]),
                             int(transit_data["transit_hour"]), int(transit_data["transit_minute"])
                         )
                         print(f"SUCCESS: Using reference time reconstructed from top-level transit_data keys: {reference_time} (Assumed Local)")
                     else:
                         print(f"DEBUG: Attempt 3: Missing one or more required top-level keys: {required_keys}")

            except Exception as e:
                print(f"ERROR: Exception during reference time extraction: {e}")
                import traceback
                traceback.print_exc() # Print full traceback for detailed debugging

            # Fallback if no time could be extracted
            if reference_time is None:
                reference_time = datetime.now() # Keep existing fallback but log warning
                print(f"WARNING: Could not extract reference time from transit_data. Falling back to datetime.now(): {reference_time}. Results may drift.")

            # --- Calculation based on the determined reference_time ---
            
            # Calculate how many degrees until the ascendant reaches the Part of Fortune
            degrees_to_pof = (natal_pof - current_asc_pos) % 360
            
            # Convert to hours (ascendant moves at 15° per hour)
            hours_to_pof = degrees_to_pof / 15
            
            # First conjunction time calculated from the stable reference time
            first_conjunction = reference_time + timedelta(hours=hours_to_pof)
            print(f"First conjunction time: {first_conjunction}")
            print(f"Hours to POF: {hours_to_pof}")
            print(f"Reference Time: {reference_time}") # Changed log from 'Now'
            print(f"Time Delta: {timedelta(hours=hours_to_pof)}")
            
            # Calculate duration - Ascendant moves at 15° per hour, using the provided orb
            # orb° / 15° per hour = orb/15 hours = (orb/15)*60 minutes on each side
            minutes_per_degree = 4  # 15° per hour = 1° per 4 minutes
            conjunction_duration_minutes = int(orb * minutes_per_degree * 2)  # Double the orb duration for total (before and after)
            conjunction_half_duration = conjunction_duration_minutes / 2  # Half for calculating start and end times
            
            # Generate conjunctions for the specified number of days
            for day in range(num_days):
                try:
                    # Calculate conjunction time for this day
                    # Each day, the ascendant will reach the same degree ~4 minutes earlier (sidereal day is ~23h56m)
                    conjunction_time = first_conjunction + timedelta(days=day, minutes=-4*day)
                    # print(f"Conjunction time: {conjunction_time}") # Original print
                    print(f"Conjunction time for day {day}: {conjunction_time}") # Modified print for clarity

                    # Calculate the sign information
                    pof_sign_num = int(natal_pof / 30)
                    pof_sign = list(ZODIAC_SIGNS.keys())[pof_sign_num]
                    pof_degree = natal_pof % 30
                    
                    # Calculate the start and end time for this conjunction
                    start_time = conjunction_time - timedelta(minutes=conjunction_half_duration)
                    end_time = conjunction_time + timedelta(minutes=conjunction_half_duration)
                    
                    # Add to results
                    conjunctions.append({
                        "conjunction_date": conjunction_time.strftime("%Y-%m-%d %H:%M"),
                        "time_iso": conjunction_time.isoformat(),
                        "days_away": day,
                        "hours_away": round((conjunction_time - reference_time).total_seconds() / 3600, 1) if day == 0 else None,
                        "part_of_fortune": {
                            "position": round(natal_pof, 2),
                            "sign": pof_sign,
                            "degree": round(pof_degree, 2)
                        },
                        "is_night_chart": is_night_chart,
                        "is_estimated": estimation_method != "transit_ascendant",  # Only direct ascendant is not estimated
                        "estimation_method": estimation_method,
                        "calculation_note": f"Ascendant position calculated via: {estimation_method}",
                        "duration": {
                            "minutes": conjunction_duration_minutes,
                            "orb_used": orb,
                            "start_time": start_time.strftime("%Y-%m-%d %H:%M"),
                            "exact_time": conjunction_time.strftime("%Y-%m-%d %H:%M"),
                            "end_time": end_time.strftime("%Y-%m-%d %H:%M"),
                            "description": f"This conjunction lasts approximately {conjunction_duration_minutes} minutes, from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')} (using {orb}° orb)"
                        }
                    })
                except Exception as e:
                    print(f"Error calculating conjunction for day {day}: {str(e)}")
                    # Skip this day if an error occurs
        
            # Add interpretation and accuracy note for each conjunction
            for conjunction in conjunctions:
                pof_sign = conjunction["part_of_fortune"]["sign"]
                pof_degree = conjunction["part_of_fortune"]["degree"]
                conj_date = conjunction["conjunction_date"]
                is_estimated = conjunction.get("is_estimated", False)
                estimation_method = conjunction.get("estimation_method", "")
                
                # Base interpretation
                base_interpretation = (
                    f"The ascendant will conjunct your natal Part of Fortune at {round(pof_degree, 2)}° {ZODIAC_SIGNS[pof_sign]} "
                    f"on {conj_date}. This creates a brief window of enhanced fortune and opportunity, "
                    f"especially for new beginnings and important personal initiatives. "
                    f"This alignment lasts approximately {conjunction_duration_minutes} minutes (using {orb}° orb)."
                )
                
                # Add accuracy note based on estimation method
                if is_estimated:
                    accuracy_notes = {
                        "transit_ascendant": "This is a precise calculation based on the actual ascendant position in the transit chart.",
                        "from_midheaven": "This is a good approximation based on the midheaven position (±5-10 minutes).",
                        "from_house_10": "This is a good approximation based on the 10th house cusp (±5-10 minutes).",
                        "sun_position": "This method provides a reasonable approximation (±10-15 minutes).",
                        "time_based": "This method provides a general approximation (±20-30 minutes).",
                        "simple_time": "This is a very general approximation (±30-60 minutes).",
                        "natal_fallback": "Accuracy depends on how much the transit ascendant has shifted from the natal ascendant."
                    }
                    
                    method_desc = {
                        "transit_ascendant": "using the exact transit ascendant position",
                        "from_midheaven": "calculated from the midheaven position",
                        "from_house_10": "calculated from the 10th house cusp",
                        "sun_position": "based on the sun's position and time of day",
                        "time_based": "based on your birth chart and current time",
                        "simple_time": "based on time of day only",
                        "natal_fallback": "using the natal ascendant as a fallback"
                    }
                    
                    method_text = method_desc.get(estimation_method, "using an estimated method")
                    accuracy_text = accuracy_notes.get(estimation_method, "Timing may vary.")
                    
                    interpretation = (
                        f"{base_interpretation} (Note: This time is {method_text}. "
                        f"{accuracy_text} For precise timing, please consult an ephemeris or astrology software "
                        f"with your exact birth location and current location.)"
                    )
                else:
                    interpretation = base_interpretation
                
                conjunction["interpretation"] = interpretation
            
            return conjunctions
                
        except Exception as e:
            error_msg = f"Error calculating ascendant-part of fortune conjunctions: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return [{"error": error_msg}]
