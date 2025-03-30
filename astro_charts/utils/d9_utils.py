from typing import Dict, Any
from .yogi_point_utils import ZODIAC_SIGNS

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
    