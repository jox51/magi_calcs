from typing import Dict, List, Any
from datetime import datetime

# Dasha periods in years for each planet
DASHA_PERIODS = {
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "mercury": 17,
    "jupiter": 16,
    "venus": 20,
    "saturn": 19,
    "rahu": 18,
    "ketu": 7
}

def calculate_dasha_lord(moon_nakshatra_deg: float, birth_date: str, target_date: str) -> str:
    """Calculate the Dasha lord for a given date based on Moon's natal position
    
    Args:
        moon_nakshatra_deg: The moon's longitude in degrees (0-360)
        birth_date: Birth date in 'YYYY-MM-DD' format
        target_date: Target date for which to calculate the dasha lord
        
    Returns:
        The ruling planet for the dasha period at the target date
    """
    # Convert birth_date and target_date to datetime objects
    birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    
    # Calculate nakshatra (27 divisions)
    nakshatra = int(moon_nakshatra_deg / (360/27))
    
    # Nakshatra lords in order
    nakshatra_lords = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"] * 3
    
    # Find starting dasha lord
    start_lord = nakshatra_lords[nakshatra]
    
    # Calculate progression
    total_days = (target_dt - birth_dt).days
    total_years = total_days / 365.25
    
    # Start with the birth dasha lord
    current_index = nakshatra_lords.index(start_lord)
    years_elapsed = 0
    
    while years_elapsed < total_years:
        current_lord = nakshatra_lords[current_index]
        period_years = DASHA_PERIODS[current_lord]
        
        if years_elapsed + period_years > total_years:
            return current_lord
            
        years_elapsed += period_years
        current_index = (current_index + 1) % len(nakshatra_lords)
    
    return nakshatra_lords[current_index]

def get_available_dasha_lord(dasha_lord: str, available_planets: List[str]) -> str:
    """Get an available dasha lord from the chart data, falling back if the calculated one isn't available
    
    Args:
        dasha_lord: The originally calculated dasha lord
        available_planets: List of planets available in the chart
        
    Returns:
        An available planet to use as dasha lord
    """
    if dasha_lord in available_planets:
        return dasha_lord
    
    # Fall back to traditional visible planets if calculated dasha lord isn't available
    fallback_planets = ["jupiter", "saturn", "sun", "moon", "mars", "venus", "mercury"]
    for planet in fallback_planets:
        if planet in available_planets:
            return planet
    
    # If all else fails, return the moon (should always be available)
    return "moon"

def determine_day_night_chart(sun_pos: float, asc_pos: float, natal_data: Dict[str, Any] = None, 
                       label: str = "") -> bool:
    """
    Determine if a chart is a day or night chart
    
    A chart is considered a day chart if the Sun is above the horizon (in houses 7-12),
    and a night chart if the Sun is below the horizon (in houses 1-6).
    
    Args:
        sun_pos: The absolute position of the Sun in degrees (0-360)
        asc_pos: The absolute position of the Ascendant in degrees (0-360)
        natal_data: Optional natal chart data for alternative calculation
        label: Optional label for logging
        
    Returns:
        bool: True if day chart, False if night chart
    """
    # If sun position and ascendant position are provided directly
    if sun_pos is not None and asc_pos is not None:
        # Calculate the house of the sun relative to the ascendant
        # Each house is 30 degrees
        sun_house = int(((sun_pos - asc_pos) % 360) / 30) + 1
        
        # Houses 7-12 are above the horizon (day chart)
        is_day_chart = sun_house >= 7 and sun_house <= 12
        
        return is_day_chart
        
    # Alternative calculation using natal data if provided
    elif natal_data is not None and "subject" in natal_data:
        if "planets" in natal_data["subject"] and "sun" in natal_data["subject"]["planets"]:
            sun_data = natal_data["subject"]["planets"]["sun"]
            
            # If the house information is directly available
            if "house" in sun_data:
                sun_house_name = sun_data["house"]
                word_to_number = {
                    "First": 1, "Second": 2, "Third": 3, "Fourth": 4, "Fifth": 5, "Sixth": 6,
                    "Seventh": 7, "Eighth": 8, "Ninth": 9, "Tenth": 10, "Eleventh": 11, "Twelfth": 12
                }
                house_word = sun_house_name.split("_")[0]
                sun_house = word_to_number.get(house_word)
                
                # Houses 7-12 are above the horizon (day chart)
                is_day_chart = sun_house >= 7 and sun_house <= 12
                
                return is_day_chart
    
    # Default fallback (assume day chart if can't determine)
    return True 