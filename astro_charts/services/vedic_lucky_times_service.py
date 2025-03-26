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

    def find_closest_aspect(self, current_pos: float, daily_motion: float, yogi_point: float, is_retrograde: bool = False, orb: float = 3.0) -> Dict[str, Any]:
        return find_closest_aspect(current_pos, daily_motion, yogi_point, is_retrograde, orb)

    def calculate_yogi_point(self, natal_data: Dict[str, Any]) -> float:
        return calculate_yogi_point(natal_data)
    
    def calculate_yogi_point_transit(self, transit_data: Dict[str, Any]) -> float:
        return calculate_yogi_point_transit(transit_data)

    def sanitize_response_for_json(self, response: Dict[str, Any]) -> Dict[str, Any]:
        return sanitize_response_for_json(response)

    def find_last_aspect(self, current_pos: float, daily_motion: float, yogi_point: float, is_retrograde: bool = False, orb: float = 3.0) -> Dict[str, Any]:
        return find_last_aspect(current_pos, daily_motion, yogi_point, is_retrograde, orb)

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
                orb=orb  # Use provided orb
            )
            
            # Calculate last aspect of ruler to Yogi Point
            ruler_last_aspect = self.find_last_aspect(
                current_pos=current_ruler_pos,
                daily_motion=ruler_daily_motion,
                yogi_point=yogi_point,
                is_retrograde=ruler_retrograde,
                orb=orb  # Use provided orb
            )
            
            # Calculate next aspect of ruler to Ava Yogi Point (unlucky point)
            ruler_next_ava_aspect = self.find_closest_aspect(
                current_pos=current_ruler_pos,
                daily_motion=ruler_daily_motion,
                yogi_point=ava_yogi_point,
                is_retrograde=ruler_retrograde,
                orb=orb  # Use provided orb
            )
            
            # Calculate last aspect of ruler to Ava Yogi Point
            ruler_last_ava_aspect = self.find_last_aspect(
                current_pos=current_ruler_pos,
                daily_motion=ruler_daily_motion,
                yogi_point=ava_yogi_point,
                is_retrograde=ruler_retrograde,
                orb=orb  # Use provided orb
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
                orb=orb  # Use provided orb
            )
            
            # Calculate last aspect of Dasha lord to Yogi Point
            dasha_last_aspect = self.find_last_aspect(
                current_pos=current_dasha_pos,
                daily_motion=dasha_daily_motion,
                yogi_point=yogi_point,
                is_retrograde=dasha_retrograde,
                orb=orb  # Use provided orb
            )
            
            # Calculate next aspect of Dasha lord to Ava Yogi Point
            dasha_next_ava_aspect = self.find_closest_aspect(
                current_pos=current_dasha_pos,
                daily_motion=dasha_daily_motion,
                yogi_point=ava_yogi_point,
                is_retrograde=dasha_retrograde,
                orb=orb  # Use provided orb
            )
            
            # Calculate last aspect of Dasha lord to Ava Yogi Point
            dasha_last_ava_aspect = self.find_last_aspect(
                current_pos=current_dasha_pos,
                daily_motion=dasha_daily_motion,
                yogi_point=ava_yogi_point,
                is_retrograde=dasha_retrograde,
                orb=orb  # Use provided orb
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
                    orb=orb  # Use provided orb
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
                    orb=orb  # Use provided orb
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
                    orb=orb  # Use provided orb
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
                    orb=orb  # Use provided orb
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
            response["interpretation"] = {
                "yogi_point": f"Your Yogi Point at {round(yogi_point % 30, 2)}° {ZODIAC_SIGNS[response['yogi_point']['sign']]} indicates times of heightened spiritual awareness and fortune when activated by transits",
                "ava_yogi_point": f"Your Ava Yogi Point at {round(ava_yogi_point % 30, 2)}° {ZODIAC_SIGNS[response['ava_yogi_point']['sign']]} indicates times of challenge or difficulty when activated by transits",
                "ascendant_ruler": f"Your Ascendant ruler {ascendant_ruler.capitalize()} is currently at {round(current_ruler_degree, 2)}° {ZODIAC_SIGNS[current_ruler_sign]} {'(Retrograde) ' if ruler_retrograde else ''}and will make a {ruler_next_aspect['type']} to your Yogi Point in {ruler_next_aspect['estimated_days']} days, lasting approximately {ruler_next_aspect['duration']['days']} days (from {ruler_next_aspect['duration']['start_date']} to {ruler_next_aspect['duration']['end_date']})",
                "dasha_lord": f"Your Dasha Lord {dasha_lord.capitalize()} is currently at {round(current_dasha_degree, 2)}° {ZODIAC_SIGNS[current_dasha_sign]} {'(Retrograde) ' if dasha_retrograde else ''}and will make a {dasha_next_aspect['type']} to your Yogi Point in {dasha_next_aspect['estimated_days']} days, lasting approximately {dasha_next_aspect['duration']['days']} days (from {dasha_next_aspect['duration']['start_date']} to {dasha_next_aspect['duration']['end_date']})",
                "next_transit": f"The next significant transit will be from your {dasha_lord if dasha_next_aspect['estimated_days'] <= ruler_next_aspect['estimated_days'] else ascendant_ruler} on {dasha_next_aspect['estimated_date'] if dasha_next_aspect['estimated_days'] <= ruler_next_aspect['estimated_days'] else ruler_next_aspect['estimated_date']}",
                "last_transit": f"Your {ascendant_ruler.capitalize()} made a {ruler_last_aspect['type']} to your Yogi Point {ruler_last_aspect['estimated_days_ago']} days ago on {ruler_last_aspect['estimated_date']}, and your {dasha_lord.capitalize()} made a {dasha_last_aspect['type']} {dasha_last_aspect['estimated_days_ago']} days ago on {dasha_last_aspect['estimated_date']}.",
                "next_ava_yogi_transit": f"Be cautious around {ruler_next_ava_aspect['estimated_date']} when your {ascendant_ruler.capitalize()} makes a {ruler_next_ava_aspect['type']} to your Ava Yogi Point (active from {ruler_next_ava_aspect['duration']['start_date']} to {ruler_next_ava_aspect['duration']['end_date']}), and around {dasha_next_ava_aspect['estimated_date']} when your {dasha_lord.capitalize()} makes a {dasha_next_ava_aspect['type']} to your Ava Yogi Point (active from {dasha_next_ava_aspect['duration']['start_date']} to {dasha_next_ava_aspect['duration']['end_date']}).",
                "last_ava_yogi_transit": f"You may have experienced challenges {ruler_last_ava_aspect['estimated_days_ago']} days ago ({ruler_last_ava_aspect['estimated_date']}) when your {ascendant_ruler.capitalize()} made a {ruler_last_ava_aspect['type']} to your Ava Yogi Point, and {dasha_last_ava_aspect['estimated_days_ago']} days ago ({dasha_last_ava_aspect['estimated_date']}) when your {dasha_lord.capitalize()} made a {dasha_last_ava_aspect['type']}.",
                "best_use": "Use these periods for important beginnings, spiritual practices, or significant life decisions",
                "duration_explanation": "Transits are most powerful on the exact date but have influence throughout their duration period. The orb used for calculations affects how long the transit remains active."
            }
            
            if has_yogi_config and "next_configuration" in yogi_configurations:
                next_config = yogi_configurations["next_configuration"]
                if "type" in next_config and "formatted_time" in next_config:
                    response["interpretation"]["next_yogi_configuration"] = f"The next significant alignment is {next_config['type']} at {next_config['formatted_time']}, which is an auspicious time for spiritual practices."
            
            if has_yogi_config and "duplicate_yogi" in yogi_configurations:
                dup_yogi = yogi_configurations["duplicate_yogi"]
                if all(key in dup_yogi for key in ["planet", "degree", "sign"]):
                    response["interpretation"]["yogi_duplicate_yogi"] = f"The Duplicate Yogi is {dup_yogi['planet'].capitalize()}, the ruler of your Yogi Point sign ({response['yogi_point']['sign']}). It is currently at {round(dup_yogi['degree'], 2)}° {ZODIAC_SIGNS[dup_yogi['sign']]}."
            
            response["interpretation"]["significance"] = "These alignments create powerful spiritual windows for meditation, ceremony, or important beginnings."
            
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
            
            # Add Bullseye interpretation
            if bullseye_periods and "error" not in bullseye_periods[0]:
                # Check if we have a regular bullseye period with time
                if "time" in bullseye_periods[0]:
                    next_bullseye = bullseye_periods[0]
                    bullseye_interpretation = (
                        f"The next Bullseye period occurs at {next_bullseye['time']} when Saturn in your D9 chart "
                        f"aligns with your 7th house cusp. This is an auspicious time for making important decisions, "
                        f"beginning significant projects, or engaging in spiritual practices."
                    )
                    
                    # Check if it's currently a Bullseye period
                    current_bullseye = next(filter(lambda x: x.get("is_current", False), bullseye_periods), None)
                    if current_bullseye:
                        bullseye_interpretation = (
                            f"You are currently in a Bullseye period with Saturn at {round(current_bullseye['d9_saturn']['degree'], 2)}° "
                            f"{ZODIAC_SIGNS[current_bullseye['d9_saturn']['sign']]} in your D9 chart, "
                            f"within {current_bullseye['angular_distance']}° of your 7th house cusp. "
                            f"This is an auspicious time for important decisions and spiritual practices."
                        )
                # Check if we have a message about no bullseye periods
                elif "message" in bullseye_periods[0]:
                    message = bullseye_periods[0]["message"]
                    if "No Bullseye periods found" in message:
                        # Get specific details to make the interpretation more informative
                        current_distance = bullseye_periods[0].get("current_angular_distance", 0)
                        saturn_d9 = bullseye_periods[0].get("current_saturn_d9", {})
                        d9_seventh_cusp = bullseye_periods[0].get("d9_seventh_cusp", {})
                        
                        # Create more detailed interpretation
                        bullseye_interpretation = (
                            f"No Bullseye periods were found in the next two days. The Saturn position in your D9 chart "
                            f"is currently {round(current_distance, 2)}° away from your 7th house cusp. "
                            f"Saturn is at {round(saturn_d9.get('degree', 0), 2)}° {ZODIAC_SIGNS[saturn_d9.get('sign', 'Ari')]} "
                            f"and your 7th house cusp is at {round(d9_seventh_cusp.get('degree', 0), 2)}° {ZODIAC_SIGNS[d9_seventh_cusp.get('sign', 'Ari')]}. "
                            f"Bullseye periods occur when Saturn in the D9 chart aligns within 2.5° of your 7th house cusp, creating an "
                            f"auspicious time for important decisions and spiritual practices."
                        )
                    else:
                        bullseye_interpretation = f"Bullseye period information: {message}"
                else:
                    bullseye_interpretation = "Bullseye period information is not available with the current chart data."
            else:
                # Handle error case
                error_msg = bullseye_periods[0].get("error", "Unknown error") if bullseye_periods else "No bullseye data available"
                bullseye_interpretation = f"Bullseye period information could not be calculated: {error_msg}"
            
            response["interpretation"]["bullseye_period"] = bullseye_interpretation
            
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
                traceback.print_exc()
                response["ascendant_part_of_fortune_conjunctions"] = [{"error": f"Error calculating conjunctions: {str(e)}"}]
                response["interpretation"]["ascendant_pof_conjunction"] = (
                    "We couldn't calculate when the ascendant will conjunct your natal Part of Fortune. "
                    "This typically happens once per day for about 15-20 minutes and is an excellent time for starting new ventures."
                )
                
            # Get list of significant dates from the calculated data
            lucky_dates = []
            
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
            response["dates_summary"] = {
                "person_name": name,
                "asc_pof_conjunction_dates": [],
                "location_daily_dates": [],
                "location_power_dates": [],
                "yearly_power_dates": [],
                "bullseye_periods": [],  # This ensures bullseye_periods is always initialized
                "ascendant_ruler_dates": [],
                "dasha_lord_dates": [],
                "jupiter_pof_dates": [],
                "lucky_dates": [],
                "unlucky_dates": []
            }
            
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
        # Get the sign number (0-11) and position within the sign (0-30°)
        sign_num = int(zodiac_position / 30)
        pos_in_sign = zodiac_position % 30
        
        # Determine the element of the sign
        element = sign_num % 4  # 0=Fire, 1=Earth, 2=Air, 3=Water
        
        # Each navamsa is 3°20' (or 10/3 degrees)
        navamsa_size = 10/3
        navamsa_num = int(pos_in_sign / navamsa_size)
        
        # Determine the starting sign for the navamsa mapping based on the element
        if element == 0:  # Fire signs
            start_sign = 0  # Aries
        elif element == 1:  # Earth signs
            start_sign = 3  # Cancer
        elif element == 2:  # Air signs
            start_sign = 6  # Libra
        else:  # Water signs
            start_sign = 3  # Cancer
        
        # Calculate the Navamsa sign
        navamsa_sign = (start_sign + navamsa_num) % 12
        
        # Calculate the position within the navamsa sign
        # We're not adjusting the position within the sign as we're only interested in the sign placement
        # for basic D9 analysis
        navamsa_position = navamsa_sign * 30 + 15  # Middle of the sign
        
        return navamsa_position
        
    def calculate_d9_chart(self, natal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the D9 (Navamsa) chart from natal data.
        
        Args:
            natal_data: The natal chart data
            
        Returns:
            Dictionary containing the D9 positions for all planets and points
        """
        d9_chart = {
            "planets": {},
            "houses": {},
            "lagna": {}
        }
        
        # Calculate D9 positions for all planets
        for planet_name, planet_data in natal_data["subject"]["planets"].items():
            absolute_pos = planet_data["abs_pos"]
            d9_position = self.calculate_d9_position(absolute_pos)
            d9_sign_num = int(d9_position / 30)
            d9_sign = list(ZODIAC_SIGNS.keys())[d9_sign_num]
            
            d9_chart["planets"][planet_name] = {
                "d9_position": d9_position,
                "d9_sign": d9_sign,
                "d9_degree": d9_position % 30,
                "natal_position": absolute_pos,
                "natal_sign": planet_data["sign"],
                "is_retrograde": planet_data.get("retrograde", False)
            }
        
        # Calculate D9 position for the Ascendant (Lagna)
        if "houses" in natal_data["subject"] and "ascendant" in natal_data["subject"]["houses"]:
            ascendant_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
            d9_asc_position = self.calculate_d9_position(ascendant_pos)
            d9_asc_sign_num = int(d9_asc_position / 30)
            d9_asc_sign = list(ZODIAC_SIGNS.keys())[d9_asc_sign_num]
            
            d9_chart["lagna"] = {
                "d9_position": d9_asc_position,
                "d9_sign": d9_asc_sign,
                "d9_degree": d9_asc_position % 30,
                "natal_position": ascendant_pos,
                "natal_sign": natal_data["subject"]["houses"]["ascendant"]["sign"]
            }
            
            # Calculate D9 positions for house cusps if available
            has_house_cusps = False
            for house_num in range(1, 13):
                house_key = f"house_{house_num}"
                if house_key in natal_data["subject"]["houses"]:
                    has_house_cusps = True
                    house_pos = natal_data["subject"]["houses"][house_key]["abs_pos"]
                    d9_house_position = self.calculate_d9_position(house_pos)
                    d9_house_sign_num = int(d9_house_position / 30)
                    d9_house_sign = list(ZODIAC_SIGNS.keys())[d9_house_sign_num]
                    
                    d9_chart["houses"][house_key] = {
                        "d9_position": d9_house_position,
                        "d9_sign": d9_house_sign,
                        "d9_degree": d9_house_position % 30,
                        "natal_position": house_pos,
                        "natal_sign": natal_data["subject"]["houses"][house_key]["sign"]
                    }
            
            # If house cusps aren't available, calculate them based on the lagna (ascendant)
            # This ensures houses are available for bullseye calculations
            if not has_house_cusps and d9_chart["lagna"]:
                d9_asc_position = d9_chart["lagna"]["d9_position"]
                
                # Calculate all 12 houses, evenly spaced 30° apart
                for house_num in range(1, 13):
                    house_key = f"house_{house_num}"
                    # House 1 is the ascendant, other houses are 30° apart
                    house_pos = (d9_asc_position + (house_num - 1) * 30) % 360
                    d9_house_sign_num = int(house_pos / 30)
                    d9_house_sign = list(ZODIAC_SIGNS.keys())[d9_house_sign_num]
                    
                    # Add the house to d9_chart
                    d9_chart["houses"][house_key] = {
                        "d9_position": house_pos,
                        "d9_sign": d9_house_sign,
                        "d9_degree": house_pos % 30,
                        "natal_position": (natal_data["subject"]["houses"]["ascendant"]["abs_pos"] + (house_num - 1) * 30) % 360,
                        "natal_sign": list(ZODIAC_SIGNS.keys())[int(((natal_data["subject"]["houses"]["ascendant"]["abs_pos"] + (house_num - 1) * 30) % 360) / 30)]
                    }
        
        # Calculate D9 position for Yogi Point
        yogi_point = self.calculate_yogi_point(natal_data)
        d9_yogi_position = self.calculate_d9_position(yogi_point)
        d9_yogi_sign_num = int(d9_yogi_position / 30)
        d9_yogi_sign = list(ZODIAC_SIGNS.keys())[d9_yogi_sign_num]
        
        d9_chart["yogi_point"] = {
            "d9_position": d9_yogi_position,
            "d9_sign": d9_yogi_sign,
            "d9_degree": d9_yogi_position % 30,
            "natal_position": yogi_point,
            "natal_sign": list(ZODIAC_SIGNS.keys())[int(yogi_point / 30)]
        }
        
        # Calculate D9 position for Ava Yogi Point
        ava_yogi_point = self.calculate_ava_yogi_point(yogi_point)
        d9_ava_yogi_position = self.calculate_d9_position(ava_yogi_point)
        d9_ava_yogi_sign_num = int(d9_ava_yogi_position / 30)
        d9_ava_yogi_sign = list(ZODIAC_SIGNS.keys())[d9_ava_yogi_sign_num]
        
        d9_chart["ava_yogi_point"] = {
            "d9_position": d9_ava_yogi_position,
            "d9_sign": d9_ava_yogi_sign,
            "d9_degree": d9_ava_yogi_position % 30,
            "natal_position": ava_yogi_point,
            "natal_sign": list(ZODIAC_SIGNS.keys())[int(ava_yogi_point / 30)]
        }
        
        # Ensure the 7th house is always present (critical for bullseye calculations)
        if "lagna" in d9_chart and d9_chart["lagna"] and "house_7" not in d9_chart["houses"]:
            d9_asc_position = d9_chart["lagna"]["d9_position"]
            d9_seventh_position = (d9_asc_position + 180) % 360
            d9_seventh_sign_num = int(d9_seventh_position / 30)
            d9_seventh_sign = list(ZODIAC_SIGNS.keys())[d9_seventh_sign_num]
            
            d9_chart["houses"]["house_7"] = {
                "d9_position": d9_seventh_position,
                "d9_sign": d9_seventh_sign,
                "d9_degree": d9_seventh_position % 30,
                "natal_position": (natal_data["subject"]["houses"]["ascendant"]["abs_pos"] + 180) % 360,
                "natal_sign": list(ZODIAC_SIGNS.keys())[int(((natal_data["subject"]["houses"]["ascendant"]["abs_pos"] + 180) % 360) / 30)]
            }
        
        return d9_chart
    
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
                    d9_seventh_cusp_at_time = self.calculate_d9_position(seventh_cusp_at_time)
                    
                    # Saturn's position doesn't change much in a day, but we can calculate it for precision
                    saturn_pos_at_time = (saturn_pos + (hours_since_now * saturn_daily_motion / 24)) % 360
                    d9_saturn_pos_at_time = self.calculate_d9_position(saturn_pos_at_time)
                    
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
                            precise_d9_seventh_cusp = self.calculate_d9_position(precise_seventh_cusp)
                            
                            precise_saturn_pos = (saturn_pos + (precise_hours_since_now * saturn_daily_motion / 24)) % 360
                            precise_d9_saturn_pos = self.calculate_d9_position(precise_saturn_pos)
                            
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
                    projected_saturn_d9_pos = self.calculate_d9_position(projected_saturn_pos)
                    
                    # For each projection day, check different hours since 7th house cusp
                    # cycles through zodiac every day
                    for hour in [0, 6, 12, 18]:  # Check 4 times per day for efficiency
                        check_time = check_date.replace(hour=hour, minute=0, second=0)
                        
                        # Calculate projected Ascendant at this time
                        hours_since_now = (check_time - now).total_seconds() / 3600
                        projected_asc_pos = (current_asc_pos + (hours_since_now * 15)) % 360
                        
                        # Calculate projected 7th house cusp and its D9 position
                        projected_7th_cusp = (projected_asc_pos + 180) % 360
                        projected_d9_7th_cusp = self.calculate_d9_position(projected_7th_cusp)
                        
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
                                fine_d9_7th_cusp = self.calculate_d9_position(fine_7th_cusp)
                                
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
        try:
            # If no special configuration data provided, return original list
            if not pof_rahu_data and not pof_regulus_data and not pof_lord_lagna_data:
                return all_dates_list
                
            # Convert time window to seconds for comparison
            time_window_seconds = time_window_hours * 3600
            
            # Process each date in the list
            for date_entry in all_dates_list:
                if "date" not in date_entry or not date_entry["date"]:
                    continue
                    
                try:
                    # Parse the date string to a datetime object
                    date_datetime = datetime.strptime(date_entry["date"], "%Y-%m-%d %H:%M")
                    stacked_with = []
                    
                    # Check for Part of Fortune - Rahu conjunctions
                    if pof_rahu_data:
                        for pof_rahu in pof_rahu_data:
                            if "target_date" not in pof_rahu or "error" in pof_rahu:
                                continue
                                
                            try:
                                pof_rahu_datetime = datetime.strptime(pof_rahu["target_date"], "%Y-%m-%d %H:%M")
                                
                                # Check if within time window and is conjunct
                                time_diff = abs((date_datetime - pof_rahu_datetime).total_seconds())
                                if time_diff <= time_window_seconds and pof_rahu.get("is_pof_rahu_conjunct", False):
                                    stack_info = {
                                        "type": "part_of_fortune_rahu",
                                        "date": pof_rahu["target_date"],
                                        "description": "Part of Fortune conjunct Rahu (North Node)",
                                        "significance": "Intensifies manifestation power and karmic significance"
                                    }
                                    stacked_with.append(stack_info)
                            except Exception as e:
                                print(f"Error processing POF-Rahu date {pof_rahu.get('target_date')}: {str(e)}")
                    
                    # Check for Part of Fortune - Regulus conjunctions
                    if pof_regulus_data:
                        for pof_regulus in pof_regulus_data:
                            if "target_date" not in pof_regulus or "error" in pof_regulus:
                                continue
                                
                            try:
                                pof_regulus_datetime = datetime.strptime(pof_regulus["target_date"], "%Y-%m-%d %H:%M")
                                
                                # Check if within time window and is conjunct
                                time_diff = abs((date_datetime - pof_regulus_datetime).total_seconds())
                                if time_diff <= time_window_seconds and pof_regulus.get("is_pof_regulus_conjunct", False):
                                    stack_info = {
                                        "type": "part_of_fortune_regulus",
                                        "date": pof_regulus["target_date"],
                                        "description": "Part of Fortune conjunct Regulus (Royal Star)",
                                        "significance": "Adds fame, recognition and royal favor to manifestations"
                                    }
                                    stacked_with.append(stack_info)
                            except Exception as e:
                                print(f"Error processing POF-Regulus date {pof_regulus.get('target_date')}: {str(e)}")
                    
                    # Check for Part of Fortune - Lord Lagna conjunctions
                    if pof_lord_lagna_data:
                        for pof_lord in pof_lord_lagna_data:
                            if "target_date" not in pof_lord or "error" in pof_lord:
                                continue
                                
                            try:
                                pof_lord_datetime = datetime.strptime(pof_lord["target_date"], "%Y-%m-%d %H:%M")
                                
                                # Check if within time window and is conjunct
                                time_diff = abs((date_datetime - pof_lord_datetime).total_seconds())
                                if time_diff <= time_window_seconds and pof_lord.get("is_pof_lord_lagna_conjunct", False):
                                    lord_planet = pof_lord.get("lord_lagna", {}).get("planet", "").capitalize()
                                    stack_info = {
                                        "type": "part_of_fortune_lord_lagna",
                                        "date": pof_lord["target_date"],
                                        "description": f"Part of Fortune conjunct {lord_planet} (Lord of your Ascendant)",
                                        "significance": "Aligns personal empowerment with financial/material prosperity"
                                    }
                                    stacked_with.append(stack_info)
                            except Exception as e:
                                print(f"Error processing POF-Lord Lagna date {pof_lord.get('target_date')}: {str(e)}")
                    
                    # If we found any stacked configurations, add them to the date entry
                    if stacked_with:
                        date_entry["stacked_with"] = stacked_with
                        # Also mark the date as more powerful
                        date_entry["stacked_power"] = len(stacked_with)
                        if "significance" in date_entry:
                            date_entry["significance"] = "STACKED POWER: " + date_entry["significance"]
                        
                except Exception as e:
                    print(f"Error processing date entry {date_entry.get('date')}: {str(e)}")
            
            return all_dates_list
            
        except Exception as e:
            print(f"Error in find_stacked_alignments: {str(e)}")
            return all_dates_list  # Return original list in case of error
            
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
        try:
            # If less than 2 dates, no stacking possible
            if len(all_dates_list) < 2:
                return all_dates_list
            
            # First filter out entries with invalid dates or "N/A"
            valid_dates = []
            for date_entry in all_dates_list:
                if "date" not in date_entry or not date_entry["date"] or "N/A" in date_entry["date"]:
                    continue
                    
                try:
                    # Check if it can be parsed as a datetime
                    datetime.strptime(date_entry["date"], "%Y-%m-%d %H:%M")
                    valid_dates.append(date_entry)
                except (ValueError, TypeError):
                    continue
            
            # Process each date in the list to find stacks
            for i, date_entry in enumerate(valid_dates):
                try:
                    # Get date entry type from its name field
                    entry_type = date_entry.get("name", "").split("_")[0] if "_" in date_entry.get("name", "") else ""
                    
                    # Get time window for this entry
                    entry_start_time = None
                    entry_end_time = None
                    
                    # Try to get precise start/end times from duration if available
                    if "duration" in date_entry and date_entry["duration"] and isinstance(date_entry["duration"], dict):
                        if "start_time" in date_entry["duration"] and "end_time" in date_entry["duration"]:
                            try:
                                entry_start_time = datetime.strptime(date_entry["duration"]["start_time"], "%Y-%m-%d %H:%M")
                                entry_end_time = datetime.strptime(date_entry["duration"]["end_time"], "%Y-%m-%d %H:%M")
                            except (ValueError, TypeError):
                                pass
                    
                    # Fallback to exact time if start/end times not available directly
                    if not entry_start_time or not entry_end_time:
                        # For alignments with days duration
                        if "duration" in date_entry and date_entry["duration"] and isinstance(date_entry["duration"], dict) and "days" in date_entry["duration"]:
                            if date_entry["duration"]["days"] > 0 and "start_date" in date_entry["duration"] and "end_date" in date_entry["duration"]:
                                if date_entry["duration"]["start_date"] != "N/A" and date_entry["duration"]["end_date"] != "N/A":
                                    try:
                                        # Try to parse with time if available, otherwise use date only
                                        try:
                                            entry_start_time = datetime.strptime(date_entry["duration"]["start_date"], "%Y-%m-%d %H:%M")
                                        except ValueError:
                                            entry_start_time = datetime.strptime(date_entry["duration"]["start_date"], "%Y-%m-%d")
                                            
                                        try:
                                            entry_end_time = datetime.strptime(date_entry["duration"]["end_date"], "%Y-%m-%d %H:%M")
                                        except ValueError:
                                            # Add 23:59 to make it end of day
                                            end_date_str = date_entry["duration"]["end_date"] + " 23:59"
                                            entry_end_time = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")
                                    except (ValueError, TypeError):
                                        pass
                    
                    # If still no duration info, use exact time and default to a small window (±5 minutes)
                    if not entry_start_time or not entry_end_time:
                        try:
                            exact_time = datetime.strptime(date_entry["date"], "%Y-%m-%d %H:%M")
                            entry_start_time = exact_time - timedelta(minutes=5)
                            entry_end_time = exact_time + timedelta(minutes=5)
                        except (ValueError, TypeError):
                            # If we can't determine a time window, skip this entry
                            continue
                    
                    internal_stacks = []
                    
                    # Check other dates for stacking
                    for j, other_entry in enumerate(valid_dates):
                        if i == j:  # Skip self
                            continue
                            
                        # Get other entry type
                        other_type = other_entry.get("name", "").split("_")[0] if "_" in other_entry.get("name", "") else ""
                        
                        # If excluding same type and types match, skip
                        if exclude_same_type and entry_type and other_type and entry_type == other_type:
                            continue
                            
                        try:
                            # Get time window for other entry
                            other_start_time = None
                            other_end_time = None
                            
                            # Try to get precise start/end times from duration if available
                            if "duration" in other_entry and other_entry["duration"] and isinstance(other_entry["duration"], dict):
                                if "start_time" in other_entry["duration"] and "end_time" in other_entry["duration"]:
                                    try:
                                        other_start_time = datetime.strptime(other_entry["duration"]["start_time"], "%Y-%m-%d %H:%M")
                                        other_end_time = datetime.strptime(other_entry["duration"]["end_time"], "%Y-%m-%d %H:%M")
                                    except (ValueError, TypeError):
                                        pass
                            
                            # Fallback to exact time if start/end times not available directly
                            if not other_start_time or not other_end_time:
                                # For alignments with days duration
                                if "duration" in other_entry and other_entry["duration"] and isinstance(other_entry["duration"], dict) and "days" in other_entry["duration"]:
                                    if other_entry["duration"]["days"] > 0 and "start_date" in other_entry["duration"] and "end_date" in other_entry["duration"]:
                                        if other_entry["duration"]["start_date"] != "N/A" and other_entry["duration"]["end_date"] != "N/A":
                                            try:
                                                # Try to parse with time if available, otherwise use date only
                                                try:
                                                    other_start_time = datetime.strptime(other_entry["duration"]["start_date"], "%Y-%m-%d %H:%M")
                                                except ValueError:
                                                    other_start_time = datetime.strptime(other_entry["duration"]["start_date"], "%Y-%m-%d")
                                                    
                                                try:
                                                    other_end_time = datetime.strptime(other_entry["duration"]["end_date"], "%Y-%m-%d %H:%M")
                                                except ValueError:
                                                    # Add 23:59 to make it end of day
                                                    other_end_date_str = other_entry["duration"]["end_date"] + " 23:59"
                                                    other_end_time = datetime.strptime(other_end_date_str, "%Y-%m-%d %H:%M")
                                            except (ValueError, TypeError):
                                                pass
                            
                            # If still no duration info, use exact time and default to a small window (±5 minutes)
                            if not other_start_time or not other_end_time:
                                try:
                                    other_exact_time = datetime.strptime(other_entry["date"], "%Y-%m-%d %H:%M")
                                    other_start_time = other_exact_time - timedelta(minutes=5)
                                    other_end_time = other_exact_time + timedelta(minutes=5)
                                except (ValueError, TypeError):
                                    # If we can't determine a time window, skip this entry
                                    continue
                            
                            # Check if the time windows overlap
                            if entry_start_time <= other_end_time and entry_end_time >= other_start_time:
                                # Calculate overlap amount in minutes
                                overlap_start = max(entry_start_time, other_start_time)
                                overlap_end = min(entry_end_time, other_end_time)
                                overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60
                                
                                # Only consider it a stack if there's a meaningful overlap (at least 1 minute)
                                if overlap_minutes >= 1:
                                    # Found a stacked date with overlapping time window
                                    stack_info = {
                                        "type": "internal_stack",
                                        "name": other_entry.get("name", "unknown"),
                                        "date": other_entry["date"],
                                        "description": other_entry.get("description", "Stacked alignment"),
                                        "overlap_minutes": round(overlap_minutes, 1),
                                        "overlap_window": {
                                            "start_time": overlap_start.strftime("%Y-%m-%d %H:%M"),
                                            "end_time": overlap_end.strftime("%Y-%m-%d %H:%M"),
                                            "description": f"Alignments overlap for {round(overlap_minutes)} minutes from {overlap_start.strftime('%H:%M')} to {overlap_end.strftime('%H:%M')}"
                                        }
                                    }
                                    
                                    # Add duration if available
                                    if "duration" in other_entry and other_entry["duration"]:
                                        stack_info["duration"] = other_entry["duration"]
                                        
                                    internal_stacks.append(stack_info)
                        except Exception as e:
                            print(f"Error comparing with date {other_entry.get('date')}: {str(e)}")
                    
                    # If we found any internal stacks, add them to the date entry
                    if internal_stacks:
                        if "stacked_with" not in date_entry:
                            date_entry["stacked_with"] = []
                            
                        # Add internal stacks to any existing stacked_with array
                        date_entry["stacked_with"].extend(internal_stacks)
                        
                        # Update or set stacked_power
                        if "stacked_power" in date_entry:
                            date_entry["stacked_power"] += len(internal_stacks)
                        else:
                            date_entry["stacked_power"] = len(internal_stacks)
                            
                        # Update significance to indicate stacking
                        if "significance" in date_entry:
                            if "STACKED POWER:" not in date_entry["significance"]:
                                date_entry["significance"] = "STACKED POWER: " + date_entry["significance"]
                        else:
                            date_entry["significance"] = "STACKED POWER: Multiple alignments overlap with this period"
                        
                except Exception as e:
                    print(f"Error processing internal stacking for {date_entry.get('date')}: {str(e)}")
            
            return all_dates_list
            
        except Exception as e:
            print(f"Error in find_internally_stacked_dates: {str(e)}")
            return all_dates_list  # Return original list in case of error

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
        conjunctions = []
        
        try:
            # Calculate the natal Part of Fortune position
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
                
            # Get current ascendant position
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
                current_asc_pos = (midheaven_pos - 90) % 360
                estimation_method = "from_midheaven"
                print(f"APPROXIMATION: Estimated ascendant from midheaven: {round(current_asc_pos, 2)}°")
            
            # Check if MC is stored as house_10 instead
            elif ("transit" in transit_data and 
                 "subject" in transit_data["transit"] and 
                 "houses" in transit_data["transit"]["subject"] and 
                 "house_10" in transit_data["transit"]["subject"]["houses"]):
                
                mc_pos = transit_data["transit"]["subject"]["houses"]["house_10"]["abs_pos"]
                current_asc_pos = (mc_pos - 90) % 360
                estimation_method = "from_house_10"
                print(f"APPROXIMATION: Estimated ascendant from house_10: {round(current_asc_pos, 2)}°")
            
            # =====================================================================
            # PRIORITY 3: Calculate from transit Sun position and time
            # =====================================================================
            elif ("transit" in transit_data and 
                 "subject" in transit_data["transit"] and 
                 "planets" in transit_data["transit"]["subject"] and 
                 "sun" in transit_data["transit"]["subject"]["planets"]):
                
                estimation_method = "sun_position"
                transit_sun_pos = transit_data["transit"]["subject"]["planets"]["sun"]["abs_pos"]
                print(f"APPROXIMATION: Using sun position at {round(transit_sun_pos, 2)}° for ascendant calculation")
                
                # Get current time
                current_time = datetime.now()
                hour_of_day = current_time.hour + current_time.minute/60
                
                # Try to get transit time if available
                transit_time_available = False
                if ("transit" in transit_data and 
                    "subject" in transit_data["transit"] and 
                    "birth_data" in transit_data["transit"]["subject"] and 
                    "time" in transit_data["transit"]["subject"]["birth_data"]):
                    try:
                        transit_time = transit_data["transit"]["subject"]["birth_data"]["time"]
                        if ":" in transit_time:
                            transit_hour, transit_minute = map(int, transit_time.split(':'))
                            hour_of_day = transit_hour + transit_minute/60
                            transit_time_available = True
                            print(f"Using transit chart time: {transit_hour}:{transit_minute} ({hour_of_day:.2f} hours)")
                    except Exception as e:
                        print(f"Error parsing transit time: {e}, using current time instead")
                
                # Get transit location if available (for longitude adjustment)
                longitude = None
                if ("transit" in transit_data and 
                    "subject" in transit_data["transit"] and 
                    "birth_data" in transit_data["transit"]["subject"] and 
                    "longitude" in transit_data["transit"]["subject"]["birth_data"]):
                    try:
                        longitude = float(transit_data["transit"]["subject"]["birth_data"]["longitude"])
                        print(f"Using transit chart longitude: {longitude}")
                    except Exception as e:
                        print(f"Error parsing longitude: {e}, proceeding without longitude adjustment")
                
                # Calculate ascendant based on sun position and time
                if longitude is not None:
                    # Adjust hour for longitude (15° = 1 hour)
                    longitude_hour_adjustment = longitude / 15
                    adjusted_hour = (hour_of_day - longitude_hour_adjustment) % 24
                    print(f"Adjusted hour for longitude: {adjusted_hour:.2f}")
                    
                    # Calculate ascendant based on sun position and adjusted time
                    # This uses the fact that at noon (solar noon), sun is near the MC (midheaven)
                    # At that time, ascendant is roughly sun_position - 90°
                    # We adjust from there based on hours from noon
                    noon = 12
                    hours_from_noon = (adjusted_hour - noon) % 24
                    
                    # At noon: ASC ≈ SUN - 90°
                    # Each hour offset from noon changes ASC by ~15°
                    if hours_from_noon <= 12:  # From noon to midnight
                        ascendant_offset = -90 + (hours_from_noon * 15)
                    else:  # From midnight to noon
                        ascendant_offset = 90 - ((hours_from_noon - 12) * 15)
                    
                    current_asc_pos = (transit_sun_pos + ascendant_offset) % 360
                else:
                    # Simplified calculation if no longitude data
                    hours_since_midnight = hour_of_day % 24
                    
                    # Calculate approximate ascendant position based on time of day
                    # Mapping the 24-hour day onto a 360° circle with some adjustments
                    # for the typical relationship between sun and ascendant
                    if hours_since_midnight < 6:  # Midnight to sunrise
                        progress = hours_since_midnight / 6
                        ascendant_offset = 90 - (progress * 90)
                    elif hours_since_midnight < 12:  # Sunrise to noon
                        progress = (hours_since_midnight - 6) / 6
                        ascendant_offset = -(progress * 90)
                    elif hours_since_midnight < 18:  # Noon to sunset
                        progress = (hours_since_midnight - 12) / 6
                        ascendant_offset = -90 - (progress * 90)
                    else:  # Sunset to midnight
                        progress = (hours_since_midnight - 18) / 6
                        ascendant_offset = -180 + (progress * 270)
                    
                    current_asc_pos = (transit_sun_pos + ascendant_offset) % 360
                
                print(f"Calculated transit ascendant based on sun position: {round(current_asc_pos, 2)}°")
            
            # =====================================================================
            # PRIORITY 4: Use time-based estimation from natal chart as fallback
            # =====================================================================
            else:
                estimation_method = "time_based"
                current_time = datetime.now()
                hour_of_day = current_time.hour + current_time.minute/60
                print("FALLBACK: No transit sun position found, using time-based estimation from natal chart")
                
                # Try to get birth time
                try:
                    if "date_utc" in natal_data["subject"]:
                        birth_time_str = natal_data["subject"]["date_utc"].split('T')[1]
                        birth_hour = int(birth_time_str.split(':')[0])
                        birth_minute = int(birth_time_str.split(':')[1])
                        birth_time_decimal = birth_hour + birth_minute/60
                        
                        # Calculate hours difference
                        hours_diff = (hour_of_day - birth_time_decimal) % 24
                        
                        # Ascendant moves ~15° per hour
                        ascendant_adjustment = hours_diff * 15
                        
                        # Calculate current estimated ascendant
                        current_asc_pos = (natal_asc_pos + ascendant_adjustment) % 360
                        print(f"Estimated transit ascendant using natal chart + time adjustment: {round(current_asc_pos, 2)}°")
                    else:
                        raise ValueError("No date_utc field in natal data")
                        
                except Exception as e:
                    # Ultimate fallback: simple time-based calculation
                    print(f"Error with time-based estimation: {str(e)}. Using simplest time-based method.")
                    estimation_method = "simple_time"
                    
                    # Start from 0° Aries at midnight, advancing 15° per hour
                    ascendant_base = 0
                    ascendant_adjustment = hour_of_day * 15
                    current_asc_pos = (ascendant_base + ascendant_adjustment) % 360
                    print(f"Estimated transit ascendant using simplest time-based method: {round(current_asc_pos, 2)}°")
            
            # If we still don't have an ascendant position after all fallbacks, throw an error
            if current_asc_pos is None:
                raise ValueError("Could not determine ascendant position using any available method")
            
            # Current time
            now = datetime.now()
            
            # Calculate how many degrees until the ascendant reaches the Part of Fortune
            degrees_to_pof = (natal_pof - current_asc_pos) % 360
            
            # Convert to hours (ascendant moves at 15° per hour)
            hours_to_pof = degrees_to_pof / 15
            
            # First conjunction time
            first_conjunction = now + timedelta(hours=hours_to_pof)
            
            # Calculate duration - Ascendant moves at 15° per hour, using the provided orb
            # orb° / 15° per hour = orb/15 hours = (orb/15)*60 minutes on each side
            minutes_per_degree = 4  # 15° per hour = 1° per 4 minutes
            conjunction_duration_minutes = int(orb * minutes_per_degree * 2)  # Double the orb duration for total (before and after)
            conjunction_half_duration = conjunction_duration_minutes / 2  # Half for calculating start and end times
            
            # Generate conjunctions for the specified number of days
            for day in range(num_days):
                try:
                    # Calculate conjunction time for this day
                    # Each day, the ascendant will reach the same degree 4 minutes earlier (sidereal day is ~23h56m)
                    conjunction_time = first_conjunction + timedelta(days=day, minutes=-4*day)
                    
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
                        "hours_away": round((conjunction_time - now).total_seconds() / 3600, 1) if day == 0 else None,
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
                        "simple_time": "This is a very general approximation (±30-60 minutes)."
                    }
                    
                    method_desc = {
                        "transit_ascendant": "using the exact transit ascendant position",
                        "from_midheaven": "calculated from the midheaven position",
                        "from_house_10": "calculated from the 10th house cusp",
                        "sun_position": "based on the sun's position and time of day",
                        "time_based": "based on your birth chart and current time",
                        "simple_time": "based on time of day only"
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
        try:
            # Calculate Yogi Point from natal data
            yogi_point = self.calculate_yogi_point_transit(transit_data)
            print(f"Yogi Point Transit for Location Specific Alignments: {yogi_point}")
            # Determine the sign of the Yogi Point
            yogi_sign_num = int(yogi_point / 30)
            yogi_sign = list(ZODIAC_SIGNS.keys())[yogi_sign_num]
            
            # Determine the sign ruler of the Yogi Point (Duplicate Yogi)
            duplicate_yogi_planet = self.get_ascendant_ruler(yogi_sign, zodiac_type="Sidereal")
            
            # Determine the star ruler of the Yogi Point (Yogi)
            # The star ruler is based on the nakshatra division (27 segments) of the zodiac
            nakshatra_index = int((yogi_point * 27) / 360)
            
            # Nakshatra lords in order (Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury)
            nakshatra_lords = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"] * 3
            yogi_planet = nakshatra_lords[nakshatra_index]
            
            # Current date/time
            now = datetime.now()
            
            # Create a result dictionary with calculated data
            result = {
                "yogi_point": {
                    "absolute_position": yogi_point,
                    "sign": yogi_sign,
                    "degree": round(yogi_point % 30, 2),
                    "full_sign_name": ZODIAC_SIGNS[yogi_sign]
                },
                "duplicate_yogi": {
                    "planet": duplicate_yogi_planet,
                    "description": f"Sign ruler of {ZODIAC_SIGNS[yogi_sign]} (the sign containing your Yogi Point)"
                },
                "yogi": {
                    "planet": yogi_planet,
                    "description": f"Star ruler (nakshatra lord) of your Yogi Point at {round(yogi_point % 30, 2)}° {ZODIAC_SIGNS[yogi_sign]}"
                },
                "current_location": {
                    "city": current_city,
                    "nation": current_nation
                },
                "calculation_date": now.strftime("%Y-%m-%d %H:%M")
            }
            
            # Define planets and their approximate daily motion
            planets = {
                "sun": {"motion": 1.0, "name": "Sun"},
                "moon": {"motion": 13.2, "name": "Moon"},
                "mercury": {"motion": 1.0, "name": "Mercury"},
                "venus": {"motion": 1.0, "name": "Venus"},
                "mars": {"motion": 0.5, "name": "Mars"},
                "jupiter": {"motion": 0.083, "name": "Jupiter"},
                "saturn": {"motion": 0.034, "name": "Saturn"},
                "rahu": {"motion": 0.053, "name": "Rahu", "is_retrograde": True},
                "ketu": {"motion": 0.053, "name": "Ketu", "is_retrograde": True}
            }
            
            # Get actual planet positions from transit data if available
            planet_positions = {}
            planet_retrograde = {}
            
            if transit_data and "transit" in transit_data and "subject" in transit_data["transit"] and "planets" in transit_data["transit"]["subject"]:
                transit_planets = transit_data["transit"]["subject"]["planets"]
                
                # Extract actual positions from transit data
                for planet_name in planets.keys():
                    if planet_name in transit_planets:
                        planet_positions[planet_name] = transit_planets[planet_name]["abs_pos"]
                        planet_retrograde[planet_name] = transit_planets[planet_name].get("retrograde", False)
            
            # If transit data is not available or incomplete, fall back to estimation
            if not planet_positions:
                # Calculate approximate planet positions based on the sun's position
                sun_longitude = (now.timetuple().tm_yday - 80) % 365  # Approximate Sun position from day of year
                sun_position = (sun_longitude / 365) * 360
                
                # For a more realistic approximation, offset each planet based on its mean distance from the Sun
                planet_positions = {
                    "sun": sun_position,
                    "moon": (sun_position + 180 + (now.day * 12)) % 360,  # Moon moves quickly and could be anywhere
                    "mercury": (sun_position + 20) % 360,  # Mercury is never far from the Sun
                    "venus": (sun_position + 45) % 360,   # Venus can be up to ~47° from the Sun
                    "mars": (sun_position + 120) % 360,   # Other planets are more varied
                    "jupiter": (sun_position + 190) % 360,
                    "saturn": (sun_position + 240) % 360,
                    "rahu": (sun_position + 160) % 360,
                    "ketu": (sun_position + 340) % 360
                }
                
                # Default retrograde status from known patterns
                for planet in planets.keys():
                    planet_retrograde[planet] = planets.get(planet, {}).get("is_retrograde", False)
            
            # Calculate positions for Yogi and Duplicate Yogi
            yogi_position = planet_positions.get(yogi_planet)
            duplicate_yogi_position = planet_positions.get(duplicate_yogi_planet)
            
            # If positions couldn't be determined, use fallback
            if yogi_position is None:
                print(f"Warning: Position for {yogi_planet} not found in transit data, using fallback")
                yogi_position = (hash(yogi_planet) % 360)
            
            if duplicate_yogi_position is None:
                print(f"Warning: Position for {duplicate_yogi_planet} not found in transit data, using fallback")
                duplicate_yogi_position = (hash(duplicate_yogi_planet) % 360)
            
            # Store the positions in the result
            result["yogi"]["current_position"] = {
                "absolute": round(yogi_position, 2),
                "sign": list(ZODIAC_SIGNS.keys())[int(yogi_position / 30)],
                "degree": round(yogi_position % 30, 2),
                "is_retrograde": planet_retrograde.get(yogi_planet, False)
            }
            
            result["duplicate_yogi"]["current_position"] = {
                "absolute": round(duplicate_yogi_position, 2),
                "sign": list(ZODIAC_SIGNS.keys())[int(duplicate_yogi_position / 30)],
                "degree": round(duplicate_yogi_position % 30, 2),
                "is_retrograde": planet_retrograde.get(duplicate_yogi_planet, False)
            }
            
            # Now we need to find when BOTH the Yogi and Duplicate Yogi will be:
            # 1. Conjunct or opposite each other, AND
            # 2. In the Ascendant or Descendant at the current location
            
            # Get the actual ascendant position from the transit data if available
            transit_ascendant_pos = None
            if transit_data and "transit" in transit_data and "subject" in transit_data["transit"] and "houses" in transit_data["transit"]["subject"] and "ascendant" in transit_data["transit"]["subject"]["houses"]:
                transit_ascendant_pos = transit_data["transit"]["subject"]["houses"]["ascendant"]["abs_pos"]
                print(f"Using actual transit ascendant position for {current_city}, {current_nation}: {transit_ascendant_pos}°")
            else:
                # Fallback to estimation if not available
                # Ascendant moves at approximately 1° every 4 minutes (15° per hour)
                current_hour = now.hour + now.minute / 60
                transit_ascendant_pos = (current_hour * 15) % 360
                print(f"Warning: Using estimated ascendant position {transit_ascendant_pos}° because actual ascendant not found in transit data")
            
            # These are extremely rare configurations, similar to yearly power alignments
            power_alignments = []
            
            # Calculate when Yogi and Duplicate Yogi will be conjunct or opposite
            # First calculate their relative motion (degrees per day)
            if yogi_planet in planets and duplicate_yogi_planet in planets:
                yogi_daily_motion = planets[yogi_planet]["motion"]
                duplicate_yogi_daily_motion = planets[duplicate_yogi_planet]["motion"]
                
                # Adjust for retrograde motion
                yogi_direction = -1 if planet_retrograde.get(yogi_planet, False) else 1
                duplicate_yogi_direction = -1 if planet_retrograde.get(duplicate_yogi_planet, False) else 1
                
                # Calculate relative motion between the two planets
                relative_motion = abs(yogi_daily_motion * yogi_direction - duplicate_yogi_daily_motion * duplicate_yogi_direction)
                
                # Ensure we have some relative motion to avoid division by zero
                if relative_motion < 0.01:
                    relative_motion = 0.01
                
                # Calculate angular separation between Yogi and Duplicate Yogi
                angular_sep = abs(yogi_position - duplicate_yogi_position) % 360
                if angular_sep > 180:
                    angular_sep = 360 - angular_sep
                
                # Check if already in conjunction within orb
                if angular_sep <= orb:
                    # They're already in conjunction within the specified orb
                    days_to_conjunction = 0
                else:
                    # Calculate days until conjunction
                    days_to_conjunction = (angular_sep - orb) / relative_motion
                
                # Check if already in opposition within orb
                opposition_sep = abs(180 - angular_sep)
                if opposition_sep <= orb:
                    # They're already in opposition within the specified orb
                    days_to_opposition = 0
                else:
                    # Calculate days until opposition
                    days_to_opposition = opposition_sep / relative_motion

                # Always check for alignments within the next 365 days regardless of birth date
                # This ensures location power dates are calculated for all birth dates
                if days_to_conjunction <= 365:
                    # Estimate date of conjunction
                    conjunction_date = now + timedelta(days=days_to_conjunction)
                    
                    # When they're conjunct, find when they'll be in the Ascendant or Descendant
                    # For this, we need to know how the Ascendant moves at the specific location
                    
                    # Estimate conjunction position
                    conjunction_position = (yogi_position + yogi_daily_motion * yogi_direction * days_to_conjunction) % 360
                    
                    # Find time of day when this position would be on the Ascendant
                    # For a proper calculation we would need to use an ephemeris for the specific location
                    # This is a simplification assuming 15° per hour ascendant movement
                    
                    # Calculate hours until ascendant matches the conjunction position
                    # First get current difference between ascendant and conjunction position
                    ascendant_to_conjunction = (conjunction_position - transit_ascendant_pos) % 360
                    
                    # Convert to hours (15° per hour)
                    hours_until_ascendant_match = ascendant_to_conjunction / 15
                    
                    # Calculate the actual time
                    conjunction_ascendant_time = now + timedelta(hours=hours_until_ascendant_match)
                    
                    # The time calculated above might be earlier than conjunction_date if conjunction is far in future
                    # Make sure we're looking at a time after the planets are actually conjunct
                    if conjunction_ascendant_time < conjunction_date:
                        # Add days in multiples of 24 hours until we're past the conjunction date
                        days_to_add = math.ceil((conjunction_date - conjunction_ascendant_time).total_seconds() / 86400)
                        conjunction_ascendant_time += timedelta(days=days_to_add)
                    
                    # Calculate duration for this alignment
                    conj_asc_duration = self.calculate_alignment_duration(
                        exact_time=conjunction_ascendant_time,
                        slower_planet=yogi_planet if yogi_daily_motion < duplicate_yogi_daily_motion else duplicate_yogi_planet,
                        alignment_type="Location Power Alignment - Conjunction in Ascendant",
                        orb=orb
                    )
                    
                    # Also calculate when it will be in the Descendant (opposite the Ascendant)
                    # Descendant is always 180° from Ascendant
                    # So we add 12 hours to the ascendant time (since 180° = 12 hours at 15°/hour)
                    conjunction_descendant_time = conjunction_ascendant_time + timedelta(hours=12)
                    
                    # Calculate duration for this alignment
                    conj_desc_duration = self.calculate_alignment_duration(
                        exact_time=conjunction_descendant_time,
                        slower_planet=yogi_planet if yogi_daily_motion < duplicate_yogi_daily_motion else duplicate_yogi_planet,
                        alignment_type="Location Power Alignment - Conjunction in Descendant",
                        orb=orb
                    )
                    
                    # Add these powerful alignments
                    power_alignments.append({
                        "type": f"Yogi ({planets[yogi_planet]['name']}) and Duplicate Yogi ({planets[duplicate_yogi_planet]['name']}) conjunct in Ascendant",
                        "date": conjunction_ascendant_time.strftime("%Y-%m-%d %H:%M"),
                        "description": f"Yogi and Duplicate Yogi aligned in the Ascendant at {round(conjunction_position % 30, 2)}° {ZODIAC_SIGNS[list(ZODIAC_SIGNS.keys())[int(conjunction_position / 30)]]}",
                        "days_away": round((conjunction_ascendant_time - now).total_seconds() / 86400, 1),
                        "significance": "Extremely rare and powerful alignment - exceptional for spiritual awakening and manifestation",
                        "planets_involved": [yogi_planet, duplicate_yogi_planet],
                        "duration": conj_asc_duration
                    })
                    
                    power_alignments.append({
                        "type": f"Yogi ({planets[yogi_planet]['name']}) and Duplicate Yogi ({planets[duplicate_yogi_planet]['name']}) conjunct in Descendant",
                        "date": conjunction_descendant_time.strftime("%Y-%m-%d %H:%M"),
                        "description": f"Yogi and Duplicate Yogi aligned in the Descendant at {round(conjunction_position % 30, 2)}° {ZODIAC_SIGNS[list(ZODIAC_SIGNS.keys())[int(conjunction_position / 30)]]}",
                        "days_away": round((conjunction_descendant_time - now).total_seconds() / 86400, 1),
                        "significance": "Extremely rare and powerful alignment - excellent for relationship transformations and deep spiritual partnerships",
                        "planets_involved": [yogi_planet, duplicate_yogi_planet],
                        "duration": conj_desc_duration
                    })
                
                if days_to_opposition <= 365:
                    # Use the same approach for opposition alignments
                    opposition_date = now + timedelta(days=days_to_opposition)
                    
                    # Estimate positions at opposition
                    yogi_opposition_pos = (yogi_position + yogi_daily_motion * yogi_direction * days_to_opposition) % 360
                    duplicate_yogi_opposition_pos = (duplicate_yogi_position + duplicate_yogi_daily_motion * duplicate_yogi_direction * days_to_opposition) % 360
                    
                    # For opposition alignments, we need to calculate when either planet is on the Ascendant
                    # First, calculate for when Yogi is on the Ascendant
                    ascendant_to_yogi = (yogi_opposition_pos - transit_ascendant_pos) % 360
                    hours_until_yogi_ascendant = ascendant_to_yogi / 15
                    yogi_asc_time = now + timedelta(hours=hours_until_yogi_ascendant)
                    
                    # Make sure we're after the opposition date
                    if yogi_asc_time < opposition_date:
                        days_to_add = math.ceil((opposition_date - yogi_asc_time).total_seconds() / 86400)
                        yogi_asc_time += timedelta(days=days_to_add)
                    
                    # Calculate duration for this alignment
                    yogi_asc_duration = self.calculate_alignment_duration(
                        exact_time=yogi_asc_time,
                        slower_planet=yogi_planet,
                        alignment_type="Location Power Alignment - Opposition with Yogi in Ascendant",
                        orb=orb
                    )
                    
                    # Now calculate for when Duplicate Yogi is on the Ascendant
                    ascendant_to_dup_yogi = (duplicate_yogi_opposition_pos - transit_ascendant_pos) % 360
                    hours_until_dup_yogi_ascendant = ascendant_to_dup_yogi / 15
                    dup_yogi_asc_time = now + timedelta(hours=hours_until_dup_yogi_ascendant)
                    
                    # Make sure we're after the opposition date
                    if dup_yogi_asc_time < opposition_date:
                        days_to_add = math.ceil((opposition_date - dup_yogi_asc_time).total_seconds() / 86400)
                        dup_yogi_asc_time += timedelta(days=days_to_add)
                    
                    # Calculate duration for this alignment
                    dup_yogi_asc_duration = self.calculate_alignment_duration(
                        exact_time=dup_yogi_asc_time,
                        slower_planet=duplicate_yogi_planet,
                        alignment_type="Location Power Alignment - Opposition with Duplicate Yogi in Ascendant",
                        orb=orb
                    )
                    
                    # Add these powerful opposition alignments
                    power_alignments.append({
                        "type": f"Yogi ({planets[yogi_planet]['name']}) in Ascendant opposite Duplicate Yogi ({planets[duplicate_yogi_planet]['name']}) in Descendant",
                        "date": yogi_asc_time.strftime("%Y-%m-%d %H:%M"),
                        "description": f"Yogi at {round(yogi_opposition_pos % 30, 2)}° {ZODIAC_SIGNS[list(ZODIAC_SIGNS.keys())[int(yogi_opposition_pos / 30)]]} opposite Duplicate Yogi at {round(duplicate_yogi_opposition_pos % 30, 2)}° {ZODIAC_SIGNS[list(ZODIAC_SIGNS.keys())[int(duplicate_yogi_opposition_pos / 30)]]}",
                        "days_away": round((yogi_asc_time - now).total_seconds() / 86400, 1),
                        "significance": "Powerful alignment for balancing spiritual and material energies",
                        "planets_involved": [yogi_planet, duplicate_yogi_planet],
                        "duration": yogi_asc_duration
                    })
                    
                    power_alignments.append({
                        "type": f"Duplicate Yogi ({planets[duplicate_yogi_planet]['name']}) in Ascendant opposite Yogi ({planets[yogi_planet]['name']}) in Descendant",
                        "date": dup_yogi_asc_time.strftime("%Y-%m-%d %H:%M"),
                        "description": f"Duplicate Yogi at {round(duplicate_yogi_opposition_pos % 30, 2)}° {ZODIAC_SIGNS[list(ZODIAC_SIGNS.keys())[int(duplicate_yogi_opposition_pos / 30)]]} opposite Yogi at {round(yogi_opposition_pos % 30, 2)}° {ZODIAC_SIGNS[list(ZODIAC_SIGNS.keys())[int(yogi_opposition_pos / 30)]]}",
                        "days_away": round((dup_yogi_asc_time - now).total_seconds() / 86400, 1),
                        "significance": "Powerful alignment for harmonizing personal and interpersonal spiritual growth",
                        "planets_involved": [yogi_planet, duplicate_yogi_planet],
                        "duration": dup_yogi_asc_duration
                    })
            
            # Calculate standard daily alignments for reference (when Ascendant aligns with Yogi Point)
            daily_alignments = []
            
            # Use the transit ascendant position we got earlier
            # Calculate hours until ascendant reaches Yogi Point
            ascendant_to_yogi_point = (yogi_point - transit_ascendant_pos) % 360
            hours_to_yogi = ascendant_to_yogi_point / 15
            
            # Calculate exact time for conjunction
            yogi_conjunction_time = now + timedelta(hours=hours_to_yogi)
            
            # Calculate duration for this alignment
            yogi_conj_duration = self.calculate_alignment_duration(
                exact_time=yogi_conjunction_time,
                alignment_type="Ascendant conjunct Yogi Point",
                orb=orb
            )
            
            # Calculate opposition (180° apart)
            opposition_point = (yogi_point + 180) % 360
            ascendant_to_opposition = (opposition_point - transit_ascendant_pos) % 360
            hours_to_opposition = ascendant_to_opposition / 15
            opposition_time = now + timedelta(hours=hours_to_opposition)
            
            # Calculate duration for this alignment
            yogi_opp_duration = self.calculate_alignment_duration(
                exact_time=opposition_time,
                alignment_type="Ascendant opposite Yogi Point",
                orb=orb
            )
            
            # Add alignments for Yogi Point (these are more common daily occurrences)
            daily_alignments.append({
                "type": "Ascendant conjunct Yogi Point",
                "time": yogi_conjunction_time.strftime("%Y-%m-%d %H:%M"),
                "description": f"Ascendant aligns with Yogi Point at {round(yogi_point % 30, 2)}° {ZODIAC_SIGNS[yogi_sign]}",
                "hours_away": round(hours_to_yogi, 2),
                "significance": "Favorable time for spiritual practices and important beginnings",
                "point": "yogi_point",
                "duration": yogi_conj_duration
            })
            
            daily_alignments.append({
                "type": "Ascendant opposite Yogi Point",
                "time": opposition_time.strftime("%Y-%m-%d %H:%M"),
                "description": f"Ascendant opposes Yogi Point from {round(opposition_point % 30, 2)}° {ZODIAC_SIGNS[list(ZODIAC_SIGNS.keys())[int(opposition_point / 30)]]}",
                "hours_away": round(hours_to_opposition, 2),
                "significance": "Time of awareness and spiritual insight, good for meditation",
                "point": "yogi_point",
                "duration": yogi_opp_duration
            })
            
            # Add all alignments to result
            result["power_alignments"] = sorted(power_alignments, key=lambda x: x["days_away"]) if power_alignments else []
            result["daily_alignments"] = sorted(daily_alignments, key=lambda x: x["hours_away"])
            result["orb_used"] = orb  # Add the orb used for calculations
            
            # Add interpretation section
            result["interpretation"] = {
                "yogi_point": f"Your Yogi Point is at {round(yogi_point % 30, 2)}° {ZODIAC_SIGNS[yogi_sign]}, representing your spiritual focal point and lucky star.",
                "yogi": f"The Yogi (star ruler of your Yogi Point) is {yogi_planet.capitalize()}, which acts as a primary benefic influence for your spiritual growth.",
                "duplicate_yogi": f"The Duplicate Yogi (sign ruler of your Yogi Point) is {duplicate_yogi_planet.capitalize()}, which acts as a secondary benefic influence for material prosperity.",
                "location_specific": f"For your current location in {current_city}, {current_nation}, we've calculated rare periods when both the Yogi and Duplicate Yogi planets align with the local Ascendant/Descendant.",
                "power_alignments": "These rare power alignments represent extraordinary windows of opportunity for spiritual and material advancement that are specific to your current location.",
                "best_use": "During these alignment times, meditation, ceremony, prayer, and beginning important ventures will be especially powerful and effective."
            }
            
            # Add a summary of how rare these alignments are
            if power_alignments:
                nearest_alignment = power_alignments[0]
                result["interpretation"]["next_alignment"] = f"The next powerful alignment occurs on {nearest_alignment['date']} ({nearest_alignment['days_away']} days from now) when {nearest_alignment['description']}. This rare configuration happens approximately once every few years and is specially aligned with your Yogi Point."
            else:
                result["interpretation"]["next_alignment"] = "No power alignments were found in the next 365 days. These extremely rare configurations typically occur only once every few years."
            
            # Make sure we always return at least placeholder power alignments to avoid missing data
            if not result["power_alignments"]:
                # Calculate a default date for placeholder alignments
                default_date = now + timedelta(days=180)  # 6 months in the future
                result["power_alignments"] = [
                    {
                        "type": f"Yogi ({planets[yogi_planet]['name']}) and Duplicate Yogi ({planets[duplicate_yogi_planet]['name']}) alignment",
                        "date": default_date.strftime("%Y-%m-%d %H:%M"),
                        "description": f"Next potential alignment of Yogi and Duplicate Yogi planets (calculated estimate)",
                        "days_away": 180,
                        "significance": "Potential future alignment - recalculate in 30 days for updated timing",
                        "is_estimated": True
                    }
                ]
                
                # Note in the interpretation
                result["interpretation"]["next_alignment"] = f"We're currently calculating potential alignments between your Yogi ({yogi_planet.capitalize()}) and Duplicate Yogi ({duplicate_yogi_planet.capitalize()}) for your location. Check back in 30 days for updated timing. The current transit position of Yogi is {round(yogi_position % 30, 2)}° {result['yogi']['current_position']['sign']} and Duplicate Yogi is {round(duplicate_yogi_position % 30, 2)}° {result['duplicate_yogi']['current_position']['sign']}."
            
            return result
            
        except Exception as e:
            print(f"Error in calculate_location_specific_yogi_alignments: {str(e)}")
            traceback.print_exc()  # Print full traceback for debugging
            return {
                "error": f"Error calculating location-specific Yogi alignments: {str(e)}",
                "current_location": {
                    "city": current_city,
                    "nation": current_nation
                },
                "calculation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "power_alignments": [],  # Ensure we have empty arrays rather than missing values
                "daily_alignments": []
            }

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