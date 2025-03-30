import math
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .yogi_point_utils import ZODIAC_SIGNS
from .chart_utils import calculate_d9_chart

def calculate_bullseye_periods(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            # --- Determine the reference time for projections (Added) ---
            reference_time = None
            try:
                # Attempt 1: Get precise UTC time from transit data if available
                if transit_data and "transit" in transit_data and isinstance(transit_data['transit'], dict):
                    if "subject" in transit_data['transit'] and isinstance(transit_data['transit']['subject'], dict):
                        if "date_utc" in transit_data["transit"]["subject"]:
                            date_utc_str = transit_data["transit"]["subject"]["date_utc"]
                            if date_utc_str:
                                if date_utc_str.endswith('Z'): date_utc_str = date_utc_str[:-1] + '+00:00'
                                if '.' in date_utc_str:
                                    parts = date_utc_str.split('.')
                                    date_utc_str = parts[0] + '.' + parts[1][:6] # Truncate microseconds
                                    if '+' not in date_utc_str and '-' not in date_utc_str[10:]: date_utc_str += '+00:00'
                                reference_time = datetime.fromisoformat(date_utc_str)
                                print(f"[Bullseye] SUCCESS: Using reference time from transit.subject.date_utc: {reference_time}")

                # Attempt 2: Reconstruct from transit subject birth_data
                if reference_time is None and transit_data:
                     if ("transit" in transit_data and isinstance(transit_data['transit'], dict) and
                         "subject" in transit_data['transit'] and isinstance(transit_data['transit']['subject'], dict) and
                         "birth_data" in transit_data["transit"]["subject"] and isinstance(transit_data['transit']['subject']['birth_data'], dict)):
                         t_info = transit_data["transit"]["subject"]["birth_data"]
                         required_keys = ["date", "time"]
                         if all(k in t_info for k in required_keys) and t_info["date"] and t_info["time"]:
                             datetime_str = f"{t_info['date']} {t_info['time']}"
                             try:
                                 reference_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                                 print(f"[Bullseye] SUCCESS: Using reference time reconstructed from transit.subject.birth_data: {reference_time} (Assumed Local)")
                             except ValueError as parse_error:
                                 print(f"[Bullseye] DEBUG: Attempt 2 Error parsing date/time string '{datetime_str}': {parse_error}")

                # Attempt 3: Reconstruct from top-level transit info
                if reference_time is None and transit_data:
                    required_keys = ["transit_year", "transit_month", "transit_day", "transit_hour", "transit_minute"]
                    if all(k in transit_data for k in required_keys):
                        reference_time = datetime(
                            int(transit_data["transit_year"]), int(transit_data["transit_month"]), int(transit_data["transit_day"]),
                            int(transit_data["transit_hour"]), int(transit_data["transit_minute"])
                        )
                        print(f"[Bullseye] SUCCESS: Using reference time reconstructed from top-level transit_data keys: {reference_time} (Assumed Local)")

            except Exception as e:
                print(f"[Bullseye] ERROR: Exception during reference time extraction: {e}")

            # Fallback if no time could be extracted
            if reference_time is None:
                reference_time = datetime.now() # Use datetime.now() as fallback, but store it
                print(f"[Bullseye] WARNING: Could not extract reference time from transit_data. Falling back to current time: {reference_time}. Results may drift.")
            # --- End of added reference_time logic ---

            # Calculate D9 chart
            d9_chart = self.calculate_d9_chart(natal_data)
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
            
            # Store the fixed natal D9 7th house cusp for comparison
            natal_d9_seventh_house_cusp = seventh_house_cusp
            natal_d9_seventh_house_sign = list(ZODIAC_SIGNS.keys())[int(natal_d9_seventh_house_cusp / 30)]
            natal_d9_seventh_house_degree = natal_d9_seventh_house_cusp % 30

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
            transit_saturn_d9_pos = self.calculate_d9_position(saturn_pos)
            transit_saturn_d9_sign = list(ZODIAC_SIGNS.keys())[int(transit_saturn_d9_pos / 30)]
            transit_saturn_d9_degree = transit_saturn_d9_pos % 30
            print(f"Saturn D9 position: {transit_saturn_d9_pos}")
            
            # Calculate current angular distance between transit Saturn D9 position and the natal D9 7th house cusp
            angular_distance = abs(transit_saturn_d9_pos - natal_d9_seventh_house_cusp) % 360
            if angular_distance > 180:
                angular_distance = 360 - angular_distance
            
            # Check if we're currently in a Bullseye period (within 2.5° orb)
            is_current_bullseye = angular_distance <= 2.5
            print(f"Current angular distance: {angular_distance}, Is current bullseye: {is_current_bullseye}")
            
            # Calculate when the next Bullseye period will occur
            # We need to find when Saturn will be at the 7th house cusp position
            # Since we're working with D9 positions, we need to find when Saturn will be at the right position
            # in the tropical zodiac that corresponds to the D9 7th house cusp
            
            # REMOVED: The Ascendant makes a full rotation every day, so the bullseye occurs daily
            # REMOVED: We need to determine at what time of day this happens
            # NOTE: Bullseye period depends on TRANSIT SATURN D9 aligning with NATAL D9 7th Cusp.
            # It's driven by Saturn's slow movement, not the Ascendant's daily cycle.

            # REMOVED: now = datetime.now() # Use reference_time instead
            bullseye_periods = []
            
            # REMOVED: Get current Ascendant position from transit data if available
            # REMOVED: The Ascendant position is not needed for this revised calculation.

            # Check if currently in a Bullseye period
            if is_current_bullseye:
                 bullseye_periods.append({
                     "time": reference_time.strftime("%Y-%m-%d %H:%M"), # Time of calculation
                     "time_iso": reference_time.isoformat(),
                     "d9_seventh_cusp": {
                         "position": round(natal_d9_seventh_house_cusp, 2),
                         "sign": natal_d9_seventh_house_sign,
                         "degree": round(natal_d9_seventh_house_degree, 2)
                     },
                     "d9_saturn": {
                         "position": round(transit_saturn_d9_pos, 2),
                         "sign": transit_saturn_d9_sign,
                         "degree": round(transit_saturn_d9_degree, 2),
                         "is_retrograde": saturn_retrograde
                     },
                     "angular_distance": round(angular_distance, 2),
                     "is_current": True,
                     "duration": self.calculate_alignment_duration(
                         exact_time=reference_time, # Use reference time as 'exact' for current period
                         slower_planet="saturn",
                         alignment_type="Current Bullseye Period",
                         orb=2.5 # Orb for Bullseye is 2.5
                     )
                 })

            # REMOVED: Check each hour of today and tomorrow to find when Saturn is within 2.5° of the 7th house cusp in D9
            # REMOVED: This hourly check is not needed based on the definition. Saturn moves too slowly.

            # If no Bullseye periods found (i.e., not currently in one), estimate the next one.
            if not bullseye_periods:
                print("Not currently in a Bullseye period. Estimating next alignment...")

                # Define the orb boundaries
                orb = 2.5
                orb_start_pos = (natal_d9_seventh_house_cusp - orb) % 360
                orb_end_pos = (natal_d9_seventh_house_cusp + orb) % 360

                # Calculate Saturn's effective speed and direction
                motion_direction = -1 if saturn_retrograde else 1
                effective_speed = abs(saturn_daily_motion) # Use absolute speed for division

                # Initialize variables for estimation
                days_to_alignment = float('inf')
                shortest_distance_needed = float('inf')

                # Check if Saturn has meaningful motion
                if effective_speed < 0.001: # Consider Saturn stationary if speed is very low
                    print("Saturn is nearly stationary, cannot estimate next alignment reliably.")
                    days_to_alignment = float('inf') # Mark as unable to calculate
                else:
                    # Calculate shortest distance needed in the direction of motion
                    if motion_direction == 1: # Moving direct
                        # Target is the start of the orb (lower degree edge)
                        shortest_distance_needed = (orb_start_pos - transit_saturn_d9_pos) % 360
                    else: # Moving retrograde (motion_direction == -1)
                        # Target is the end of the orb (higher degree edge)
                        shortest_distance_needed = (transit_saturn_d9_pos - orb_end_pos) % 360

                    # Calculate days to alignment
                    if shortest_distance_needed >= 0:
                        days_to_alignment = shortest_distance_needed / effective_speed
                    else:
                         # Should not happen with % 360, but handle defensively
                        days_to_alignment = float('inf')

                # Proceed if a valid alignment time was calculated
                if days_to_alignment != float('inf') and days_to_alignment >= 0:
                    nearest_date = reference_time + timedelta(days=days_to_alignment)
                    
                    # Calculate projected Saturn D9 position at alignment
                    final_projected_saturn_pos = (saturn_pos + (days_to_alignment * saturn_daily_motion * motion_direction)) % 360
                    final_projected_saturn_d9_pos = self.calculate_d9_position(final_projected_saturn_pos)
                    
                    # Calculate angular distance at estimated alignment time (should be ~2.5)
                    proj_ang_dist_at_alignment = abs(final_projected_saturn_d9_pos - natal_d9_seventh_house_cusp) % 360
                    if proj_ang_dist_at_alignment > 180:
                        proj_ang_dist_at_alignment = 360 - proj_ang_dist_at_alignment

                    description = (
                        f"Estimated next Bullseye period starts around {nearest_date.strftime('%Y-%m-%d')}, "
                        f"in approximately {round(days_to_alignment)} days, when transit Saturn's D9 position "
                        f"({round(final_projected_saturn_d9_pos % 30, 1)}° {list(ZODIAC_SIGNS.keys())[int(final_projected_saturn_d9_pos / 30)]}) "
                        f"enters the {orb}° orb around your natal D9 7th house cusp "
                        f"({round(natal_d9_seventh_house_degree, 1)}° {ZODIAC_SIGNS[natal_d9_seventh_house_sign]})."
                    )

                    # Return the estimated alignment information
                    bullseye_periods.append({
                        "message": "Currently not in a Bullseye period. Providing next estimate.",
                        "next_estimated_bullseye": {
                            "estimated_date": nearest_date.strftime("%Y-%m-%d %H:%M"), # Use the estimated date/time
                            "days_away": round(days_to_alignment),
                            "description": description,
                            "projected_angular_distance": round(proj_ang_dist_at_alignment, 2) # Use distance at alignment
                        },
                        "is_estimated": True, # Mark as estimate
                        "d9_seventh_cusp": { # Include natal D9 7th cusp info
                            "position": round(natal_d9_seventh_house_cusp, 2),
                            "sign": natal_d9_seventh_house_sign,
                            "degree": round(natal_d9_seventh_house_degree, 2)
                        },
                        "current_saturn_d9": { # Include current D9 Saturn info
                            "position": round(transit_saturn_d9_pos, 2),
                            "sign": transit_saturn_d9_sign,
                            "degree": round(transit_saturn_d9_degree, 2),
                            "is_retrograde": saturn_retrograde
                        },
                        "current_angular_distance": round(angular_distance, 2) # Include initial angular distance
                    })

            # REMOVED: Old lookahead logic based on projecting ascendant and comparing hourly

            # Sort by time if bullseye_periods were found initially
            # (Now only contains current or estimated next)
            bullseye_periods.sort(key=lambda x: x.get("time", x.get("next_estimated_bullseye", {}).get("estimated_date", "9999")))

            return bullseye_periods

        except Exception as e:
            print(f"Error in calculate_bullseye_periods: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a properly formatted error response
            return [{
                "error": f"Error calculating Bullseye periods: {str(e)}",
                "message": "Could not calculate Bullseye periods due to an error",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")  # Add a time field # Keep now() here for error logging time
            }] 