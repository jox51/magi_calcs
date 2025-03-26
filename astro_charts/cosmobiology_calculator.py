from typing import Dict, List, Optional
import logging

# Set up logger
logger = logging.getLogger(__name__)

class CosmobiologyCalculator:
    def __init__(self):
        # Define the hard aspects used in Cosmobiology
        logger.info("Initializing CosmobiologyCalculator")
        self.hard_aspects = {
            'conjunction': 0,
            'opposition': 180,
            'square': 90,
            'semi_square': 45,
            'sesquiquadrate': 135
        }
        
        # Define orbs for aspects (Cosmobiology uses tight orbs)
        self.orb = 1.0  # 1 degree orb is typical in Cosmobiology
        
        # Define midpoint categories and their activating planets
        self.midpoint_categories = {
            'success': {
                'midpoints': [
                    ('jupiter', 'venus'),
                    ('jupiter', 'pluto'),
                    ('sun', 'jupiter'),
                    ('mars', 'jupiter'),
                    ('jupiter', 'mercury'),
                    ('venus', 'saturn'),
                    ('sun', 'pluto')
                ],
                'activators': ['sun', 'venus', 'jupiter', 'mercury']
            },
            'love': {
                'midpoints': [
                    ('venus', 'jupiter'),
                    ('venus', 'mars'),
                    ('venus', 'neptune'),
                    ('venus', 'mercury'),
                    ('venus', 'sun'),
                    ('sun', 'moon'),
                    ('moon', 'venus'),
                ],
                'activators': ['venus', 'jupiter', 'neptune', 'mars', 'mercury', 'sun']
            },
            'challenging': {
                'midpoints': [
                    ('saturn', 'mars'),
                    ('saturn', 'pluto'),
                    ('sun', 'saturn'),
                    ('saturn', 'uranus'),
                    ('mars', 'pluto'),
                    ('saturn', 'mercury'),
                    ('mars', 'neptune'),
                    ('moon', 'saturn')
                ],
                'activators': ['saturn', 'pluto', 'mars', 'uranus', 'neptune', 'mercury']
            },
            'health': {
                'midpoints': [
                    ('sun', 'saturn'),
                    ('mars', 'saturn'),
                    ('mars', 'neptune'),
                    ('saturn', 'neptune'),
                    ('neptune', 'moon'),
                    ('saturn', 'moon'),
                    ('pluto', 'moon')
                ],
                'activators': ['saturn', 'neptune', 'pluto', 'mars']
            }
        }

    def calculate_aspect_angle(self, pos1: float, pos2: float) -> float:
        """Calculate the shortest angular distance between two positions"""
        diff = abs(pos1 - pos2)
        if diff > 180:
            diff = 360 - diff
        return diff

    def check_hard_aspect(self, angle: float) -> Optional[str]:
        """Check if an angle forms any of the hard aspects"""
        for aspect_name, aspect_angle in self.hard_aspects.items():
            if abs(angle - aspect_angle) <= self.orb:
                return aspect_name
        return None

    def analyze_transit_to_midpoint(self, 
                                  midpoint_pos: float, 
                                  transit_planet: str,
                                  transit_pos: float,
                                  midpoint_planets: tuple) -> Optional[Dict]:
        """Analyze if a transit planet makes a hard aspect to a midpoint"""
        angle = self.calculate_aspect_angle(midpoint_pos, transit_pos)
        aspect = self.check_hard_aspect(angle)
        
        if aspect:
            # Determine which category this midpoint activation belongs to
            category = None
            for cat_name, cat_data in self.midpoint_categories.items():
                if (midpoint_planets in cat_data['midpoints'] and 
                    transit_planet in cat_data['activators']):
                    category = cat_name
                    break
            
            if category:
                logger.info(
                    f"Cosmobiology activation found: {category} - "
                    f"Transit {transit_planet} {aspect} to "
                    f"{midpoint_planets[0]}/{midpoint_planets[1]} midpoint "
                    f"(angle: {angle:.2f}°, orb: {abs(angle - self.hard_aspects[aspect]):.2f}°)"
                )
                
                return {
                    'category': category,
                    'midpoint_planets': midpoint_planets,
                    'transit_planet': transit_planet,
                    'aspect': aspect,
                    'angle': angle,
                    'orb': abs(angle - self.hard_aspects[aspect])
                }
            else:
                logger.debug(
                    f"Hard aspect found but not a valid category activation: "
                    f"Transit {transit_planet} {aspect} to "
                    f"{midpoint_planets[0]}/{midpoint_planets[1]} midpoint"
                )
        
        return None 