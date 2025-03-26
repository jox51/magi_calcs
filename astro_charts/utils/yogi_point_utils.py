from typing import Dict, Any

# Zodiac signs mapping
ZODIAC_SIGNS = {
    "Ari": "Aries",
    "Tau": "Taurus",
    "Gem": "Gemini",
    "Can": "Cancer",
    "Leo": "Leo",
    "Vir": "Virgo",
    "Lib": "Libra",
    "Sco": "Scorpio",
    "Sag": "Sagittarius",
    "Cap": "Capricorn",
    "Aqu": "Aquarius",
    "Pis": "Pisces"
}

def calculate_yogi_point(natal_data: Dict[str, Any]) -> float:
    """Calculate the Yogi Point based on natal Sun and Moon positions"""
    sun_long = natal_data["subject"]["planets"]["sun"]["abs_pos"]
    moon_long = natal_data["subject"]["planets"]["moon"]["abs_pos"]
    return (sun_long + moon_long + 93.33333) % 360

def calculate_yogi_point_transit(transit_data: Dict[str, Any]) -> float:
    """Calculate the Yogi Point based on natal Sun and Moon positions"""
    sun_long = transit_data["transit"]["subject"]["planets"]["sun"]["abs_pos"]
    moon_long = transit_data["transit"]["subject"]["planets"]["moon"]["abs_pos"]
    return (sun_long + moon_long + 93.33333) % 360

def calculate_ava_yogi_point(yogi_point: float) -> float:
    """Calculate the Ava Yogi Point (representing challenging or unlucky times)"""
    return (yogi_point + 186.40) % 360

def get_ascendant_ruler(ascendant_sign: str, zodiac_type: str = None) -> str:
    """Determine Ascendant ruler based on sign
    
    Args:
        ascendant_sign: The sign of the ascendant
        zodiac_type: The zodiac type (Tropical or Sidereal)
        
    Returns:
        The ruling planet of the ascendant sign
    """
    # Traditional rulerships (same for both Tropical and Sidereal)
    traditional_rulers = {
        "Ari": "mars",
        "Tau": "venus",
        "Gem": "mercury",
        "Can": "moon",
        "Leo": "sun",
        "Vir": "mercury",
        "Lib": "venus",
        "Sco": "mars",  # Traditional ruler (Mars)
        "Sag": "jupiter",
        "Cap": "saturn",
        "Aqu": "saturn",  # Traditional ruler (Saturn)
        "Pis": "jupiter"
    }
    
    # Modern rulerships (more commonly used in Tropical)
    modern_rulers = {
        "Sco": "pluto",  # Modern ruler
        "Aqu": "uranus"  # Modern ruler
    }
    
    # If zodiac type is specified, use the appropriate rulership system
    if zodiac_type and zodiac_type.lower() == "sidereal":
        # In Vedic/Sidereal astrology, traditional rulerships are always used
        return traditional_rulers.get(ascendant_sign, "")
    
    # In Tropical or unspecified, use modern rulerships for the signs with modern rulers
    return modern_rulers.get(ascendant_sign, traditional_rulers.get(ascendant_sign, ""))

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