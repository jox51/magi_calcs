import json
from datetime import datetime, timedelta
import os
import math
import traceback
from typing import Dict, Any, List, Optional, Tuple

# Import utility modules
from ..utils.yogi_point_utils import (
    calculate_yogi_point, calculate_ava_yogi_point, get_ascendant_ruler, 
    calculate_d9_position, ZODIAC_SIGNS, calculate_yogi_point_transit
)
from ..utils.aspect_utils import (
    find_closest_aspect, find_last_aspect, calculate_alignment_duration,
    PLANET_DAILY_MOTION
)
from ..utils.dasha_utils import (
    calculate_dasha_lord, get_available_dasha_lord, determine_day_night_chart,
    DASHA_PERIODS
)
from ..utils.chart_utils import (
    sanitize_response_for_json, calculate_d9_chart, find_stacked_alignments,
    find_internally_stacked_dates, get_nearest_future_date
)
from ..utils.lucky_times_utils import (
    calculate_jupiter_pof_last_conjunction, get_next_venus_aspects,
    interpret_venus_aspect, calculate_triple_alignments
)
from ..utils.alignment_utils import (
    find_mutual_yogi_ruler_alignments, find_yearly_power_alignments
)

from ..utils.yogi_configuration_utils import calculate_yogi_configurations

from ..utils.stacked_utils import find_stacked_alignments, find_internally_stacked_dates

from ..utils.d9_utils import calculate_d9_chart, calculate_d9_position

from ..utils.bullseye_utils import calculate_bullseye_periods

from ..utils.pof_utils import calculate_part_of_fortune_rahu_conjunctions, calculate_part_of_fortune_regulus_conjunctions, calculate_part_of_fortune_lord_lagna_conjunctions, calculate_ascendant_part_of_fortune_conjunctions

from ..utils.location_utils import calculate_location_specific_yogi_alignments

