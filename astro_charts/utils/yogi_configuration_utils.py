import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from .aspect_utils import PLANET_DAILY_MOTION
from .yogi_point_utils import get_ascendant_ruler, ZODIAC_SIGNS
from .alignment_utils import find_yearly_power_alignments
from .lucky_times_utils import calculate_triple_alignments

def calculate_yogi_configurations(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any], orb: float = 3.0) -> Dict[str, Any]:
        """Calculate when Yogi and Duplicate Yogi points are in significant configurations with the ascendant"""
        try:
            # Calculate Yogi Point
            print("Calculating Yogi Point")
            print(f"Transit Data: {transit_data}")
            yogi_point = self.calculate_yogi_point(natal_data)
            yogi_point_transit = self.calculate_yogi_point_transit(transit_data)
            print(f"Yogi Point: {yogi_point}")
            print(f"Yogi Point Transit: {yogi_point_transit}")
            
            # Get the sign of the Yogi Point
            yogi_sign_num = int(yogi_point / 30)
            yogi_sign = list(ZODIAC_SIGNS.keys())[yogi_sign_num]
            
            yogi_sign_transit_num = int(yogi_point_transit / 30)
            yogi_sign_transit = list(ZODIAC_SIGNS.keys())[yogi_sign_transit_num]
           
            
            # Determine the ruler of the Yogi Point sign (Duplicate Yogi)
            duplicate_yogi_planet = self.get_ascendant_ruler(yogi_sign, zodiac_type="Sidereal")
            
            duplicate_yogi_planet_transit = self.get_ascendant_ruler(yogi_sign_transit, zodiac_type="Sidereal")
            
            # Get the position of the Duplicate Yogi (the ruler planet of the Yogi Point sign)
            if duplicate_yogi_planet in transit_data["transit"]["subject"]["planets"]:
                duplicate_yogi_pos = transit_data["transit"]["subject"]["planets"][duplicate_yogi_planet]["abs_pos"]
                duplicate_yogi_retrograde = transit_data["transit"]["subject"]["planets"][duplicate_yogi_planet]["retrograde"]
                duplicate_yogi_sign_num = int(duplicate_yogi_pos / 30)
                duplicate_yogi_sign = list(ZODIAC_SIGNS.keys())[duplicate_yogi_sign_num]
                duplicate_yogi_degree = duplicate_yogi_pos % 30
            else:
                # Fallback if the ruler planet isn't in the transit chart
                duplicate_yogi_pos = (yogi_point + 180) % 360
                duplicate_yogi_retrograde = False
                duplicate_yogi_sign_num = int(duplicate_yogi_pos / 30)
                duplicate_yogi_sign = list(ZODIAC_SIGNS.keys())[duplicate_yogi_sign_num]
                duplicate_yogi_degree = duplicate_yogi_pos % 30
                duplicate_yogi_planet = "N/A"
            
            if duplicate_yogi_planet_transit in transit_data["transit"]["subject"]["planets"]:
                duplicate_yogi_pos_transit = transit_data["transit"]["subject"]["planets"][duplicate_yogi_planet_transit]["abs_pos"]
                duplicate_yogi_retrograde_transit = transit_data["transit"]["subject"]["planets"][duplicate_yogi_planet_transit]["retrograde"]
            else:
                duplicate_yogi_pos_transit = (yogi_point_transit + 180) % 360
                duplicate_yogi_retrograde_transit = False
            
            # Get current ascendant position
            ascendant_pos = None
            ascendant_sign = None
            ascendant_lord = None
            ascendant_lord_pos = None
            ascendant_lord_retrograde = False
            
            # Try to get ascendant position from transit data
            if "houses" in transit_data["transit"]["subject"] and "ascendant" in transit_data["transit"]["subject"]["houses"]:
                ascendant_pos = transit_data["transit"]["subject"]["houses"]["ascendant"]["abs_pos"]
                ascendant_sign = transit_data["transit"]["subject"]["houses"]["ascendant"]["sign"]
                ascendant_lord = self.get_ascendant_ruler(ascendant_sign, zodiac_type="Sidereal")
                
                if ascendant_lord in transit_data["transit"]["subject"]["planets"]:
                    ascendant_lord_pos = transit_data["transit"]["subject"]["planets"][ascendant_lord]["abs_pos"]
                    ascendant_lord_retrograde = transit_data["transit"]["subject"]["planets"][ascendant_lord]["retrograde"]
            
            # If we couldn't get ascendant position, try to estimate it from other data
            if ascendant_pos is None:
                print("Transit ascendant position not available, attempting fallbacks...")
                
                # First try using natal ascendant
                if "houses" in natal_data["subject"] and "ascendant" in natal_data["subject"]["houses"]:
                    ascendant_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
                    ascendant_sign = natal_data["subject"]["houses"]["ascendant"]["sign"]
                    print(f"Using natal ascendant as fallback: {ascendant_sign} at {ascendant_pos:.2f}°")
                    
                    # Get current sun position to make a rough adjustment to the ascendant
                    # This is a very simplified approximation but better than nothing
                    if "sun" in transit_data["transit"]["subject"]["planets"]:
                        transit_sun_pos = transit_data["transit"]["subject"]["planets"]["sun"]["abs_pos"]
                        natal_sun_pos = natal_data["subject"]["planets"]["sun"]["abs_pos"]
                        
                        # Adjust ascendant based on sun's movement (very approximate)
                        sun_movement = (transit_sun_pos - natal_sun_pos) % 360
                        # We don't want to advance the ascendant by the full sun movement
                        # as that would be too much, so scale it down
                        ascendant_adjustment = sun_movement * 0.1  # Scale factor (10%)
                        ascendant_pos = (ascendant_pos + ascendant_adjustment) % 360
                        print(f"Adjusted transit ascendant estimate: {ascendant_pos:.2f}°")
                
                # If still no ascendant, create an artificial one based on the current date/time
                if ascendant_pos is None:
                    now = datetime.now()
                    # Approximate ascendant based on time of day (very rough)
                    # 0 hours = 0° Aries, advancing 15° per hour
                    hour_of_day = now.hour + now.minute / 60
                    ascendant_pos = (hour_of_day * 15) % 360
                    ascendant_sign = list(ZODIAC_SIGNS.keys())[int(ascendant_pos / 30)]
                    print(f"Created artificial ascendant based on time: {ascendant_sign} at {ascendant_pos:.2f}°")
                
                # Get ascendant lord if we have the sign now
                if ascendant_sign:
                    ascendant_lord = self.get_ascendant_ruler(ascendant_sign, zodiac_type="Sidereal")
                    
                    if ascendant_lord in transit_data["transit"]["subject"]["planets"]:
                        ascendant_lord_pos = transit_data["transit"]["subject"]["planets"][ascendant_lord]["abs_pos"]
                        ascendant_lord_retrograde = transit_data["transit"]["subject"]["planets"][ascendant_lord]["retrograde"]
                    else:
                        # Fallback to sun if ascendant lord isn't available
                        ascendant_lord = "sun"
                        if "sun" in transit_data["transit"]["subject"]["planets"]:
                            ascendant_lord_pos = transit_data["transit"]["subject"]["planets"]["sun"]["abs_pos"]
                            ascendant_lord_retrograde = transit_data["transit"]["subject"]["planets"]["sun"]["retrograde"]
            
            # Even if ascendant lord information is incomplete, continue with configuration calculations
            # Just use default values for any missing data
            if ascendant_lord_pos is None and "sun" in transit_data["transit"]["subject"]["planets"]:
                ascendant_lord = "sun"
                ascendant_lord_pos = transit_data["transit"]["subject"]["planets"]["sun"]["abs_pos"]
                ascendant_lord_retrograde = transit_data["transit"]["subject"]["planets"]["sun"]["retrograde"]
            
            # If we still have no ascendant position, return basic configuration
            if ascendant_pos is None:
                return {
                    "duplicate_yogi": {
                        "planet": duplicate_yogi_planet,
                        "position": duplicate_yogi_pos,
                        "sign": duplicate_yogi_sign,
                        "degree": duplicate_yogi_degree,
                        "is_retrograde": duplicate_yogi_retrograde
                    },
                    "next_configuration": {
                        "type": "Unable to calculate configurations - Ascendant position not available",
                        "time": None,
                        "formatted_time": None
                    }
                }
            
            # Calculate time-based configurations
            now = datetime.now()
            
            # Calculate minutes until ascendant aligns with each point
            ascendant_minutes_per_degree = 4
            
            # Calculate for Yogi Point
            degrees_to_yogi = (yogi_point - ascendant_pos) % 360
            minutes_to_yogi = degrees_to_yogi * ascendant_minutes_per_degree
            yogi_time = now + timedelta(minutes=int(minutes_to_yogi))
            yogi_time_str = yogi_time.strftime("%Y-%m-%d %H:%M")
            
            # Calculate for Duplicate Yogi
            degrees_to_dup_yogi = (duplicate_yogi_pos - ascendant_pos) % 360
            minutes_to_dup_yogi = degrees_to_dup_yogi * ascendant_minutes_per_degree
            dup_yogi_time = now + timedelta(minutes=int(minutes_to_dup_yogi))
            dup_yogi_time_str = dup_yogi_time.strftime("%Y-%m-%d %H:%M")
            
            # Determine which configuration comes first
            next_config = {
                "type": "Yogi Point conjunct Ascendant",
                "time": yogi_time_str,
                "formatted_time": yogi_time_str,
                "minutes_away": int(minutes_to_yogi)
            } if minutes_to_yogi < minutes_to_dup_yogi else {
                "type": "Duplicate Yogi conjunct Ascendant",
                "time": dup_yogi_time_str,
                "formatted_time": dup_yogi_time_str,
                "minutes_away": int(minutes_to_dup_yogi)
            }
            
            # Calculate triple alignments
            triple_alignments = self.calculate_triple_alignments(
                yogi_point=yogi_point,
                duplicate_yogi=duplicate_yogi_pos,
                ascendant_pos=ascendant_pos,
                ascendant_lord_pos=ascendant_lord_pos if ascendant_lord_pos is not None else 0,
                ascendant_lord=ascendant_lord if ascendant_lord is not None else "sun",
                lord_daily_motion=PLANET_DAILY_MOTION.get(ascendant_lord if ascendant_lord is not None else "sun", 1.0),
                ascendant_lord_retrograde=ascendant_lord_retrograde,
                orb=orb
            )
            
            # Calculate yearly power alignments
            yearly_power_alignments = self.find_yearly_power_alignments(
                yogi_point=yogi_point,
                duplicate_yogi_planet=duplicate_yogi_planet,
                duplicate_yogi_pos=duplicate_yogi_pos,
                is_retrograde=duplicate_yogi_retrograde,
                ascendant_pos=ascendant_pos,
                orb=orb
            )
            
            result = {
                "duplicate_yogi": {
                    "planet": duplicate_yogi_planet,
                    "position": duplicate_yogi_pos,
                    "sign": duplicate_yogi_sign,
                    "degree": duplicate_yogi_degree,
                    "is_retrograde": duplicate_yogi_retrograde
                },
                "next_configuration": next_config,
                "ascendant_configurations": [
                    {
                        "type": "Yogi Point conjunct Ascendant",
                        "time": yogi_time_str,
                        "formatted_time": yogi_time_str,
                        "minutes_away": int(minutes_to_yogi)
                    },
                    {
                        "type": "Duplicate Yogi conjunct Ascendant",
                        "time": dup_yogi_time_str,
                        "formatted_time": dup_yogi_time_str,
                        "minutes_away": int(minutes_to_dup_yogi)
                    }
                ]
            }
            
            # Add triple alignments if available
            if triple_alignments:
                result["triple_alignments"] = triple_alignments
                
            # Add yearly power alignments if available
            if yearly_power_alignments:
                result["yearly_power_alignments"] = yearly_power_alignments
                
            return result
        except Exception as e:
            print(f"Error in calculate_yogi_configurations: {str(e)}")
            # Try to at least calculate the yearly power alignments if possible
            yearly_power_alignments = []
            try:
                if 'duplicate_yogi_planet' in locals() and 'duplicate_yogi_pos' in locals() and 'duplicate_yogi_retrograde' in locals():
                    if 'ascendant_pos' not in locals() or ascendant_pos is None:
                        # If we don't have ascendant position, try to get it from natal data
                        if "houses" in natal_data["subject"] and "ascendant" in natal_data["subject"]["houses"]:
                            ascendant_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
                    
                    if 'yogi_point' in locals() and ascendant_pos is not None:
                        # Calculate yearly power alignments
                        yearly_power_alignments = self.find_yearly_power_alignments(
                            yogi_point=yogi_point,
                            duplicate_yogi_planet=duplicate_yogi_planet,
                            duplicate_yogi_pos=duplicate_yogi_pos,
                            is_retrograde=duplicate_yogi_retrograde,
                            ascendant_pos=ascendant_pos,
                            orb=orb
                        )
            except Exception as inner_e:
                print(f"Error calculating yearly power alignments in fallback: {str(inner_e)}")
                
            # Return basic configuration without time-based calculations
            result = {
                "duplicate_yogi": {
                    "planet": duplicate_yogi_planet if 'duplicate_yogi_planet' in locals() else "unknown",
                    "position": duplicate_yogi_pos if 'duplicate_yogi_pos' in locals() else 0,
                    "sign": duplicate_yogi_sign if 'duplicate_yogi_sign' in locals() else "unknown",
                    "degree": duplicate_yogi_degree if 'duplicate_yogi_degree' in locals() else 0,
                    "is_retrograde": duplicate_yogi_retrograde if 'duplicate_yogi_retrograde' in locals() else False
                },
                "next_configuration": {
                    "type": f"Error calculating configurations: {str(e)}",
                    "time": None,
                    "formatted_time": None
                }
            }
            
            # Add yearly power alignments if we calculated them
            if yearly_power_alignments:
                result["yearly_power_alignments"] = yearly_power_alignments
                
            return result 