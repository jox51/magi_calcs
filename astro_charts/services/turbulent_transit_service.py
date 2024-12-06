from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class TurbulentTransit:
    """Class to hold Turbulent Transit data"""
    natal_planet: str
    transit_planet: str
    aspect_name: str
    aspect_degrees: float
    orbit: float
    actual_degrees: float
    transit_type: str  # 'heartbreak', 'nuclear', 'saturn'
    impact_score: int  # 1-10 scale of severity

class TurbulentTransitService:
    """Service for analyzing turbulent transits in astrological charts"""
    
    def __init__(self):
        # Define valid turbulent aspects and their orbs
        self.valid_aspects = {
            'square': {'angle': 90, 'orb': 3},
            'opposition': {'angle': 180, 'orb': 3},
            'quincunx': {'angle': 150, 'orb': 3},
            'contraparallel': {'angle': 180, 'orb': 1.5}
        }

        # Define specific transit types and their planet combinations
        self.heartbreak_pairs = [
            ('saturn', 'chiron'),
            ('chiron', 'saturn'),
            ('venus', 'chiron'),  # Added Venus-Chiron pair
            ('chiron', 'venus')   # Added Chiron-Venus pair
        ]
        
        self.nuclear_pairs = [
            ('saturn', 'jupiter'),
            ('jupiter', 'saturn'),
            ('jupiter', 'pluto'),  # Added Jupiter-Pluto pair
            ('pluto', 'jupiter')   # Added Pluto-Jupiter pair
        ]

        # Define Saturn-sensitive planets
        self.saturn_sensitive_planets = [
            'sun', 'moon', 'mercury', 'venus', 
            'mars', 'chiron'
        ]

    def calculate_angle_distance(self, pos1: float, pos2: float) -> float:
        """Calculate the shortest angular distance between two positions"""
        diff = abs(pos1 - pos2)
        return min(diff, 360 - diff)

    def calculate_impact_score(self, transit_type: str, aspect_name: str) -> int:
        """Calculate impact score (1-10) based on transit type and aspect"""
        base_scores = {
            'heartbreak': 8,
            'nuclear': 9,
            'saturn': 7
        }
        
        aspect_multipliers = {
            'opposition': 1.2,
            'square': 1.0,
            'quincunx': 0.9,
            'contraparallel': 0.8
        }
        
        base_score = base_scores.get(transit_type, 5)
        multiplier = aspect_multipliers.get(aspect_name, 1.0)
        
        return min(round(base_score * multiplier), 10)

    def analyze_turbulent_transits(self, natal_data: Dict, transit_data: Dict) -> List[Dict]:
        """Analyze chart data for turbulent transits"""
        turbulent_transits = []
        
        try:
            natal_planets = natal_data['subject']['planets']
            transit_planets = transit_data['planets']

            # Check each combination for turbulent aspects
            for transit_planet, t_data in transit_planets.items():
                for natal_planet, n_data in natal_planets.items():
                    
                    # Determine transit type
                    transit_type = None
                    if (transit_planet.lower(), natal_planet.lower()) in self.heartbreak_pairs:
                        transit_type = 'heartbreak'
                    elif (transit_planet.lower(), natal_planet.lower()) in self.nuclear_pairs:
                        transit_type = 'nuclear'
                    elif transit_planet.lower() == 'saturn' and natal_planet.lower() in self.saturn_sensitive_planets:
                        transit_type = 'saturn'
                    
                    if not transit_type:
                        continue

                    # Check each aspect
                    for aspect_name, aspect_data in self.valid_aspects.items():
                        angle_diff = self.calculate_angle_distance(
                            float(t_data['abs_pos']), 
                            float(n_data['abs_pos'])
                        )
                        
                        if abs(angle_diff - aspect_data['angle']) <= aspect_data['orb']:
                            impact_score = self.calculate_impact_score(transit_type, aspect_name)
                            
                            turbulent_transits.append({
                                'natal_planet': natal_planet,
                                'transit_planet': transit_planet,
                                'aspect_name': aspect_name,
                                'aspect_degrees': aspect_data['angle'],
                                'orbit': round(abs(angle_diff - aspect_data['angle']), 4),
                                'actual_degrees': round(angle_diff, 4),
                                'transit_type': transit_type,
                                'impact_score': impact_score
                            })

            return sorted(turbulent_transits, key=lambda x: x['impact_score'], reverse=True)

        except Exception as e:
            logger.error(f"Error analyzing turbulent transits: {str(e)}")
            raise