class VedicLuckyTimesService:
    def __init__(self):
        pass

    # These methods are now imported from utils, but kept as wrappers for backward compatibility
    def get_ascendant_ruler(self, ascendant_sign: str, zodiac_type: str = None) -> str:
        return get_ascendant_ruler(ascendant_sign, zodiac_type)

    def calculate_dasha_lord(self, moon_nakshatra_deg: float, birth_date: str, target_date: str) -> str:
        return calculate_dasha_lord(moon_nakshatra_deg, birth_date, target_date)

    def get_available_dasha_lord(self, dasha_lord: str, available_planets: List[str]) -> str:
        return get_available_dasha_lord(dasha_lord, available_planets)

    def find_closest_aspect(self, current_pos: float, daily_motion: float, yogi_point: float, is_retrograde: bool = False, orb: float = 3.0, reference_time: Optional[datetime] = None) -> Dict[str, Any]:
        return find_closest_aspect(current_pos, daily_motion, yogi_point, is_retrograde, orb, reference_time)

    def calculate_yogi_point(self, natal_data: Dict[str, Any]) -> float:
        return calculate_yogi_point(natal_data)
    
    def calculate_yogi_point_transit(self, transit_data: Dict[str, Any]) -> float:
        return calculate_yogi_point_transit(transit_data)

    def sanitize_response_for_json(self, response: Dict[str, Any]) -> Dict[str, Any]:
        return sanitize_response_for_json(response)

    def find_last_aspect(self, current_pos: float, daily_motion: float, yogi_point: float, is_retrograde: bool = False, orb: float = 3.0, reference_time: Optional[datetime] = None) -> Dict[str, Any]:
        return find_last_aspect(current_pos, daily_motion, yogi_point, is_retrograde, orb, reference_time)

    def calculate_ava_yogi_point(self, yogi_point: float) -> float:
        return calculate_ava_yogi_point(yogi_point)

    def calculate_d9_position(self, zodiac_position: float) -> float:
        return calculate_d9_position(zodiac_position)

    def calculate_d9_chart(self, natal_data: Dict[str, Any]) -> Dict[str, Any]:
        return calculate_d9_chart(natal_data)

    def find_stacked_alignments(self, all_dates_list: List[Dict[str, Any]], 
                             pof_rahu_data: List[Dict[str, Any]] = None,
                             pof_regulus_data: List[Dict[str, Any]] = None,
                             pof_lord_lagna_data: List[Dict[str, Any]] = None,
                             time_window_hours: int = 12) -> List[Dict[str, Any]]:
        return find_stacked_alignments(all_dates_list, pof_rahu_data, pof_regulus_data, pof_lord_lagna_data, time_window_hours)

    def find_internally_stacked_dates(self, all_dates_list: List[Dict[str, Any]], 
                                   exclude_same_type: bool = True) -> List[Dict[str, Any]]:
        return find_internally_stacked_dates(all_dates_list, exclude_same_type)

    def determine_day_night_chart(self, sun_pos: float, asc_pos: float, natal_data: Dict[str, Any] = None, 
                            label: str = "") -> bool:
        return determine_day_night_chart(sun_pos, asc_pos, natal_data, label)

    def calculate_alignment_duration(self, exact_time: datetime, slower_planet: str = None, alignment_type: str = "conjunction", orb: float = 3.0) -> Dict[str, Any]:
        return calculate_alignment_duration(exact_time, slower_planet, alignment_type, orb)
    
    # Use the extracted utility functions
    def calculate_jupiter_pof_last_conjunction(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any]) -> Dict[str, Any]:
        return calculate_jupiter_pof_last_conjunction(natal_data, transit_data)
    
    def get_next_venus_aspects(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any], orb: float = 3.0) -> Dict[str, Any]:
        return get_next_venus_aspects(natal_data, transit_data, orb)
    
    def interpret_venus_aspect(self, aspect_type: str, point_type: str = "yogi") -> str:
        return interpret_venus_aspect(aspect_type, point_type)
    
    def calculate_triple_alignments(self, yogi_point: float, duplicate_yogi: float, 
                              ascendant_pos: float, ascendant_lord_pos: float,
                              ascendant_lord: str, lord_daily_motion: float,
                              ascendant_lord_retrograde: bool, orb: float = 3.0) -> List[Dict[str, Any]]:
        return calculate_triple_alignments(yogi_point, duplicate_yogi, ascendant_pos, ascendant_lord_pos, 
                                          ascendant_lord, lord_daily_motion, ascendant_lord_retrograde, orb)
    
    def find_mutual_yogi_ruler_alignments(self, yogi_point: float, duplicate_yogi_planet: str, duplicate_yogi_pos: float, 
                                        ascendant_pos: float, transit_data: Dict[str, Any], num_forecasts: int = 3) -> List[Dict[str, Any]]:
        return find_mutual_yogi_ruler_alignments(yogi_point, duplicate_yogi_planet, duplicate_yogi_pos, 
                                               ascendant_pos, transit_data, num_forecasts)
    
    def find_yearly_power_alignments(self, yogi_point: float, duplicate_yogi_planet: str, 
                                    duplicate_yogi_pos: float, is_retrograde: bool,
                                    ascendant_pos: float, orb: float = 3.0) -> List[Dict[str, Any]]:
        return find_yearly_power_alignments(yogi_point, duplicate_yogi_planet, duplicate_yogi_pos, 
                                           is_retrograde, ascendant_pos, orb)
    
    # The rest of the service methods that haven't been moved to utility files...
    def process_vedic_lucky_times(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any], birth_date: str, from_date: str, name: str, orb: float = 3.0,
                                 location_specific_alignments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process vedic lucky times data and generate comprehensive results
        
        Args:
            natal_data: The natal chart data
            transit_data: The transit chart data
            birth_date: The birth date in YYYY-MM-DD format
            from_date: The date to calculate from in YYYY-MM-DD format
            name: The person's name
            orb: The orb value to use for aspects (default: 3.0)
            location_specific_alignments: Optional pre-calculated location-specific alignments
            
        Returns:
            Dictionary containing comprehensive results
        """
        try:
            
            print(f"Natal data: {natal_data}")
            print(f"Transit data: {transit_data}")

            # --- Determine the reference time for calculations (Added) ---
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
                                print(f"[ProcessVedic] SUCCESS: Using reference time from transit.subject.date_utc: {reference_time}")

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
                                 print(f"[ProcessVedic] SUCCESS: Using reference time reconstructed from transit.subject.birth_data: {reference_time} (Assumed Local)")
                             except ValueError as parse_error:
                                 print(f"[ProcessVedic] DEBUG: Attempt 2 Error parsing date/time string '{datetime_str}': {parse_error}")

                # Attempt 3: Reconstruct from top-level transit info
                if reference_time is None and transit_data:
                    required_keys = ["transit_year", "transit_month", "transit_day", "transit_hour", "transit_minute"]
                    if all(k in transit_data for k in required_keys):
                        reference_time = datetime(
                            int(transit_data["transit_year"]), int(transit_data["transit_month"]), int(transit_data["transit_day"]),
                            int(transit_data["transit_hour"]), int(transit_data["transit_minute"])
                        )
                        print(f"[ProcessVedic] SUCCESS: Using reference time reconstructed from top-level transit_data keys: {reference_time} (Assumed Local)")

            except Exception as e:
                print(f"[ProcessVedic] ERROR: Exception during reference time extraction: {e}")

            # Fallback if no time could be extracted
            if reference_time is None:
                reference_time = datetime.now()
                print(f"[ProcessVedic] WARNING: Could not extract reference time from transit_data. Falling back to current time: {reference_time}. Results may drift.")
            # --- End of added reference_time logic ---

            # Calculate Yogi Point
            yogi_point = self.calculate_yogi_point(natal_data)
            
            # Calculate Ava Yogi Point (unlucky point)
            ava_yogi_point = self.calculate_ava_yogi_point(yogi_point)
            
            # Calculate when Jupiter was last conjunct with Part of Fortune
            jupiter_pof_data = self.calculate_jupiter_pof_last_conjunction(natal_data, transit_data)
            
            # Add Jupiter-POF next conjunction to dates_summary when we build the response
            if "next_conjunction" in jupiter_pof_data:
                next_conj_data = jupiter_pof_data["next_conjunction"]
                pof_sign = jupiter_pof_data["part_of_fortune"]["sign"]
                pof_degree = jupiter_pof_data["part_of_fortune"]["degree"]
                
                jupiter_pof_date = {
                    "date": next_conj_data["date"],
                    "name": "jupiter_pof_conjunction",
                    "description": f"Jupiter conjunct Natal Part of Fortune in {pof_sign} {pof_degree}°",
                    "days_away": next_conj_data["days_away"],
                    "significance": "Jupiter conjunct your natal Part of Fortune brings a period of expanded fortune and opportunity that occurs approximately once every 12 years.",
                    "duration": next_conj_data["duration"]
                }
            
            # Calculate D9 chart
            d9_chart = self.calculate_d9_chart(natal_data)
            print(f"D9 chart: {d9_chart}")
            
            # Get transit planets
            transit_planets = transit_data["transit"]["subject"]["planets"]
            print(f"Transit planets: {transit_planets}")
            
            # Get ascendant ruler
            ascendant_sign = natal_data["subject"]["houses"]["ascendant"]["sign"]
            ascendant_ruler = self.get_ascendant_ruler(ascendant_sign, zodiac_type="Sidereal")
            
            # Get ascendant ruler position
            if ascendant_ruler in transit_planets:
                current_ruler_pos = transit_planets[ascendant_ruler]["abs_pos"]
                current_ruler_sign = transit_planets[ascendant_ruler]["sign"]
                current_ruler_degree = current_ruler_pos % 30
                ruler_retrograde = transit_planets[ascendant_ruler]["retrograde"]
            else:
                # Fallback to Sun if ruler not in transit
                ascendant_ruler = "sun"
                current_ruler_pos = transit_planets["sun"]["abs_pos"]
                current_ruler_sign = transit_planets["sun"]["sign"]
                current_ruler_degree = current_ruler_pos % 30
                ruler_retrograde = transit_planets["sun"]["retrograde"]
            
            # Calculate next aspect of ruler to Yogi Point
            ruler_daily_motion = PLANET_DAILY_MOTION.get(ascendant_ruler, 1.0)
            ruler_next_aspect = self.find_closest_aspect(
                current_pos=current_ruler_pos,
                daily_motion=ruler_daily_motion,
                yogi_point=yogi_point,
                is_retrograde=ruler_retrograde,
                orb=orb,  # Use provided orb
                reference_time=reference_time # Pass reference time
            )
            
            # Calculate last aspect of ruler to Yogi Point
            ruler_last_aspect = self.find_last_aspect(
                current_pos=current_ruler_pos,
                daily_motion=ruler_daily_motion,
                yogi_point=yogi_point,
                is_retrograde=ruler_retrograde,
                orb=orb,  # Use provided orb
                reference_time=reference_time # Pass reference time
            )
            
            # Calculate next aspect of ruler to Ava Yogi Point (unlucky point)
            ruler_next_ava_aspect = self.find_closest_aspect(
                current_pos=current_ruler_pos,
                daily_motion=ruler_daily_motion,
                yogi_point=ava_yogi_point,
                is_retrograde=ruler_retrograde,
                orb=orb,  # Use provided orb
                reference_time=reference_time # Pass reference time
            )
            
            # Calculate last aspect of ruler to Ava Yogi Point
            ruler_last_ava_aspect = self.find_last_aspect(
                current_pos=current_ruler_pos,
                daily_motion=ruler_daily_motion,
                yogi_point=ava_yogi_point,
                is_retrograde=ruler_retrograde,
                orb=orb,  # Use provided orb
                reference_time=reference_time # Pass reference time
            )
            
            # Calculate current Dasha lord
            moon_nakshatra_deg = natal_data["subject"]["planets"]["moon"]["abs_pos"]
            dasha_lord = self.calculate_dasha_lord(moon_nakshatra_deg, birth_date, from_date)
            dasha_lord = self.get_available_dasha_lord(dasha_lord, list(transit_planets.keys()))
            
            # Calculate Dasha lord position
            current_dasha_pos = transit_planets[dasha_lord]["abs_pos"]
            current_dasha_sign = transit_planets[dasha_lord]["sign"]
            current_dasha_degree = current_dasha_pos % 30
            dasha_retrograde = transit_planets[dasha_lord]["retrograde"]
            
            # Calculate next aspect of Dasha lord to Yogi Point
            dasha_daily_motion = PLANET_DAILY_MOTION.get(dasha_lord, 1.0)
            dasha_next_aspect = self.find_closest_aspect(
                current_pos=current_dasha_pos,
                daily_motion=dasha_daily_motion,
                yogi_point=yogi_point,
                is_retrograde=dasha_retrograde,
                orb=orb,  # Use provided orb
                reference_time=reference_time # Pass reference time
            )
            
            # Calculate last aspect of Dasha lord to Yogi Point
            dasha_last_aspect = self.find_last_aspect(
                current_pos=current_dasha_pos,
                daily_motion=dasha_daily_motion,
                yogi_point=yogi_point,
                is_retrograde=dasha_retrograde,
                orb=orb,  # Use provided orb
                reference_time=reference_time # Pass reference time
            )
            
            # Calculate next aspect of Dasha lord to Ava Yogi Point
            dasha_next_ava_aspect = self.find_closest_aspect(
                current_pos=current_dasha_pos,
                daily_motion=dasha_daily_motion,
                yogi_point=ava_yogi_point,
                is_retrograde=dasha_retrograde,
                orb=orb,  # Use provided orb
                reference_time=reference_time # Pass reference time
            )
            
            # Calculate last aspect of Dasha lord to Ava Yogi Point
            dasha_last_ava_aspect = self.find_last_aspect(
                current_pos=current_dasha_pos,
                daily_motion=dasha_daily_motion,
                yogi_point=ava_yogi_point,
                is_retrograde=dasha_retrograde,
                orb=orb,  # Use provided orb
                reference_time=reference_time # Pass reference time
            )
            
            # Verify that Yogi Point and Ava Yogi Point aspects have different dates
            # If they're the same, something went wrong in the calculation, so we'll slightly adjust
            
            # Check ascendant ruler next aspects
            if ruler_next_aspect.get("estimated_date") == ruler_next_ava_aspect.get("estimated_date"):
                print("Warning: Ruler next aspect dates are the same for Yogi and Ava Yogi. Recalculating...")
                # Recalculate with a slight adjustment to ensure different results
                ruler_next_ava_aspect = self.find_closest_aspect(
                    current_pos=current_ruler_pos,
                    daily_motion=ruler_daily_motion * 0.99,  # Slight adjustment to motion
                    yogi_point=ava_yogi_point,
                    is_retrograde=ruler_retrograde,
                    orb=orb,  # Use provided orb
                    reference_time=reference_time # Pass reference time
                )
            
            # Check ascendant ruler last aspects
            if ruler_last_aspect.get("estimated_date") == ruler_last_ava_aspect.get("estimated_date"):
                print("Warning: Ruler last aspect dates are the same for Yogi and Ava Yogi. Recalculating...")
                # Recalculate with a slight adjustment
                ruler_last_ava_aspect = self.find_last_aspect(
                    current_pos=current_ruler_pos,
                    daily_motion=ruler_daily_motion * 0.99,  # Slight adjustment to motion
                    yogi_point=ava_yogi_point,
                    is_retrograde=ruler_retrograde,
                    orb=orb,  # Use provided orb
                    reference_time=reference_time # Pass reference time
                )
            
            # Check dasha lord next aspects
            if dasha_next_aspect.get("estimated_date") == dasha_next_ava_aspect.get("estimated_date"):
                print("Warning: Dasha next aspect dates are the same for Yogi and Ava Yogi. Recalculating...")
                # Recalculate with a slight adjustment
                dasha_next_ava_aspect = self.find_closest_aspect(
                    current_pos=current_dasha_pos,
                    daily_motion=dasha_daily_motion * 0.99,  # Slight adjustment to motion
                    yogi_point=ava_yogi_point,
                    is_retrograde=dasha_retrograde,
                    orb=orb,  # Use provided orb
                    reference_time=reference_time # Pass reference time
                )
            
            # Check dasha lord last aspects
            if dasha_last_aspect.get("estimated_date") == dasha_last_ava_aspect.get("estimated_date"):
                print("Warning: Dasha last aspect dates are the same for Yogi and Ava Yogi. Recalculating...")
                # Recalculate with a slight adjustment
                dasha_last_ava_aspect = self.find_last_aspect(
                    current_pos=current_dasha_pos,
                    daily_motion=dasha_daily_motion * 0.99,  # Slight adjustment to motion
                    yogi_point=ava_yogi_point,
                    is_retrograde=dasha_retrograde,
                    orb=orb,  # Use provided orb
                    reference_time=reference_time # Pass reference time
                )
            
            # Get Yogi configurations if available
            has_yogi_config = True
            try:
                yogi_configurations = self.calculate_yogi_configurations(natal_data, transit_data, orb)
            except Exception as e:
                print(f"Error calculating Yogi configurations: {str(e)}")
                yogi_configurations = {
                    "duplicate_yogi": {
                        "planet": "unknown",
                        "position": 0,
                        "sign": "unknown",
                        "degree": 0,
                        "is_retrograde": False
                    },
                    "next_configuration": {
                        "type": f"Error calculating configurations: {str(e)}",
                        "time": None,
                        "formatted_time": None
                    }
                }
                has_yogi_config = False
            
            # Prepare response
            response = {
                "yogi_point": {
                    "absolute_position": yogi_point,
                    "sign": list(ZODIAC_SIGNS.keys())[int(yogi_point / 30)],
                    "degree": round(yogi_point % 30, 2)
                },
                "ava_yogi_point": {
                    "absolute_position": ava_yogi_point,
                    "sign": list(ZODIAC_SIGNS.keys())[int(ava_yogi_point / 30)],
                    "degree": round(ava_yogi_point % 30, 2)
                },
                "jupiter_pof_conjunctions": jupiter_pof_data,
                "ascendant_info": {
                    "sign": ZODIAC_SIGNS.get(ascendant_sign, ascendant_sign),
                    "ruler": ascendant_ruler,
                    "current_position": {
                        "absolute": round(current_ruler_pos, 3),
                        "sign": current_ruler_sign,
                        "degree": round(current_ruler_degree, 2),
                        "is_retrograde": ruler_retrograde
                    },
                    "next_aspect": ruler_next_aspect,
                    "last_aspect": ruler_last_aspect
                },
                "dasha_info": {
                    "current_dasha_lord": dasha_lord,
                    "birth_moon_nakshatra_deg": moon_nakshatra_deg,
                    "current_position": {
                        "absolute": round(current_dasha_pos, 3),
                        "sign": current_dasha_sign,
                        "degree": round(current_dasha_degree, 2),
                        "is_retrograde": dasha_retrograde
                    },
                    "next_aspect": dasha_next_aspect,
                    "last_aspect": dasha_last_aspect
                },
                "next_transits": {
                    "ascendant_ruler": {
                        "planet": ascendant_ruler,
                        "date": ruler_next_aspect.get("estimated_date"),
                        "aspect": ruler_next_aspect.get("type"),
                        "days_away": ruler_next_aspect.get("estimated_days"),
                        "is_retrograde": ruler_retrograde,
                        "duration": ruler_next_aspect.get("duration")
                    },
                    "dasha_lord": {
                        "planet": dasha_lord,
                        "date": dasha_next_aspect.get("estimated_date"),
                        "aspect": dasha_next_aspect.get("type"),
                        "days_away": dasha_next_aspect.get("estimated_days"),
                        "is_retrograde": dasha_retrograde,
                        "duration": dasha_next_aspect.get("duration")
                    }
                },
                "last_transits": {
                    "ascendant_ruler": {
                        "planet": ascendant_ruler,
                        "date": ruler_last_aspect.get("estimated_date"),
                        "aspect": ruler_last_aspect.get("type"),
                        "days_ago": ruler_last_aspect.get("estimated_days_ago"),
                        "is_retrograde": ruler_retrograde,
                        "duration": ruler_last_aspect.get("duration")
                    },
                    "dasha_lord": {
                        "planet": dasha_lord,
                        "date": dasha_last_aspect.get("estimated_date"),
                        "aspect": dasha_last_aspect.get("type"),
                        "days_ago": dasha_last_aspect.get("estimated_days_ago"),
                        "is_retrograde": dasha_retrograde,
                        "duration": dasha_last_aspect.get("duration")
                    }
                },
                "ava_yogi_transits": {
                    "next": {
                        "ascendant_ruler": {
                            "planet": ascendant_ruler,
                            "date": ruler_next_ava_aspect.get("estimated_date"),
                            "aspect": ruler_next_ava_aspect.get("type"),
                            "days_away": ruler_next_ava_aspect.get("estimated_days"),
                            "is_retrograde": ruler_retrograde,
                            "duration": ruler_next_ava_aspect.get("duration")
                        },
                        "dasha_lord": {
                            "planet": dasha_lord,
                            "date": dasha_next_ava_aspect.get("estimated_date"),
                            "aspect": dasha_next_ava_aspect.get("type"),
                            "days_away": dasha_next_ava_aspect.get("estimated_days"),
                            "is_retrograde": dasha_retrograde,
                            "duration": dasha_next_ava_aspect.get("duration")
                        }
                    },
                    "last": {
                        "ascendant_ruler": {
                            "planet": ascendant_ruler,
                            "date": ruler_last_ava_aspect.get("estimated_date"),
                            "aspect": ruler_last_ava_aspect.get("type"),
                            "days_ago": ruler_last_ava_aspect.get("estimated_days_ago"),
                            "is_retrograde": ruler_retrograde,
                            "duration": ruler_last_ava_aspect.get("duration")
                        },
                        "dasha_lord": {
                            "planet": dasha_lord,
                            "date": dasha_last_ava_aspect.get("estimated_date"),
                            "aspect": dasha_last_ava_aspect.get("type"),
                            "days_ago": dasha_last_ava_aspect.get("estimated_days_ago"),
                            "is_retrograde": dasha_retrograde,
                            "duration": dasha_last_ava_aspect.get("duration")
                        }
                    }
                }
            }
            
            # Add yogi configurations if available
            if has_yogi_config:
                response["yogi_configurations"] = {
                    "duplicate_yogi": yogi_configurations["duplicate_yogi"],
                    "next_configuration": yogi_configurations["next_configuration"] 
                }
                
                # Add ascendant configurations if available
                if "ascendant_configurations" in yogi_configurations:
                    response["yogi_configurations"]["ascendant_configurations"] = yogi_configurations["ascendant_configurations"]
                
                # Add lord configurations if available
                if "lord_configurations" in yogi_configurations:
                    response["yogi_configurations"]["lord_configurations"] = yogi_configurations["lord_configurations"]
                
                # Add triple alignments if they exist
                if "triple_alignments" in yogi_configurations:
                    response["yogi_configurations"]["triple_alignments"] = yogi_configurations["triple_alignments"]
                    
                # Add yearly power alignments if they exist
                if "yearly_power_alignments" in yogi_configurations:
                    response["yogi_configurations"]["yearly_power_alignments"] = yogi_configurations["yearly_power_alignments"]
            
            # Add interpretation
            response["interpretation"] = {}
            
            # Initialize dates_summary dictionary early
            response["dates_summary"] = {
                "person_name": name,
                "asc_pof_conjunction_dates": [],
                "location_daily_dates": [],
                "location_power_dates": [],
                "yearly_power_dates": [],
                "bullseye_periods": [], # Ensures bullseye_periods is always initialized
                "ascendant_ruler_dates": [],
                "dasha_lord_dates": [],
                "jupiter_pof_dates": [],
                "lucky_dates": [],
                "unlucky_dates": []
            }
            
            # Add person name 
            response["person_name"] = name
            
            # Add D9 chart to response
            # response["d9_chart"] = d9_chart
            
            # Add interpretation for yearly power alignments if available
            if has_yogi_config and "yearly_power_alignments" in yogi_configurations and yogi_configurations["yearly_power_alignments"]:
                try:
                    next_power = yogi_configurations["yearly_power_alignments"][0]
                    if next_power and "type" in next_power and "formatted_time" in next_power:
                        response["interpretation"]["yearly_power_alignment"] = (
                            f"A rare and powerful {next_power['type']} will occur on {next_power['formatted_time']}. "
                            f"This is an extraordinary alignment that happens only about once per year, "
                            f"when the Yogi Point and its ruling planet form a mutual aspect while one of them aligns with the Ascendant. "
                            f"This creates an exceptionally powerful time for spiritual practices, major beginnings, or important life events."
                        )
                except Exception as e:
                    # If there's an error accessing yearly power alignments, silently continue
                    print(f"Error adding yearly power alignment interpretation: {str(e)}")
            
            # Add D9 interpretation to the response
            response["interpretation"]["d9_yogi_point"] = f"In your D9 chart, your Yogi Point is at {round(d9_chart['yogi_point']['d9_degree'], 2)}° {ZODIAC_SIGNS[d9_chart['yogi_point']['d9_sign']]}, revealing deeper spiritual qualities and karmic patterns."
            
            # If D9 Lagna is available, add interpretation
            if "lagna" in d9_chart and d9_chart["lagna"]:
                response["interpretation"]["d9_lagna"] = f"Your D9 Ascendant is in {ZODIAC_SIGNS[d9_chart['lagna']['d9_sign']]}, indicating your spiritual partnership tendencies and deeper spiritual purpose."
            
            # Calculate Bullseye periods
            bullseye_periods = self.calculate_bullseye_periods(natal_data, transit_data)
            
            # Add Bullseye periods to response
            response["bullseye_periods"] = bullseye_periods
            
            # --- Adjusted Bullseye Interpretation and Summary Logic ---
            bullseye_interpretation = "Bullseye period information is not available or in an unexpected format."
            if bullseye_periods and isinstance(bullseye_periods, list) and bullseye_periods:
                period_data = bullseye_periods[0] # Process the first entry

                # Handle error case first
                if "error" in period_data:
                    error_msg = period_data.get("error", "Unknown error")
                    bullseye_interpretation = f"Bullseye period information could not be calculated: {error_msg}"
                    # Clear the summary entry if there was an error
                    response["dates_summary"]["bullseye_periods"] = []
                    print(f"Bullseye period calculation returned an error: {error_msg} - clearing dates_summary entry")
                
                # Handle current bullseye period
                elif "time" in period_data and period_data.get("is_current"):
                    current_bullseye = period_data
                    bullseye_interpretation = (
                        f"You are currently in a Bullseye period (active from {current_bullseye['duration']['start_time']} to {current_bullseye['duration']['end_time']}) "
                        f"with Saturn at {round(current_bullseye['d9_saturn']['degree'], 1)}° "
                        f"{ZODIAC_SIGNS[current_bullseye['d9_saturn']['sign']]} in your D9 chart, "
                        f"within {round(current_bullseye['angular_distance'], 1)}° of your natal D9 7th house cusp "
                        f"({round(current_bullseye['d9_seventh_cusp']['degree'], 1)}° {ZODIAC_SIGNS[current_bullseye['d9_seventh_cusp']['sign']]}). "
                        f"This is an auspicious time for important decisions and spiritual practices."
                    )
                    # Add to dates_summary
                    days_away = 0 # Current period
                    response["dates_summary"]["bullseye_periods"] = [{
                        "date": current_bullseye["time"],
                        "name": "current_bullseye_period",
                        "description": "Current Bullseye Period - Saturn aligns with D9 7th house cusp",
                        "significance": "Auspicious time for decisions and spiritual practices",
                        "duration": current_bullseye.get("duration"),
                        "days_away": round(days_away)
                    }]
                    print(f"Added current Bullseye period {current_bullseye['time']} to dates_summary")

                # Handle estimation cases (found estimate OR could not estimate)
                elif "message" in period_data and "next_estimated_bullseye" in period_data:
                    estimate_info = period_data["next_estimated_bullseye"]
                    current_saturn_info = period_data["current_saturn_d9"]
                    cusp_info = period_data["d9_seventh_cusp"]
                    current_distance = period_data["current_angular_distance"]

                    # Check if an actual date was estimated
                    if estimate_info.get("estimated_date"):
                        bullseye_interpretation = estimate_info.get("description", "Could not generate detailed interpretation for estimated Bullseye period.")
                        # Add estimate to dates_summary
                        response["dates_summary"]["bullseye_periods"] = [{
                            "date": estimate_info["estimated_date"],
                            "name": "next_estimated_bullseye",
                            "description": "Estimated Next Bullseye Period",
                            "significance": bullseye_interpretation,
                            "days_away": estimate_info.get("days_away"),
                            "is_estimated": True,
                            "duration": None # Duration is harder to estimate long-term
                        }]
                        print(f"Added estimated next Bullseye period {estimate_info['estimated_date']} to dates_summary")
                    else: # Handle "Could not estimate" case
                        bullseye_interpretation = (
                            f"No Bullseye period is currently active. {estimate_info.get('description', '')} "
                            f"Current Transit Saturn D9 is at {round(current_saturn_info['degree'], 1)}° {ZODIAC_SIGNS[current_saturn_info['sign']]} "
                            f"and Natal D9 7th Cusp is at {round(cusp_info['degree'], 1)}° {ZODIAC_SIGNS[cusp_info['sign']]}, "
                            f"with an angular distance of {round(current_distance, 1)}°. An alignment requires this distance to be within 2.5°."
                        )
                        # Clear the summary entry as no date was found
                        response["dates_summary"]["bullseye_periods"] = []
                        print(f"Bullseye period message: '{period_data['message']}' but no estimated date found - clearing dates_summary entry")

                # Fallback for unexpected format
                else:
                    bullseye_interpretation = "Bullseye period information is not available or in an unexpected format."
                    # Clear the summary entry
                    response["dates_summary"]["bullseye_periods"] = []
                    print("Bullseye period data found, but format not recognized for dates_summary - clearing dates_summary entry.")
            
            # Handle case where bullseye_periods is empty/None
            else:
                bullseye_interpretation = "No Bullseye period data was returned."
                # Ensure the summary entry is empty
                response["dates_summary"]["bullseye_periods"] = []
                print("No Bullseye period data returned - ensuring dates_summary entry is empty.")

            response["interpretation"]["bullseye_period"] = bullseye_interpretation
            # --- End of Adjusted Bullseye Logic ---
            
            # Calculate when the ascendant will conjunct the natal Part of Fortune (next 7 days)
            try:
                # Debug transit structure before calculation
                print("Transit data structure debug:")
                if "transit" in transit_data:
                    print(f"Transit keys: {list(transit_data['transit'].keys())}")
                    if "subject" in transit_data["transit"]:
                        print(f"Transit subject keys: {list(transit_data['transit']['subject'].keys())}")
                        if "houses" in transit_data["transit"]["subject"]:
                            print(f"Houses available: {transit_data['transit']['subject']['houses'].keys()}")
                        else:
                            print("Transit houses not directly available in the expected structure")
                            # Check houses in other locations if needed
                    if "houses" in transit_data:
                        print(f"Houses keys at root: {list(transit_data['houses'].keys())}")
                
                pof_asc_conjunctions = self.calculate_ascendant_part_of_fortune_conjunctions(
                    natal_data=natal_data,
                    transit_data=transit_data,
                    num_days=7,
                    orb=orb  # Pass the user-provided orb parameter
                )
                
                # Add Part of Fortune-Ascendant conjunctions to the response
                response["ascendant_part_of_fortune_conjunctions"] = pof_asc_conjunctions
                
                # Add interpretation to the main interpretation section
                if pof_asc_conjunctions and not any("error" in conj for conj in pof_asc_conjunctions):
                    next_conj = pof_asc_conjunctions[0]
                    pof_sign = next_conj["part_of_fortune"]["sign"]
                    pof_degree = next_conj["part_of_fortune"]["degree"]
                    conj_date = next_conj["conjunction_date"]
                    
                    if "hours_away" in next_conj and next_conj["hours_away"] is not None:
                        hours_text = f" ({next_conj['hours_away']} hours from now)"
                    else:
                        hours_text = ""
                    
                    estimation_method = next_conj.get("estimation_method", "")
                    method_text = ""
                    if estimation_method == "sun_position":
                        method_text = " (estimated based on sun position)"
                    elif estimation_method == "time_based":
                        method_text = " (estimated based on time of day)"
                    elif estimation_method == "simple_time":
                        method_text = " (approximated)"
                    
                    response["interpretation"]["ascendant_pof_conjunction"] = (
                        f"The ascendant will next conjunct your natal Part of Fortune at {round(pof_degree, 2)}° {ZODIAC_SIGNS[pof_sign]} "
                        f"on {conj_date}{hours_text}{method_text}. This daily 15-20 minute window is excellent for starting new ventures, "
                        f"making important decisions, or any activity where you want to align with fortunate energies."
                    )
                else:
                    # Handle error case with a graceful message
                    response["interpretation"]["ascendant_pof_conjunction"] = (
                        "We couldn't precisely calculate when the ascendant will conjunct your natal Part of Fortune. "
                        "This typically happens once per day for about 15-20 minutes and is an excellent time for starting new ventures."
                    )
            except Exception as e:
                print(f"Error calculating ascendant-partof fortune conjunctions: {str(e)}")
                import traceback
            #     traceback.print_exc()
            #     response["ascendant_part_of_fortune_conjunctions"] = [{"error": f"Error calculating conjunctions: {str(e)}"}]
            #     response["interpretation"]["ascendant_pof_conjunction"] = (
            #         "We couldn't calculate when the ascendant will conjunct your natal Part of Fortune. "
            #         "This typically happens once per day for about 15-20 minutes and is an excellent time for starting new ventures."
            #     )
                
            # Get list of significant dates from the calculated data
            lucky_dates = []
            unlucky_dates = [] # Initialize unlucky_dates as well
            
            # Add all the bullseye periods
            if "bullseye_periods" in response and isinstance(response["bullseye_periods"], list):
                for period in response["bullseye_periods"]:
                    if isinstance(period, dict) and "time" in period:
                        lucky_dates.append(period["time"])
            
            # Add yogi configurations
            if "yogi_configurations" in response:
                # Add the next configuration
                if "next_configuration" in response["yogi_configurations"] and "formatted_time" in response["yogi_configurations"]["next_configuration"]:
                    lucky_dates.append(response["yogi_configurations"]["next_configuration"]["formatted_time"])
                
                # Add ascendant configurations
                if "ascendant_configurations" in response["yogi_configurations"] and isinstance(response["yogi_configurations"]["ascendant_configurations"], list):
                    for config in response["yogi_configurations"]["ascendant_configurations"]:
                        if "formatted_time" in config:
                            lucky_dates.append(config["formatted_time"])
                
                # Add lord configurations
                if "lord_configurations" in response["yogi_configurations"] and isinstance(response["yogi_configurations"]["lord_configurations"], list):
                    for config in response["yogi_configurations"]["lord_configurations"]:
                        if "formatted_time" in config:
                            lucky_dates.append(config["formatted_time"])
                
                # Add triple alignments
                if "triple_alignments" in response["yogi_configurations"] and isinstance(response["yogi_configurations"]["triple_alignments"], list):
                    for alignment in response["yogi_configurations"]["triple_alignments"]:
                        if "formatted_time" in alignment:
                            lucky_dates.append(alignment["formatted_time"])
                
                # Add yearly power alignments
                if "yearly_power_alignments" in response["yogi_configurations"] and isinstance(response["yogi_configurations"]["yearly_power_alignments"], list):
                    for alignment in response["yogi_configurations"]["yearly_power_alignments"]:
                        if "formatted_time" in alignment:
                            lucky_dates.append(alignment["formatted_time"])
            
            # Add next transits
            if "next_transits" in response:
                if "ascendant_ruler" in response["next_transits"] and "date" in response["next_transits"]["ascendant_ruler"]:
                    lucky_dates.append(response["next_transits"]["ascendant_ruler"]["date"])
                if "dasha_lord" in response["next_transits"] and "date" in response["next_transits"]["dasha_lord"]:
                    lucky_dates.append(response["next_transits"]["dasha_lord"]["date"])
            
            # Remove duplicates and sort
            lucky_dates = sorted(list(set(filter(None, lucky_dates))))
            
            # Calculate Part of Fortune - Rahu conjunctions for these dates
            pof_rahu_conjunctions = self.calculate_part_of_fortune_rahu_conjunctions(natal_data, transit_data, lucky_dates)
            
            # Add the results to the response
            response["part_of_fortune_rahu_conjunctions"] = pof_rahu_conjunctions
            
            # Add summary to interpretation
            pof_rahu_conjunct_dates = [conj["target_date"] for conj in pof_rahu_conjunctions if conj.get("is_pof_rahu_conjunct")]
            
            if pof_rahu_conjunct_dates:
                response["interpretation"]["part_of_fortune_rahu"] = (
                    f"The Part of Fortune conjuncts Rahu on the following lucky dates: {', '.join(pof_rahu_conjunct_dates)}. "
                    f"These dates represent especially powerful windows for manifestation, spiritual growth, and unexpected beneficial opportunities."
                )
            else:
                # Check for close conjunctions
                close_conjunctions = []
                for conj in pof_rahu_conjunctions:
                    if "closest_conjunction" in conj and conj["closest_conjunction"].get("is_within_orb"):
                        close_conjunctions.append(conj["closest_conjunction"]["date"])
                
                if close_conjunctions:
                    response["interpretation"]["part_of_fortune_rahu"] = (
                        f"While the Part of Fortune doesn't exactly conjunct Rahu on your lucky dates, "
                        f"there are close conjunctions on: {', '.join(close_conjunctions)}. "
                        f"These dates also offer enhanced manifestation potential."
                    )
                else:
                    response["interpretation"]["part_of_fortune_rahu"] = (
                        "The Part of Fortune does not conjunct Rahu on any of the calculated lucky dates. "
                        "Focus on the other auspicious factors identified in this analysis."
                    )
            
            # Calculate Part of Fortune - Regulus conjunctions for these dates
            pof_regulus_conjunctions = self.calculate_part_of_fortune_regulus_conjunctions(natal_data, transit_data, lucky_dates)
            
            # Add the results to the response
            response["part_of_fortune_regulus_conjunctions"] = pof_regulus_conjunctions
            
            # Add summary to interpretation
            pof_regulus_conjunct_dates = [conj["target_date"] for conj in pof_regulus_conjunctions if conj.get("is_pof_regulus_conjunct")]
            
            if pof_regulus_conjunct_dates:
                response["interpretation"]["part_of_fortune_regulus"] = (
                    f"The Part of Fortune conjuncts Regulus on the following lucky dates: {', '.join(pof_regulus_conjunct_dates)}. "
                    f"These dates represent powerful windows for recognition, success, and favorable outcomes from authority figures."
                )
            else:
                # Check for close conjunctions
                close_conjunctions = []
                for conj in pof_regulus_conjunctions:
                    if conj.get("angular_distance", float('inf')) <= 5:  # Within 5° orb for wider influence
                        close_conjunctions.append(conj["target_date"])
                
                if close_conjunctions:
                    response["interpretation"]["part_of_fortune_regulus"] = (
                        f"While the Part of Fortune doesn't exactly conjunct Regulus on your lucky dates, "
                        f"there are close alignments on: {', '.join(close_conjunctions)}. "
                        f"These dates still offer enhanced potential for recognition and success."
                    )
                else:
                    response["interpretation"]["part_of_fortune_regulus"] = (
                        "The Part of Fortune does not closely align with Regulus on any of the calculated lucky dates. "
                        "Focus on the other auspicious factors identified in this analysis."
                    )
            
            # Calculate Part of Fortune - Lord Lagna conjunctions for these dates
            pof_lord_lagna_conjunctions = self.calculate_part_of_fortune_lord_lagna_conjunctions(natal_data, transit_data, lucky_dates)
            
            # Add the results to the response
            response["part_of_fortune_lord_lagna_conjunctions"] = pof_lord_lagna_conjunctions
            
            # Add summary to interpretation
            pof_lord_lagna_conjunct_dates = [conj["target_date"] for conj in pof_lord_lagna_conjunctions if conj.get("is_pof_lord_lagna_conjunct")]
            
            if pof_lord_lagna_conjunct_dates:
                response["interpretation"]["part_of_fortune_lord_lagna"] = (
                    f"The Part of Fortune conjuncts the Lord of the Ascendant (Lagna) on the following lucky dates: {', '.join(pof_lord_lagna_conjunct_dates)}. "
                    f"These dates represent auspicious times for personal empowerment, success, and aligning one's actions with prosperity."
                )
            else:
                # Check for close conjunctions
                close_conjunctions = []
                for conj in pof_lord_lagna_conjunctions:
                    if conj.get("angular_distance", float('inf')) <= 5:  # Within 5° orb for wider influence
                        close_conjunctions.append(conj["target_date"])
                
                if close_conjunctions:
                    response["interpretation"]["part_of_fortune_lord_lagna"] = (
                        f"While the Part of Fortune doesn't exactly conjunct the Lord of the Ascendant (Lagna) on your lucky dates, "
                        f"there are close conjunctions on: {', '.join(close_conjunctions)}. "
                        f"These dates still offer enhanced potential for personal empowerment and success."
                    )
                else:
                    response["interpretation"]["part_of_fortune_lord_lagna"] = (
                        "The Part of Fortune does not closely align with the Lord of the Ascendant (Lagna) on any of the calculated lucky dates. "
                        "Focus on the other auspicious factors identified in this analysis."
                    )
            
            # Create a dedicated summary section for lucky and unlucky dates
            # This block is redundant as it was moved earlier to ~line 553
            # Deleting this block:
            # response["dates_summary"] = {
            #     "person_name": name,
            #     "asc_pof_conjunction_dates": [],
            #     "location_daily_dates": [],
            #     "location_power_dates": [],
            #     "yearly_power_dates": [],
            #     "bullseye_periods": [],
            #     "ascendant_ruler_dates": [],
            #     "dasha_lord_dates": [],
            #     "jupiter_pof_dates": [],
            #     "lucky_dates": [],
            #     "unlucky_dates": []
            # }
            
            # We'll handle Jupiter-POF dates later in the code to avoid duplication
            # (This was previously adding jupiter_pof_date here)
            
            # Add asc-pof conjunctions (if available)
            if "ascendant_part_of_fortune_conjunctions" in response:
                for idx, conj in enumerate(response["ascendant_part_of_fortune_conjunctions"]):
                    if idx < 3 and "conjunction_date" in conj:  # Only include nearest 3
                        response["dates_summary"]["asc_pof_conjunction_dates"].append({
                            "date": conj["conjunction_date"],
                            "name": f"asc_pof_conj_{idx}",  # Added name field with index
                            "description": f"Ascendant conjunct Part of Fortune at {conj['part_of_fortune']['sign']} {round(conj['part_of_fortune']['degree'], 1)}°",
                            "days_away": conj.get("days_away", 0),
                            "significance": f"Brief {conj.get('duration', {}).get('minutes', 20)}-minute window of enhanced fortune (daily occurrence)",
                            "duration": conj.get("duration", {
                                "minutes": 20,
                                "description": "Ascendant-Part of Fortune conjunctions typically last about 20 minutes"
                            })
                        })
            
            # Add lucky dates summary - ascendant ruler aspects to Yogi Point
            if "next_transits" in response and "ascendant_ruler" in response["next_transits"]:
                asc_ruler = response["next_transits"]["ascendant_ruler"]
                if asc_ruler["date"]:
                    response["dates_summary"]["ascendant_ruler_dates"].append({
                        "date": asc_ruler["date"],
                        "name": f"asc_ruler_yogi_{asc_ruler['aspect']}",  # Added name field
                        "description": f"{asc_ruler['planet'].capitalize()} ({asc_ruler['aspect']}) to Yogi Point",
                        "days_away": asc_ruler["days_away"],
                        "significance": "Favorable transit for spiritual development and fortunate events",
                        "duration": asc_ruler.get("duration")
                    })
            
            # Add lucky dates summary - dasha lord aspects to Yogi Point
            if "next_transits" in response and "dasha_lord" in response["next_transits"]:
                dasha_lord = response["next_transits"]["dasha_lord"]
                if dasha_lord["date"]:
                    response["dates_summary"]["dasha_lord_dates"].append({
                        "date": dasha_lord["date"],
                        "name": f"dasha_lord_yogi_{dasha_lord['aspect']}",  # Added name field
                        "description": f"{dasha_lord['planet'].capitalize()} ({dasha_lord['aspect']}) to Yogi Point",
                        "days_away": dasha_lord["days_away"],
                        "significance": "Favorable dasha lord transit enhancing luck and opportunity",
                        "duration": dasha_lord.get("duration")
                    })
            
            # Add Bullseye periods if available
            if "bullseye_periods" in response and isinstance(response["bullseye_periods"], list):
                # Check if it's the "no bullseye periods found" message
                if len(response["bullseye_periods"]) == 1 and "message" in response["bullseye_periods"][0] and "No Bullseye periods found" in response["bullseye_periods"][0]["message"]:
                    # Add the next estimated Bullseye period to dates_summary
                    if "next_estimated_bullseye" in response["bullseye_periods"][0]:
                        next_bullseye = response["bullseye_periods"][0]["next_estimated_bullseye"]
                        response["dates_summary"]["bullseye_periods"].append({
                            "date": next_bullseye["estimated_date"],
                            "name": "next_estimated_bullseye",
                            "description": "Estimated Next Bullseye Period",
                            "significance": next_bullseye["description"],
                            "days_away": next_bullseye["days_away"],
                            "is_estimated": True  # Flag to indicate this is an estimate
                        })
                        print(f"Added estimated next Bullseye period {next_bullseye['estimated_date']} to dates_summary")
                    else:
                        print("No bullseye periods found - not adding to dates_summary")
                else:
                    # Only include actual bullseye periods
                    for idx, period in enumerate(response["bullseye_periods"]):
                        if idx < 2 and "time" in period and "error" not in period and "message" not in period:  # Only include nearest 2 actual periods
                            # Calculate days away
                            days_away = 0
                            try:
                                period_date = datetime.strptime(period["time"], "%Y-%m-%d %H:%M")
                                now = datetime.now()
                                days_away = (period_date - now).total_seconds() / 86400  # Convert seconds to days
                            except Exception as e:
                                print(f"Error calculating days_away for bullseye period: {str(e)}")
                                
                            response["dates_summary"]["bullseye_periods"].append({
                                "date": period["time"],
                                "name": f"bullseye_period_{idx}",  # Added name field with index
                                "description": "Bullseye Period - Saturn aligns with D9 7th house cusp",
                                "significance": "Auspicious time for decisions and spiritual practices",
                                "duration": period.get("duration"),
                                "days_away": round(days_away) if days_away >= 0 else 0  # Add days_away
                            })
            
            # Add yogi configurations if available
            if "yogi_configurations" in response:
                if "yearly_power_alignments" in response["yogi_configurations"]:
                    for idx, alignment in enumerate(response["yogi_configurations"]["yearly_power_alignments"]):
                        if "formatted_time" in alignment:
                            response["dates_summary"]["yearly_power_dates"].append({
                                "date": alignment["formatted_time"],
                                "name": f"yearly_power_alignment_{idx}",  # Added name field with index
                                "description": alignment.get("type", "Yearly Power Alignment"),
                                "significance": "Rare and extremely powerful alignment (occurs ~once per year)",
                                "duration": alignment.get("duration")
                            })
            
            # Part of Fortune - Rahu conjunctions
            if "part_of_fortune_rahu_conjunctions" in response:
                for conj in response["part_of_fortune_rahu_conjunctions"]:
                    if conj.get("is_pof_rahu_conjunct", False):
                        response["dates_summary"]["yearly_power_dates"].append({
                            "date": conj["target_date"],
                            "name": "pof_rahu_conjunction",
                            "description": "Part of Fortune conjunct Rahu",
                            "significance": "Powerful for manifestation and unexpected opportunities",
                            "duration": conj.get("duration")
                        })
            
            # Add unlucky dates summary - ava yogi point transits
            if "ava_yogi_transits" in response:
                # Next ava yogi transits (upcoming challenging periods)
                if "next" in response["ava_yogi_transits"]:
                    if "ascendant_ruler" in response["ava_yogi_transits"]["next"]:
                        asc_ruler_ava = response["ava_yogi_transits"]["next"]["ascendant_ruler"]
                        if asc_ruler_ava["date"]:
                            response["dates_summary"]["unlucky_dates"].append({
                                "date": asc_ruler_ava["date"],
                                "description": f"{asc_ruler_ava['planet'].capitalize()} ({asc_ruler_ava['aspect']}) to Ava Yogi Point",
                                "days_away": asc_ruler_ava["days_away"],
                                "significance": "Challenging transit - potential obstacles or delays",
                                "duration": asc_ruler_ava.get("duration")
                            })
                    
                    if "dasha_lord" in response["ava_yogi_transits"]["next"]:
                        dasha_lord_ava = response["ava_yogi_transits"]["next"]["dasha_lord"]
                        if dasha_lord_ava["date"]:
                            response["dates_summary"]["unlucky_dates"].append({
                                "date": dasha_lord_ava["date"],
                                "description": f"{dasha_lord_ava['planet'].capitalize()} ({dasha_lord_ava['aspect']}) to Ava Yogi Point",
                                "days_away": dasha_lord_ava["days_away"],
                                "significance": "Challenging dasha lord transit - exercise caution",
                                "duration": dasha_lord_ava.get("duration")
                            })
            
                # Add recent ava yogi transits for context
                if "last" in response["ava_yogi_transits"]:
                    if "ascendant_ruler" in response["ava_yogi_transits"]["last"]:
                        asc_ruler_ava_last = response["ava_yogi_transits"]["last"]["ascendant_ruler"]
                        if asc_ruler_ava_last["date"]:
                            response["dates_summary"]["unlucky_dates"].append({
                                "date": asc_ruler_ava_last["date"],
                                "description": f"{asc_ruler_ava_last['planet'].capitalize()} ({asc_ruler_ava_last['aspect']}) to Ava Yogi Point",
                                "days_ago": asc_ruler_ava_last["days_ago"],
                                "significance": "Recent challenging period",
                                "duration": asc_ruler_ava_last.get("duration")
                            })
                    
                    if "dasha_lord" in response["ava_yogi_transits"]["last"]:
                        dasha_lord_ava_last = response["ava_yogi_transits"]["last"]["dasha_lord"]
                        if dasha_lord_ava_last["date"]:
                            response["dates_summary"]["unlucky_dates"].append({
                                "date": dasha_lord_ava_last["date"],
                                "description": f"{dasha_lord_ava_last['planet'].capitalize()} ({dasha_lord_ava_last['aspect']}) to Ava Yogi Point",
                                "days_ago": dasha_lord_ava_last["days_ago"],
                                "significance": "Recent challenging period",
                                "duration": dasha_lord_ava_last.get("duration")
                            })
                            
            # Add location-specific alignments if they are in the response
            if location_specific_alignments is not None:
                # Add the alignments to the response for backward compatibility
                response["location_specific_alignments"] = location_specific_alignments
                
                # Add power alignments (rare conjunction/opposition of Yogi and Duplicate Yogi in Asc/Desc)
                if "power_alignments" in location_specific_alignments and isinstance(location_specific_alignments["power_alignments"], list):
                    for idx, alignment in enumerate(location_specific_alignments["power_alignments"]):
                        if "date" in alignment and "type" in alignment:
                            response["dates_summary"]["location_power_dates"].append({
                                "date": alignment["date"],
                                "name": f"location_power_{idx}_{alignment['type'].lower().replace(' ', '_').replace('(', '').replace(')', '')}",
                                "description": alignment.get("description", alignment["type"]),
                                "days_away": alignment.get("days_away", 0),
                                "significance": alignment.get("significance", "Extremely rare and powerful alignment specific to your current location"),
                                "duration": alignment.get("duration")
                            })
                
                # Add daily alignments (more common) for reference
                if "daily_alignments" in location_specific_alignments and isinstance(location_specific_alignments["daily_alignments"], list):
                    for idx, alignment in enumerate(location_specific_alignments["daily_alignments"]):
                        if "time" in alignment and "type" in alignment:
                            response["dates_summary"]["location_daily_dates"].append({
                                "date": alignment["time"],
                                "name": f"location_daily_{alignment['type'].lower().replace(' ', '_')}",
                                "description": alignment.get("description", alignment["type"]),
                                "hours_away": alignment.get("hours_away", 0),
                                "significance": alignment.get("significance", "Daily Yogi Point alignment with local Ascendant"),
                                "duration": alignment.get("duration")
                            })
            # Fallback to the old way (for backward compatibility) 
            elif "location_specific_alignments" in response and isinstance(response["location_specific_alignments"], dict):
                loc_alignments = response["location_specific_alignments"]
                
                # Add power alignments (rare conjunction/opposition of Yogi and Duplicate Yogi in Asc/Desc)
                if "power_alignments" in loc_alignments and isinstance(loc_alignments["power_alignments"], list):
                    for idx, alignment in enumerate(loc_alignments["power_alignments"]):
                        if "date" in alignment and "type" in alignment:
                            response["dates_summary"]["location_power_dates"].append({
                                "date": alignment["date"],
                                "name": f"location_power_{idx}_{alignment['type'].lower().replace(' ', '_').replace('(', '').replace(')', '')}",
                                "description": alignment.get("description", alignment["type"]),
                                "days_away": alignment.get("days_away", 0),
                                "significance": alignment.get("significance", "Extremely rare and powerful alignment specific to your current location"),
                                "duration": alignment.get("duration")
                            })
                
                # Add daily alignments (more common) for reference
                if "daily_alignments" in loc_alignments and isinstance(loc_alignments["daily_alignments"], list):
                    for idx, alignment in enumerate(loc_alignments["daily_alignments"]):
                        if "time" in alignment and "type" in alignment:
                            response["dates_summary"]["location_daily_dates"].append({
                                "date": alignment["time"],
                                "name": f"location_daily_{alignment['type'].lower().replace(' ', '_')}",
                                "description": alignment.get("description", alignment["type"]),
                                "hours_away": alignment.get("hours_away", 0),
                                "significance": alignment.get("significance", "Daily Yogi Point alignment with local Ascendant"),
                                "duration": alignment.get("duration")
                            })
            
            # Check for stacked alignments with Part of Fortune special configurations
            # This enhances any dates that are close to these special alignments
            print("Checking for stacked alignments with Part of Fortune configurations...")
            try:
                # Get the Part of Fortune configuration data
                pof_rahu_data = response.get("part_of_fortune_rahu_conjunctions", [])
                pof_regulus_data = response.get("part_of_fortune_regulus_conjunctions", [])
                pof_lord_lagna_data = response.get("part_of_fortune_lord_lagna_conjunctions", [])
                
                # Apply the stacked alignment check to all date categories
                for date_category in ["asc_pof_conjunction_dates", "location_daily_dates", 
                                     "location_power_dates", "yearly_power_dates",
                                     "bullseye_periods", "ascendant_ruler_dates", 
                                     "dasha_lord_dates", "jupiter_pof_dates"]:
                    if date_category in response["dates_summary"] and response["dates_summary"][date_category]:
                        response["dates_summary"][date_category] = self.find_stacked_alignments(
                            response["dates_summary"][date_category],
                            pof_rahu_data,
                            pof_regulus_data,
                            pof_lord_lagna_data
                        )
                
                # Now apply to the combined lucky_dates list
                response["dates_summary"]["lucky_dates"] = self.find_stacked_alignments(
                    response["dates_summary"]["lucky_dates"],
                    pof_rahu_data,
                    pof_regulus_data,
                    pof_lord_lagna_data
                )
                
                print("Stacked alignment check completed.")
            except Exception as e:
                print(f"Error checking for stacked alignments: {str(e)}")
            
            # Check for internally stacked dates (dates that stack with each other)
            print("Checking for internally stacked dates...")
            try:
                # Apply the internal stacking check to all date categories
                for date_category in ["asc_pof_conjunction_dates", "location_daily_dates", 
                                    "location_power_dates", "yearly_power_dates",
                                    "bullseye_periods", "ascendant_ruler_dates", 
                                    "dasha_lord_dates", "jupiter_pof_dates"]:
                    if date_category in response["dates_summary"] and response["dates_summary"][date_category]:
                        response["dates_summary"][date_category] = self.find_internally_stacked_dates(
                            response["dates_summary"][date_category]
                        )
                
                # Now apply to the combined lucky_dates list
                response["dates_summary"]["lucky_dates"] = self.find_internally_stacked_dates(
                    response["dates_summary"]["lucky_dates"]
                )
                
                print("Internal stacking check completed.")
            except Exception as e:
                print(f"Error checking for internally stacked dates: {str(e)}")
            
            # Sort all date arrays by date
            for date_array_name in ["asc_pof_conjunction_dates", "location_daily_dates", 
                                    "location_power_dates", "yearly_power_dates",
                                    "bullseye_periods", "ascendant_ruler_dates", 
                                    "dasha_lord_dates", "jupiter_pof_dates", "lucky_dates", "unlucky_dates"]:
                if response["dates_summary"][date_array_name]:
                    try:
                        # Filter out entries with "N/A" or invalid dates before sorting
                        valid_dates = []
                        invalid_dates = []
                        
                        for date_entry in response["dates_summary"][date_array_name]:
                            try:
                                if date_entry["date"] and "N/A" not in date_entry["date"]:
                                    # Parse the date part (handling different formats with or without time)
                                    datetime.strptime(date_entry["date"].split(" ")[0], "%Y-%m-%d")
                                    valid_dates.append(date_entry)
                                else:
                                    invalid_dates.append(date_entry)
                            except (ValueError, TypeError, AttributeError):
                                # If date can't be parsed, add to invalid dates
                                invalid_dates.append(date_entry)
                        
                        # Sort valid dates
                        sorted_valid_dates = sorted(
                            valid_dates,
                            key=lambda x: datetime.strptime(x["date"].split(" ")[0], "%Y-%m-%d")
                        )
                        
                        # Combine sorted valid dates with invalid dates at the end
                        response["dates_summary"][date_array_name] = sorted_valid_dates + invalid_dates
                        
                    except Exception as e:
                        print(f"Error sorting {date_array_name}: {str(e)}")
            
            # Create overview summary from nearest dates
            summary_text = []
            
            # Get nearest future date from each category
            nearest_dates = []
            
            # Function to get the nearest future date from a category
            def get_nearest_future_date(dates_array):
                future_dates = [d for d in dates_array if "date" in d and "days_away" in d and "N/A" not in d["date"]]
                if future_dates:
                    future_dates.sort(key=lambda x: x["days_away"])
                    return future_dates[0]
                return None
            
            # Check each category for nearest future date
            for category in ["asc_pof_conjunction_dates", "location_daily_dates", 
                         "location_power_dates", "yearly_power_dates",
                         "bullseye_periods", "ascendant_ruler_dates", 
                         "dasha_lord_dates", "jupiter_pof_dates"]:
                nearest = get_nearest_future_date(response["dates_summary"][category])
                if nearest:
                    nearest_dates.append(nearest)
            
            # Sort by days_away to find the nearest overall
            if nearest_dates:
                nearest_dates.sort(key=lambda x: x["days_away"])
                nearest_lucky = nearest_dates[0]
                summary_text.append(f"Next lucky date: {nearest_lucky['date']} - {nearest_lucky['description']}")
            
            # Get nearest unlucky date
            nearest_unlucky = next((d for d in response["dates_summary"]["unlucky_dates"] if "days_away" in d), None)
            if nearest_unlucky:
                summary_text.append(f"Next challenging date: {nearest_unlucky['date']} - {nearest_unlucky['description']}")
            
            # Add summary to the easy-to-view section
            response["dates_summary"]["overview"] = " | ".join(summary_text)
            
            # Add Jupiter-POF dates to the summary
            if "jupiter_pof_conjunctions" in response and "next_conjunction" in response["jupiter_pof_conjunctions"]:
                next_conj_data = response["jupiter_pof_conjunctions"]["next_conjunction"]
                jupiter_pof_entry = {
                    "date": next_conj_data["date"],
                    "name": "jupiter_pof_conjunction",
                    "description": f"Jupiter conjunct Natal Part of Fortune in {response['jupiter_pof_conjunctions']['part_of_fortune']['sign']} {response['jupiter_pof_conjunctions']['part_of_fortune']['degree']}°",
                    "days_away": next_conj_data["days_away"],
                    "significance": "Jupiter conjunct your natal Part of Fortune brings a period of expanded fortune and opportunity that occurs approximately once every 12 years.",
                    "duration": next_conj_data["duration"]
                }
                
                # Add only to jupiter_pof_dates array
                response["dates_summary"]["jupiter_pof_dates"].append(jupiter_pof_entry)
                
                # Also add the last conjunction if available
                if "last_conjunction" in response["jupiter_pof_conjunctions"]:
                    last_conj_data = response["jupiter_pof_conjunctions"]["last_conjunction"]
                    last_jupiter_pof_entry = {
                        "date": last_conj_data["date"],
                        "name": "jupiter_pof_last_conjunction",
                        "description": f"Jupiter last conjunct Natal Part of Fortune in {response['jupiter_pof_conjunctions']['part_of_fortune']['sign']} {response['jupiter_pof_conjunctions']['part_of_fortune']['degree']}°",
                        "days_ago": last_conj_data["days_ago"],
                        "significance": "Jupiter's last conjunction with your Part of Fortune was a period of expanded fortune and opportunity.",
                        "duration": last_conj_data.get("duration", {
                            "days": 24,
                            "start_date": "Unknown",
                            "exact_date": last_conj_data["date"],
                            "end_date": "Unknown",
                            "description": f"This aspect was active for approximately 24 days around {last_conj_data['date']}"
                        })
                    }
                    response["dates_summary"]["jupiter_pof_dates"].append(last_jupiter_pof_entry)
                
                # Only add to lucky_dates if not already added through another method
                # Check if we already have this date in lucky_dates
                date_exists = any(
                    d.get("date") == jupiter_pof_entry["date"] and 
                    d.get("name") == jupiter_pof_entry["name"]
                    for d in response["dates_summary"]["lucky_dates"]
                )
                
                if not date_exists:
                    response["dates_summary"]["lucky_dates"].append(jupiter_pof_entry)
            
            # Final sanity check to remove any duplicates in jupiter_pof_dates
            if "jupiter_pof_dates" in response["dates_summary"]:
                # Create a set to track seen entries
                seen_entries = set()
                unique_entries = []
                
                for entry in response["dates_summary"]["jupiter_pof_dates"]:
                    # Create a tuple of key identifying fields
                    entry_key = (entry.get("date"), entry.get("name"))
                    
                    # Only add if we haven't seen this entry before
                    if entry_key not in seen_entries:
                        seen_entries.add(entry_key)
                        unique_entries.append(entry)
                
                # Replace with deduplicated list
                response["dates_summary"]["jupiter_pof_dates"] = unique_entries
                
                # Extract the next and last jupiter-pof conjunction dates
                next_date = None
                last_date = None
                
                for entry in response["dates_summary"]["jupiter_pof_dates"]:
                    if "jupiter_pof_conjunction" == entry.get("name"):
                        next_date = entry.get("date")
                    elif "jupiter_pof_last_conjunction" == entry.get("name"):
                        last_date = entry.get("date")
                
                # Remove previous approach using separate keys
                if "jupiter_pof_next_date" in response["dates_summary"]:
                    del response["dates_summary"]["jupiter_pof_next_date"]
                if "jupiter_pof_last_date" in response["dates_summary"]:
                    del response["dates_summary"]["jupiter_pof_last_date"]
                
                # Add next_date and last_date exactly as specified in example
                if next_date:
                    response["dates_summary"]["jupiter_pof_dates"].append({"next_date": next_date})
                
                if last_date:
                    response["dates_summary"]["jupiter_pof_dates"].append({"last_date": last_date})
            
            return response
            
        except Exception as e:
            print(f"Error in process_vedic_lucky_times: {str(e)}")
            # Return a complete response with error information and default values
            return {
                "error": f"Error processing Vedic lucky times: {str(e)}",
                "yogi_point": {
                    "absolute_position": yogi_point if 'yogi_point' in locals() else 0,
                    "sign": list(ZODIAC_SIGNS.keys())[int(yogi_point / 30)] if 'yogi_point' in locals() else "unknown",
                    "degree": round(yogi_point % 30, 2) if 'yogi_point' in locals() else 0
                },
                "ava_yogi_point": {
                    "absolute_position": 0,
                    "sign": "unknown",
                    "degree": 0
                },
                "ascendant_info": {
                    "sign": "unknown",
                    "ruler": "sun",  # Default to sun as a fallback
                    "current_position": {
                        "absolute": 0,
                        "sign": "unknown",
                        "degree": 0,
                        "is_retrograde": False
                    }
                },
                "next_transits": {
                    "ascendant_ruler": {
                        "planet": "sun",
                        "date": None,
                        "aspect": "none",
                        "days_away": 0,
                        "is_retrograde": False,
                        "duration": None
                    },
                    "dasha_lord": {
                        "planet": "sun",
                        "date": None,
                        "aspect": "none",
                        "days_away": 0,
                        "is_retrograde": False,
                        "duration": None
                    }
                },
                "last_transits": {
                    "ascendant_ruler": {
                        "planet": "sun",
                        "date": None,
                        "aspect": "none",
                        "days_ago": 0,
                        "is_retrograde": False,
                        "duration": None
                    },
                    "dasha_lord": {
                        "planet": "sun",
                        "date": None,
                        "aspect": "none",
                        "days_ago": 0,
                        "is_retrograde": False,
                        "duration": None
                    }
                },
                "ava_yogi_transits": {
                    "next": {
                        "ascendant_ruler": {
                            "planet": "sun",
                            "date": None,
                            "aspect": "none",
                            "days_away": 0,
                            "is_retrograde": False
                        },
                        "dasha_lord": {
                            "planet": "sun",
                            "date": None,
                            "aspect": "none",
                            "days_away": 0,
                            "is_retrograde": False
                        }
                    },
                    "last": {
                        "ascendant_ruler": {
                            "planet": "sun",
                            "date": None,
                            "aspect": "none",
                            "days_ago": 0,
                            "is_retrograde": False
                        },
                        "dasha_lord": {
                            "planet": "sun",
                            "date": None,
                            "aspect": "none",
                            "days_ago": 0,
                            "is_retrograde": False
                        }
                    }
                },
                "interpretation": {
                    "yogi_point": "Error calculating Yogi Point interpretation",
                    "ava_yogi_point": "Error calculating Ava Yogi Point interpretation",
                    "ascendant_ruler": "Error calculating Ascendant Ruler interpretation",
                    "dasha_lord": "Error calculating Dasha Lord interpretation",
                    "next_transit": "Error calculating next transit interpretation",
                    "last_transit": "Error calculating last transit interpretation",
                    "next_ava_yogi_transit": "Error calculating next Ava Yogi transit interpretation",
                    "last_ava_yogi_transit": "Error calculating last Ava Yogi transit interpretation",
                    "best_use": "Please try again later"
                }
            }

    def calculate_yogi_configurations(self, natal_data: Dict[str, Any], transit_data: Dict[str, Any], orb: float = 3.0) -> Dict[str, Any]:
        """Calculate when Yogi and Duplicate Yogi points are in significant configurations with the ascendant"""
      
        return calculate_yogi_configurations(self, natal_data, transit_data, orb)

    def calculate_d9_position(self, zodiac_position: float) -> float:
        """
        Calculate the D9 (Navamsa) position for a given zodiac position.
        
        Each sign is divided into 9 equal parts (3°20' or ~3.33° each).
        The mapping follows:
        - For fire signs (Aries, Leo, Sagittarius): Aries → Leo
        - For earth signs (Taurus, Virgo, Capricorn): Cancer → Pisces
        - For air signs (Gemini, Libra, Aquarius): Libra → Gemini
        - For water signs (Cancer, Scorpio, Pisces): Cancer → Pisces
        
        Args:
            zodiac_position: Absolute position in the zodiac (0-360°)
            
        Returns:
            The D9 position (0-360°)
        """
        return calculate_d9_position(self, zodiac_position)
        
    def calculate_d9_chart(self, natal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the D9 (Navamsa) chart from natal data.
        
        Args:
            natal_data: The natal chart data
            
        Returns:
            Dictionary containing the D9 positions for all planets and points
        """
        return calculate_d9_chart(self, natal_data)
    
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
        return calculate_bullseye_periods(self, natal_data, transit_data)
            
    def find_stacked_alignments(self, all_dates_list: List[Dict[str, Any]], 
                             pof_rahu_data: List[Dict[str, Any]] = None,
                             pof_regulus_data: List[Dict[str, Any]] = None,
                             pof_lord_lagna_data: List[Dict[str, Any]] = None,
                             time_window_hours: int = 12) -> List[Dict[str, Any]]:
        """
        Check if any dates in the dates list align with Part of Fortune special configurations.
        When dates are close to these special configurations, they are considered "stacked"
        and marked as more powerful.
        
        Args:
            all_dates_list: List of date dictionaries from dates_summary
            pof_rahu_data: List of Part of Fortune - Rahu conjunction data
            pof_regulus_data: List of Part of Fortune - Regulus conjunction data
            pof_lord_lagna_data: List of Part of Fortune - Lord Lagna conjunction data
            time_window_hours: Hours window to consider for alignment (default: 12 hours)
            
        Returns:
            The same dates list with added stacked_with information where applicable
        """
        return find_stacked_alignments(self, all_dates_list, pof_rahu_data, pof_regulus_data, pof_lord_lagna_data, time_window_hours)
            
    
            
    def find_internally_stacked_dates(self, all_dates_list: List[Dict[str, Any]], 
                                   exclude_same_type: bool = True) -> List[Dict[str, Any]]:
        """
        Find dates within the dates_summary that stack with each other (occur close in time).
        This identifies when multiple auspicious dates/alignments occur close to each other,
        creating a compound effect of beneficial energies.
        
        Alignments are considered stacked only if their actual time windows overlap.
        
        Args:
            all_dates_list: List of date dictionaries from dates_summary
            exclude_same_type: Whether to exclude stacking between dates of the same type
            
        Returns:
            The same dates list with added internal_stacks information where applicable
        """
        return find_internally_stacked_dates(self, all_dates_list, exclude_same_type)
    
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
        return calculate_ascendant_part_of_fortune_conjunctions(self, natal_data, transit_data, num_days, orb)
    
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
        return calculate_part_of_fortune_rahu_conjunctions(self, natal_data, transit_data, lucky_dates)

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
        return calculate_part_of_fortune_regulus_conjunctions(self, natal_data, transit_data, lucky_dates)

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
        return calculate_part_of_fortune_lord_lagna_conjunctions(self, natal_data, transit_data, lucky_dates)
    
    def calculate_location_specific_yogi_alignments(self, natal_data: Dict[str, Any], current_city: str, current_nation: str, orb: float = 3.0, transit_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate when the Yogi (star ruler of the Yogi Point) and duplicate yogi (sign ruler of the Yogi Point)
        are both conjunct or opposite AND in the ascendant or descendant for a specified location.
        This is a rare and powerful alignment specific to the current location.
        
        Args:
            natal_data: The natal chart data containing the Yogi Point
            current_city: The current city where the person is located
            current_nation: The current nation where the person is located
            orb: The orb value to use for aspects (default: 3.0)
            transit_data: The transit chart data (optional, for more accurate planet positions)
            
        Returns:
            Dictionary containing location-specific Yogi and duplicate Yogi alignment details
        """
        return calculate_location_specific_yogi_alignments(self, natal_data, current_city, current_nation, orb, transit_data)
    
    
    def calculate_alignment_duration(self, exact_time: datetime, slower_planet: str = None, alignment_type: str = "conjunction", orb: float = 3.0) -> Dict[str, Any]:
        """
        Calculate the duration of an alignment involving the Ascendant and optionally a slower-moving planet.
        
        Args:
            exact_time: The exact time of the alignment
            slower_planet: The name of a slower-moving planet involved (if any)
            alignment_type: The type of alignment (conjunction, opposition, etc.)
            orb: The orb value to use (default: 3.0)
            
        Returns:
            Dictionary containing duration information
        """
        # Ascendant moves at 15 degrees per hour (1 degree per 4 minutes)
        ascendant_minutes_per_degree = 4
        
        # Base duration calculation - how long the ascendant takes to move through 2*orb degrees
        base_duration_minutes = int(2 * orb * ascendant_minutes_per_degree)
        
        # Adjust for planet involvement if applicable
        adjustment_factor = 1.0
        if slower_planet:
            # Add a small factor for the slower moving planet for more realistic timing
            if slower_planet == "jupiter":
                # Jupiter's slow movement means the window is slightly extended
                adjustment_factor = 1.3
            elif slower_planet == "saturn":
                # Saturn's very slow movement extends the window more
                adjustment_factor = 1.4
            elif slower_planet == "venus":
                # Venus adds a modest extension to the window
                adjustment_factor = 1.1
            elif slower_planet == "mars":
                # Mars adds a slight extension
                adjustment_factor = 1.05
            elif slower_planet in ["sun", "mercury"]:
                # Sun and Mercury add minimal extension
                adjustment_factor = 1.02
        
        # For special alignment types, add a slight increase to duration
        if "power" in alignment_type.lower() or "yearly" in alignment_type.lower():
            # These are special, rare alignments - give them slightly longer duration
            adjustment_factor *= 1.2
        
        # Calculate final duration
        duration_minutes = int(base_duration_minutes * adjustment_factor)
        
        # Calculate start and end times
        half_duration = duration_minutes // 2
        start_time = exact_time - timedelta(minutes=half_duration)
        end_time = exact_time + timedelta(minutes=half_duration)
        
        # Format duration for human readability
        duration_text = f"{duration_minutes} minutes"
        if duration_minutes >= 60:
            hours = duration_minutes // 60
            remaining_minutes = duration_minutes % 60
            if remaining_minutes == 0:
                duration_text = f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                duration_text = f"{hours} hour{'s' if hours > 1 else ''} and {remaining_minutes} minutes"
        
        return {
            "minutes": duration_minutes,
            "orb_used": orb,
            "start_time": start_time.strftime("%Y-%m-%d %H:%M"),
            "exact_time": exact_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M"),
            "description": f"This alignment lasts approximately {duration_text}, from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')} (using {orb}° orb)"
        }