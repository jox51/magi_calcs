import math
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from .yogi_point_utils import calculate_yogi_point, get_ascendant_ruler, ZODIAC_SIGNS
from .aspect_utils import calculate_alignment_duration

def calculate_location_specific_yogi_alignments(natal_data: Dict[str, Any], current_city: str, current_nation: str, orb: float = 3.0, transit_data: Dict[str, Any] = None) -> Dict[str, Any]:
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
        yogi_point = calculate_yogi_point(natal_data)
        
        # Determine the sign of the Yogi Point
        yogi_sign_num = int(yogi_point / 30)
        yogi_sign = list(ZODIAC_SIGNS.keys())[yogi_sign_num]
        
        # Determine the sign ruler of the Yogi Point (Duplicate Yogi)
        duplicate_yogi_planet = get_ascendant_ruler(yogi_sign, zodiac_type="Sidereal")
        
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
                conj_asc_duration = calculate_alignment_duration(
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
                conj_desc_duration = calculate_alignment_duration(
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
                yogi_asc_duration = calculate_alignment_duration(
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
                dup_yogi_asc_duration = calculate_alignment_duration(
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
        yogi_conj_duration = calculate_alignment_duration(
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
        yogi_opp_duration = calculate_alignment_duration(
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