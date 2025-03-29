import json
from datetime import datetime, timedelta
import math
from typing import Dict, Any, List, Optional, Tuple

# Import other utility modules that might be needed
from .yogi_point_utils import ZODIAC_SIGNS
from .aspect_utils import PLANET_DAILY_MOTION, find_closest_aspect, find_last_aspect, calculate_alignment_duration


def calculate_jupiter_pof_last_conjunction(natal_data: Dict[str, Any], transit_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate when Jupiter was last conjunct with the natal Part of Fortune.
    
    Args:
        natal_data: The natal chart data dictionary
        transit_data: The transit chart data dictionary
        
    Returns:
        Dictionary containing Jupiter-POF conjunction data
    """
    try:
        # Calculate the natal Part of Fortune position
        natal_asc_pos = natal_data["subject"]["houses"]["ascendant"]["abs_pos"]
        natal_moon_pos = natal_data["subject"]["planets"]["moon"]["abs_pos"]
        natal_sun_pos = natal_data["subject"]["planets"]["sun"]["abs_pos"]
        
        # Use the utility function to determine if it's a day or night chart
        from .dasha_utils import determine_day_night_chart
        is_day_chart = determine_day_night_chart(natal_sun_pos, natal_asc_pos, natal_data)
        
        # Calculate Part of Fortune position
        if is_day_chart:
            pof_pos = (natal_asc_pos + natal_moon_pos - natal_sun_pos) % 360
 
            pof_pos = (natal_asc_pos - natal_moon_pos + natal_sun_pos) % 360
       
        
        # Get current Jupiter position
        current_jupiter_pos = transit_data["transit"]["subject"]["planets"]["jupiter"]["abs_pos"]
        jupiter_is_retrograde = transit_data["transit"]["subject"]["planets"]["jupiter"]["retrograde"]
        
        # Get Jupiter's daily motion
        jupiter_daily_motion = PLANET_DAILY_MOTION["jupiter"]
        
        # Calculate angular distance between Jupiter and Part of Fortune
        angle_diff = min(
            abs(current_jupiter_pos - pof_pos),
            abs(current_jupiter_pos - pof_pos - 360),
            abs(current_jupiter_pos - pof_pos + 360)
        )
        
        # Determine if Jupiter is past the POF
        jupiter_past_pof = (current_jupiter_pos > pof_pos and (current_jupiter_pos - pof_pos) < 180) or \
                          (current_jupiter_pos < pof_pos and (pof_pos - current_jupiter_pos) > 180)
        
        # Estimate days since last conjunction
        if jupiter_past_pof:
            days_since_conjunction = int(angle_diff / jupiter_daily_motion)
        else:
            days_since_conjunction = int((360 - angle_diff) / jupiter_daily_motion)
        
        # Calculate the estimated date
        today = datetime.now()
        last_conjunction_date = today - timedelta(days=days_since_conjunction)
        
        # Calculate days until next conjunction (Jupiter's full cycle is about 12 years)
        days_until_next = int((360 - angle_diff) / jupiter_daily_motion) if jupiter_past_pof else int(angle_diff / jupiter_daily_motion)
        next_conjunction_date = today + timedelta(days=days_until_next)
        
        # Calculate duration of the conjunction
        # Jupiter moves at approximately 0.083 degrees per day
        # For a tight orb of 1 degree, that's about 12 days on either side
        conjunction_duration = {
            "days": 24,
            "start_date": (last_conjunction_date - timedelta(days=12)).strftime("%Y-%m-%d"),
            "exact_date": last_conjunction_date.strftime("%Y-%m-%d"),
            "end_date": (last_conjunction_date + timedelta(days=12)).strftime("%Y-%m-%d"),
            "description": f"This aspect was active for approximately 24 days, from {(last_conjunction_date - timedelta(days=12)).strftime('%Y-%m-%d')} to {(last_conjunction_date + timedelta(days=12)).strftime('%Y-%m-%d')}"
        }
        
        next_conjunction_duration = {
            "days": 24,
            "start_date": (next_conjunction_date - timedelta(days=12)).strftime("%Y-%m-%d"),
            "exact_date": next_conjunction_date.strftime("%Y-%m-%d"),
            "end_date": (next_conjunction_date + timedelta(days=12)).strftime("%Y-%m-%d"),
            "description": f"This aspect will be active for approximately 24 days, from {(next_conjunction_date - timedelta(days=12)).strftime('%Y-%m-%d')} to {(next_conjunction_date + timedelta(days=12)).strftime('%Y-%m-%d')}"
        }
        
        # Print the results for debugging
        print("\n--------- JUPITER-PART OF FORTUNE CONJUNCTION ANALYSIS ---------")
        print(f"Natal Part of Fortune position: {pof_pos:.2f}° ({list(ZODIAC_SIGNS.keys())[int(pof_pos / 30)]} {pof_pos % 30:.2f}°)")
        print(f"Current Jupiter position: {current_jupiter_pos:.2f}° ({list(ZODIAC_SIGNS.keys())[int(current_jupiter_pos / 30)]} {current_jupiter_pos % 30:.2f}°)")
        print(f"Angular distance: {angle_diff:.2f}°")
        print(f"Jupiter is currently {'retrograde' if jupiter_is_retrograde else 'direct'}")
        print(f"Jupiter has {'passed' if jupiter_past_pof else 'not yet reached'} the Part of Fortune")
        print(f"Estimated last conjunction: {last_conjunction_date.strftime('%Y-%m-%d')} ({days_since_conjunction} days ago)")
        print(f"Estimated next conjunction: {next_conjunction_date.strftime('%Y-%m-%d')} (in {days_until_next} days)")
        print(f"Jupiter takes approximately {int(360/jupiter_daily_motion/365.25)} years to complete a full cycle")
        print("---------------------------------------------------------------\n")
        
        # Return the data
        return {
            "part_of_fortune": {
                "position": pof_pos,
                "sign": list(ZODIAC_SIGNS.keys())[int(pof_pos / 30)],
                "degree": round(pof_pos % 30, 2)
            },
            "current_jupiter": {
                "position": current_jupiter_pos,
                "sign": list(ZODIAC_SIGNS.keys())[int(current_jupiter_pos / 30)],
                "degree": round(current_jupiter_pos % 30, 2),
                "is_retrograde": jupiter_is_retrograde
            },
            "angular_distance": round(angle_diff, 2),
            "jupiter_past_pof": jupiter_past_pof,
            "last_conjunction": {
                "date": last_conjunction_date.strftime("%Y-%m-%d"),
                "days_ago": days_since_conjunction,
                "duration": conjunction_duration
            },
            "next_conjunction": {
                "date": next_conjunction_date.strftime("%Y-%m-%d"),
                "days_away": days_until_next,
                "duration": next_conjunction_duration
            },
            "cycle_years": int(360/jupiter_daily_motion/365.25)
        }
    except Exception as e:
        print(f"Error calculating Jupiter-Part of Fortune conjunction: {str(e)}")
        return {
            "error": f"Error calculating Jupiter-Part of Fortune conjunction: {str(e)}"
        }


def get_next_venus_aspects(natal_data: Dict[str, Any], transit_data: Dict[str, Any], orb: float = 3.0) -> Dict[str, Any]:
    """
    Find upcoming Venus aspects to the Yogi Point and Ava Yogi Point
    
    Args:
        natal_data: Natal chart data dictionary
        transit_data: Transit chart data dictionary
        orb: Orb value for aspects (default: 3.0)
        
    Returns:
        Dictionary containing Venus aspect data
    """
    from .yogi_point_utils import calculate_yogi_point, calculate_ava_yogi_point
    
    try:
        # Calculate Yogi Point
        yogi_point = calculate_yogi_point(natal_data)
        
        # Calculate Ava Yogi Point (challenging point)
        ava_yogi_point = calculate_ava_yogi_point(yogi_point)
        
        # Get current Venus position
        # Check if Venus is available in the chart data
        if "venus" not in transit_data["transit"]["subject"]["planets"]:
            # Return error if Venus isn't available
            return {
                "error": "Venus data is not available in the transit chart. This might be due to sidereal mode settings.",
                "yogi_point": {
                    "absolute_position": yogi_point,
                    "sign": list(ZODIAC_SIGNS.keys())[int(yogi_point / 30)],
                    "degree": round(yogi_point % 30, 2)
                },
                "ava_yogi_point": {
                    "absolute_position": ava_yogi_point,
                    "sign": list(ZODIAC_SIGNS.keys())[int(ava_yogi_point / 30)],
                    "degree": round(ava_yogi_point % 30, 2)
                }
            }
        
        current_venus_pos = transit_data["transit"]["subject"]["planets"]["venus"]["abs_pos"]
        is_venus_retrograde = transit_data["transit"]["subject"]["planets"]["venus"]["retrograde"]
        venus_sign = transit_data["transit"]["subject"]["planets"]["venus"]["sign"]
        venus_degree = current_venus_pos % 30
        
        # Initialize results
        venus_yogi_aspects = []
        venus_ava_yogi_aspects = []
        today = datetime.now()
        
        # Venus moves approximately 1° per day (adjusted for retrograde if needed)
        venus_daily_motion = 1.0 if not is_venus_retrograde else 0.8  # Retrograde is usually a bit slower
        
        # Use the provided orb parameter instead of a fixed value
        standard_orb = orb
        
        # Define aspect points for Yogi Point
        aspect_points = {
            'conjunction': yogi_point,
            'trine1': (yogi_point + 120) % 360,
            'trine2': (yogi_point - 120) % 360,
            'sextile1': (yogi_point + 60) % 360,
            'sextile2': (yogi_point - 60) % 360,
            'square1': (yogi_point + 90) % 360,
            'square2': (yogi_point - 90) % 360,
            'opposition': (yogi_point + 180) % 360
        }
        
        # For each aspect point, calculate estimated date of aspect
        for aspect_name, aspect_point in aspect_points.items():
            # Calculate shortest distance to aspect point
            direct_diff = (aspect_point - current_venus_pos) % 360
            retro_diff = (current_venus_pos - aspect_point) % 360
            
            # Determine which direction Venus needs to move
            is_direct_aspect = direct_diff <= retro_diff
            
            # Calculate the right distance based on Venus's actual motion (direct or retrograde)
            if (is_direct_aspect and not is_venus_retrograde) or (not is_direct_aspect and is_venus_retrograde):
                # Venus is already moving in the right direction
                distance = min(direct_diff, retro_diff)
            else:
                # Venus needs to go the long way around
                distance = 360 - min(direct_diff, retro_diff)
                
            # Calculate days to aspect
            days_to_aspect = int(distance / venus_daily_motion)
            
            # Cap at reasonable timeframe
            days_to_aspect = min(days_to_aspect, 365)  # Venus will make all aspects within a year
            
            # Calculate estimated date
            estimated_date = today + timedelta(days=days_to_aspect)
            
            # Calculate duration of aspect (how long Venus will be within orb)
            # Venus will be within orb for 2 * orb degrees
            # So if orb is 3 degrees, Venus will be within orb for 6 degrees total
            # (3 degrees before exact aspect, 3 degrees after)
            duration_days = int((2 * standard_orb) / venus_daily_motion)
            
            # Calculate when aspect begins (entering orb)
            start_date = estimated_date - timedelta(days=int(standard_orb / venus_daily_motion))
            
            # Calculate when aspect ends (leaving orb)
            end_date = estimated_date + timedelta(days=int(standard_orb / venus_daily_motion))
            
            # Store aspect information
            base_aspect = aspect_name.rstrip('12')  # Remove number from trine1/trine2 etc
            
            venus_yogi_aspects.append({
                'aspect_type': base_aspect,
                'estimated_date': estimated_date.strftime("%Y-%m-%d"),
                'days_to_aspect': days_to_aspect,
                'aspect_point': aspect_point,
                'distance': round(distance, 2),
                'interpretation': interpret_venus_aspect(base_aspect, "yogi"),
                'duration': {
                    'days': duration_days,
                    'start_date': start_date.strftime("%Y-%m-%d"),
                    'exact_date': estimated_date.strftime("%Y-%m-%d"),
                    'end_date': end_date.strftime("%Y-%m-%d"),
                    'description': f"This aspect is active for approximately {duration_days} days, from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                }
            })
        
        # Do the same for Ava Yogi Point (challenging aspects)
        ava_aspect_points = {
            'conjunction': ava_yogi_point,
            'trine1': (ava_yogi_point + 120) % 360,
            'trine2': (ava_yogi_point - 120) % 360,
            'sextile1': (ava_yogi_point + 60) % 360,
            'sextile2': (ava_yogi_point - 60) % 360,
            'square1': (ava_yogi_point + 90) % 360,
            'square2': (ava_yogi_point - 90) % 360,
            'opposition': (ava_yogi_point + 180) % 360
        }
        
        for aspect_name, aspect_point in ava_aspect_points.items():
            direct_diff = (aspect_point - current_venus_pos) % 360
            retro_diff = (current_venus_pos - aspect_point) % 360
            
            is_direct_aspect = direct_diff <= retro_diff
            
            if (is_direct_aspect and not is_venus_retrograde) or (not is_direct_aspect and is_venus_retrograde):
                distance = min(direct_diff, retro_diff)
            else:
                distance = 360 - min(direct_diff, retro_diff)
                
            days_to_aspect = int(distance / venus_daily_motion)
            days_to_aspect = min(days_to_aspect, 365)
            
            estimated_date = today + timedelta(days=days_to_aspect)
            
            # Calculate duration of aspect (how long Venus will be within orb)
            duration_days = int((2 * standard_orb) / venus_daily_motion)
            
            # Calculate when aspect begins (entering orb)
            start_date = estimated_date - timedelta(days=int(standard_orb / venus_daily_motion))
            
            # Calculate when aspect ends (leaving orb)
            end_date = estimated_date + timedelta(days=int(standard_orb / venus_daily_motion))
            
            base_aspect = aspect_name.rstrip('12')
            
            venus_ava_yogi_aspects.append({
                'aspect_type': base_aspect,
                'estimated_date': estimated_date.strftime("%Y-%m-%d"),
                'days_to_aspect': days_to_aspect,
                'aspect_point': aspect_point,
                'distance': round(distance, 2),
                'interpretation': interpret_venus_aspect(base_aspect, "ava_yogi"),
                'duration': {
                    'days': duration_days,
                    'start_date': start_date.strftime("%Y-%m-%d"),
                    'exact_date': estimated_date.strftime("%Y-%m-%d"),
                    'end_date': end_date.strftime("%Y-%m-%d"),
                    'description': f"This aspect is active for approximately {duration_days} days, from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                }
            })
        
        # Sort aspects by days to aspect
        venus_yogi_aspects.sort(key=lambda x: x['days_to_aspect'])
        venus_ava_yogi_aspects.sort(key=lambda x: x['days_to_aspect'])
        
        # Create response
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
            "current_venus": {
                "absolute_position": current_venus_pos,
                "sign": venus_sign,
                "degree": round(venus_degree, 2),
                "is_retrograde": is_venus_retrograde
            },
            "venus_yogi_aspects": venus_yogi_aspects,
            "venus_ava_yogi_aspects": venus_ava_yogi_aspects,
            "interpretation": {
                "yogi_point": f"Your Yogi Point at {round(yogi_point % 30, 2)}° in {ZODIAC_SIGNS[list(ZODIAC_SIGNS.keys())[int(yogi_point / 30)]]} indicates times of heightened spiritual awareness and fortune when activated by Venus transits"
            }
        }
        
        return response
    except Exception as e:
        print(f"Error calculating Venus aspects: {str(e)}")
        return {
            "error": f"Error calculating Venus aspects: {str(e)}"
        }


def interpret_venus_aspect(aspect_type: str, point_type: str = "yogi") -> str:
    """
    Interpret a Venus aspect to either the Yogi or Ava Yogi Point
    
    Args:
        aspect_type: Type of aspect (conjunction, trine, sextile, square, opposition)
        point_type: Type of point (yogi or ava_yogi)
        
    Returns:
        String interpretation of the aspect
    """
    # Interpretations for Venus aspects to Yogi Point
    yogi_interpretations = {
        'conjunction': "Venus conjunction to your Yogi Point brings a heightened sense of pleasure, beauty, and harmony. This is an excellent time for social activities, creative pursuits, and matters of the heart. You may feel more attractive and magnetic to others, and relationships of all kinds are favored. Financial opportunities may also present themselves.",
        'trine': "Venus trine to your Yogi Point creates a harmonious flow of artistic inspiration, social connection, and financial opportunity. This is a favorable time for creative projects, romance, and diplomatic endeavors. You'll find it easier to attract positive relationships and material resources with less effort than usual.",
        'sextile': "Venus sextile to your Yogi Point offers opportunities for creative expression, social connection, and financial gain. This aspect encourages you to actively pursue aesthetic pleasures, romantic interests, and collaborative projects. A little initiative in these areas can lead to significant rewards.",
        'square': "Venus square to your Yogi Point may create tension between your spiritual path and your desires for pleasure, beauty, or connection. This is a time to find balance between material enjoyments and higher aspirations. Relationships may require extra attention, and financial decisions should be made with care.",
        'opposition': "Venus opposition to your Yogi Point brings awareness about how your relationships and values impact your spiritual growth. This aspect illuminates potential imbalances between giving and receiving, or between material and spiritual priorities. Diplomatic negotiations and compromises in relationships may be necessary."
    }
    
    # Interpretations for Venus aspects to Ava Yogi Point (more challenging)
    ava_yogi_interpretations = {
        'conjunction': "Venus conjunction to your Ava Yogi Point may bring challenges in relationships, finances, or self-worth. Be cautious about overindulgence, excessive spending, or seeking validation through others. This transit can reveal where you might be placing too much importance on external beauty or material possessions.",
        'trine': "Venus trine to your Ava Yogi Point can ease challenging situations related to relationships or finances, but may also lead to complacency or taking the path of least resistance. Be mindful of overlooking important details in agreements or becoming too comfortable with unsatisfactory situations.",
        'sextile': "Venus sextile to your Ava Yogi Point offers opportunities to address relationship or financial challenges through creative problem-solving. However, this aspect may tempt you to choose pleasure over necessary growth. Balance enjoyment with responsibility during this time.",
        'square': "Venus square to your Ava Yogi Point creates tension around values, relationships, and resources. This aspect can highlight conflicts between what you desire and what truly serves your highest good. Financial stress or relationship disagreements may emerge to teach important lessons about attachment.",
        'opposition': "Venus opposition to your Ava Yogi Point brings awareness of relationship patterns or value systems that may be undermining your well-being. This transit illuminates where you might be compromising too much for harmony or placing too much importance on external validation."
    }
    
    # Return the appropriate interpretation based on aspect type and point type
    if point_type == "yogi":
        return yogi_interpretations.get(aspect_type, "This Venus aspect to your Yogi Point influences your experiences with harmony, beauty, relationships, and resources.")
    else:
        return ava_yogi_interpretations.get(aspect_type, "This Venus aspect to your Ava Yogi Point may present challenges related to values, relationships, or resources that require careful navigation.")


def calculate_triple_alignments(yogi_point: float, duplicate_yogi: float, 
                              ascendant_pos: float, ascendant_lord_pos: float,
                              ascendant_lord: str, lord_daily_motion: float,
                              ascendant_lord_retrograde: bool, orb: float = 3.0) -> List[Dict[str, Any]]:
    """
    Calculate triple alignments between Yogi point, duplicate Yogi, and ascendant or other points
    
    Args:
        yogi_point: The Yogi point position in degrees
        duplicate_yogi: The duplicate Yogi position in degrees
        ascendant_pos: The ascendant position in degrees
        ascendant_lord_pos: The ascendant lord position in degrees
        ascendant_lord: The ascendant lord planet name
        lord_daily_motion: The daily motion of the ascendant lord
        ascendant_lord_retrograde: Whether the ascendant lord is retrograde
        orb: The orb value to use for aspects (default: 3.0)
        
    Returns:
        List of dictionary containing triple alignment data
    """
    # Triple alignments involve yogi point, duplicate yogi, and ascendant all aligned
    try:
        # Initialize result list
        triple_alignments = []
        
        # Get current time for reference
        current_time = datetime.now()
        
        # Case 1: Yogi Point on Ascendant, Duplicate Yogi aspecting
        # Calculate when Yogi Point will be conjunct Ascendant
        ascendant_motion = 360 / 24  # Ascendant moves through entire zodiac in 24 hours
        yogi_asc_diff = (yogi_point - ascendant_pos) % 360
        hours_to_yogi_asc = yogi_asc_diff / (360 / 24)
        
        # If hours is greater than 24, take modulo
        hours_to_yogi_asc = hours_to_yogi_asc % 24
        
        # Calculate the time when Yogi Point will be conjunct Ascendant
        yogi_asc_time = current_time + timedelta(hours=hours_to_yogi_asc)
        
        # Calculate angle between Duplicate Yogi and Ascendant at that time
        # Note: This is simplified - in reality we'd need to calculate the exact position
        # of Duplicate Yogi at that future time, which would require more detailed transit calculations
        
        # For now, we'll estimate by assuming the Duplicate Yogi (ascendant lord) moves at its average daily rate
        # Convert hours to days
        days_to_yogi_asc = hours_to_yogi_asc / 24
        
        # Calculate how much the duplicate yogi will move in that time
        if ascendant_lord_retrograde:
            duplicate_yogi_movement = -lord_daily_motion * days_to_yogi_asc
        else:
            duplicate_yogi_movement = lord_daily_motion * days_to_yogi_asc
        
        # Calculate new position of duplicate yogi at the time of Yogi Point-Ascendant conjunction
        future_duplicate_yogi_pos = (duplicate_yogi + duplicate_yogi_movement) % 360
        
        # Calculate if Duplicate Yogi will be making any major aspect to the Ascendant at that time
        # Major aspects: conjunction (0°), opposition (180°), trine (120°), square (90°), sextile (60°)
        aspects = [
            {"type": "conjunction", "angle": 0, "orb": orb},
            {"type": "opposition", "angle": 180, "orb": orb},
            {"type": "trine", "angle": 120, "orb": orb},
            {"type": "trine", "angle": 240, "orb": orb},  # 2nd trine
            {"type": "square", "angle": 90, "orb": orb},
            {"type": "square", "angle": 270, "orb": orb},  # 2nd square
            {"type": "sextile", "angle": 60, "orb": orb},
            {"type": "sextile", "angle": 300, "orb": orb}  # 2nd sextile
        ]
        
        for aspect in aspects:
            # Calculate aspect point
            aspect_point = (yogi_point + aspect["angle"]) % 360
            
            # Calculate if the duplicate yogi is within orb of this aspect point
            aspect_diff = min(
                abs(future_duplicate_yogi_pos - aspect_point),
                abs(future_duplicate_yogi_pos - aspect_point - 360),
                abs(future_duplicate_yogi_pos - aspect_point + 360)
            )
            
            if aspect_diff <= aspect["orb"]:
                # We have a triple alignment!
                # Calculate how long the aspect will be active (within orb)
                aspect_duration_hours = (aspect["orb"] * 2) / ascendant_motion
                
                # Create the alignment entry
                alignment = {
                    "type": f"Yogi Point conjunct Ascendant with {ascendant_lord.capitalize()} {aspect['type']}",
                    "time": yogi_asc_time.strftime("%Y-%m-%d %H:%M"),
                    "formatted_time": yogi_asc_time.strftime("%B %d, %Y at %I:%M %p"),
                    "days_away": days_to_yogi_asc,
                    "hours_away": hours_to_yogi_asc,
                    "duration": {
                        "hours": round(aspect_duration_hours, 1),
                        "start_time": (yogi_asc_time - timedelta(hours=aspect_duration_hours/2)).strftime("%Y-%m-%d %H:%M"),
                        "exact_time": yogi_asc_time.strftime("%Y-%m-%d %H:%M"),
                        "end_time": (yogi_asc_time + timedelta(hours=aspect_duration_hours/2)).strftime("%Y-%m-%d %H:%M"),
                        "description": f"This alignment is active for approximately {round(aspect_duration_hours, 1)} hours."
                    },
                    "description": f"The Yogi Point will be conjunct the Ascendant with {ascendant_lord.capitalize()} making a {aspect['type']} aspect. This creates a powerful window for spiritual growth, manifestation, and aligning with your highest potential."
                }
                
                triple_alignments.append(alignment)
        
        # Sort alignments by time
        triple_alignments.sort(key=lambda x: x["hours_away"])
        
        return triple_alignments
    
    except Exception as e:
        print(f"Error calculating triple alignments: {str(e)}")
        return [{"error": f"Error calculating triple alignments: {str(e)}"}] 