from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class CinderellaLinkage:
    """Class to hold Cinderella Linkage data between two people"""
    person1_name: str
    person2_name: str
    planet1_name: str
    planet2_name: str
    aspect_name: str
    aspect_degrees: float
    orbit: float
    actual_degrees: float

class MagiLinkageCalculator:
    """Calculate Cinderella linkages between two people's charts"""
    
    def __init__(self):
        # Define valid Cinderella planet pairs
        self.cinderella_pairs = [
            ('jupiter', 'chiron'),
            ('venus', 'chiron'),
            ('neptune', 'chiron')
        ]

        # Define valid aspect angles and orbs
        self.valid_aspects = {
            'conjunction': {'angle': 0, 'orb': 3},
            'opposition': {'angle': 180, 'orb': 3},
            'trine': {'angle': 120, 'orb': 3},
            'square': {'angle': 90, 'orb': 3},
            'sextile': {'angle': 60, 'orb': 3},
            'quincunx': {'angle': 150, 'orb': 3},
            'parallel': {'angle': 0, 'orb': 1},  # For declination
            'contraparallel': {'angle': 180, 'orb': 1}  # For declination
        }

    def is_cinderella_pair(self, planet1: str, planet2: str) -> bool:
        """Check if two planets form a valid Cinderella pair"""
        planet1, planet2 = planet1.lower(), planet2.lower()
        return (planet1, planet2) in self.cinderella_pairs or (planet2, planet1) in self.cinderella_pairs

    def calculate_angle_distance(self, pos1: float, pos2: float) -> float:
        """Calculate the shortest angular distance between two positions"""
        diff = abs(pos1 - pos2)
        return 360 - diff if diff > 180 else diff

    def find_cinderella_linkages(self, person1_data: Dict, person2_data: Dict) -> List[Dict]:
        """Find all Cinderella linkages between two people's charts"""
        linkages = []
        
        # Get relevant planets for each person (accounting for 'subject' nesting)
        person1_planets = {
            'jupiter': person1_data['subject']['planets']['jupiter'],
            'venus': person1_data['subject']['planets']['venus'],
            'neptune': person1_data['subject']['planets']['neptune'],
            'chiron': person1_data['subject']['planets']['chiron']
        }
        
        person2_planets = {
            'jupiter': person2_data['subject']['planets']['jupiter'],
            'venus': person2_data['subject']['planets']['venus'],
            'neptune': person2_data['subject']['planets']['neptune'],
            'chiron': person2_data['subject']['planets']['chiron']
        }

        # Check each possible combination
        for p1_name, p1_data in person1_planets.items():
            for p2_name, p2_data in person2_planets.items():
                # Skip if not a Cinderella pair
                if not self.is_cinderella_pair(p1_name, p2_name):
                    continue

                # Calculate longitude aspects
                angle = self.calculate_angle_distance(
                    p1_data['abs_pos'], 
                    p2_data['abs_pos']
                )

                # Check each aspect
                for aspect_name, aspect_data in self.valid_aspects.items():
                    # Skip declination aspects for longitude calculations
                    if aspect_name in ['parallel', 'contraparallel']:
                        continue

                    orb = abs(angle - aspect_data['angle'])
                    if orb <= aspect_data['orb']:
                        # Create dictionary instead of CinderellaLinkage object
                        linkages.append({
                            'person1_name': person1_data['subject']['name'],
                            'person2_name': person2_data['subject']['name'],
                            'planet1_name': p1_name,
                            'planet2_name': p2_name,
                            'aspect_name': aspect_name,
                            'aspect_degrees': aspect_data['angle'],
                            'orbit': round(orb, 4),
                            'actual_degrees': round(angle, 4)
                        })

                # Check declination aspects if both planets have declination values
                dec1 = p1_data.get('declination')
                dec2 = p2_data.get('declination')
                
                if dec1 is not None and dec2 is not None:
                    dec_diff = abs(dec1 - dec2)
                    
                    # Check parallel
                    if dec_diff <= self.valid_aspects['parallel']['orb']:
                        linkages.append({
                            'person1_name': person1_data['subject']['name'],
                            'person2_name': person2_data['subject']['name'],
                            'planet1_name': p1_name,
                            'planet2_name': p2_name,
                            'aspect_name': 'parallel',
                            'aspect_degrees': 0,
                            'orbit': round(dec_diff, 4),
                            'actual_degrees': round(dec_diff, 4)
                        })
                    
                    # Check contraparallel
                    elif abs(dec_diff - 180) <= self.valid_aspects['contraparallel']['orb']:
                        linkages.append({
                            'person1_name': person1_data['subject']['name'],
                            'person2_name': person2_data['subject']['name'],
                            'planet1_name': p1_name,
                            'planet2_name': p2_name,
                            'aspect_name': 'contraparallel',
                            'aspect_degrees': 180,
                            'orbit': round(abs(dec_diff - 180), 4),
                            'actual_degrees': round(dec_diff, 4)
                        })

        return linkages
