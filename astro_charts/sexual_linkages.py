from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class SexualLinkage:
    """Class to hold Sexual Linkage data between two people"""
    person1_name: str
    person2_name: str
    planet1_name: str
    planet2_name: str
    aspect_name: str
    aspect_degrees: float
    orbit: float
    actual_degrees: float

class SexualLinkageCalculator:
    """Calculate Sexual linkages between two people's charts"""
    
    def __init__(self):
        # Define valid Sexual planet pairs (both directions)
        self.sexual_pairs = [
            ('venus', 'pluto'),
            ('pluto', 'venus'),
            ('mars', 'pluto'),
            ('pluto', 'mars'),
            ('venus', 'mars'),
            ('mars', 'venus')
        ]

        # Define valid aspect angles and orbs
        self.valid_aspects = {
            'conjunction': {'angle': 0, 'orb': 3},
            'opposition': {'angle': 180, 'orb': 3},
            'trine': {'angle': 120, 'orb': 3},
            'quincunx': {'angle': 150, 'orb': 3},
            'parallel': {'angle': 0, 'orb': 1.5},
            'contraparallel': {'angle': 180, 'orb': 1.5}
        }

    def is_sexual_pair(self, planet1: str, planet2: str) -> bool:
        """Check if two planets form a valid Sexual pair"""
        return (planet1.lower(), planet2.lower()) in self.sexual_pairs

    def calculate_angle_distance(self, pos1: float, pos2: float) -> float:
        """Calculate the shortest angular distance between two positions"""
        diff = abs(pos1 - pos2)
        return 360 - diff if diff > 180 else diff

    def find_sexual_linkages(self, person1_data: Dict, person2_data: Dict) -> List[Dict]:
        """Find all Sexual linkages between two people's charts"""
        linkages = []
        PARALLEL_ORB = 7  # Increased from 1.5 to match chart
        
        try:
            person1_planets = person1_data['subject']['planets']
            person2_planets = person2_data['subject']['planets']

            # Check each combination
            for p1_name in ['venus', 'mars', 'pluto']:
                for p2_name in ['venus', 'mars', 'pluto']:
                    if not self.is_sexual_pair(p1_name, p2_name):
                        continue

                    p1_data = person1_planets[p1_name]
                    p2_data = person2_planets[p2_name]

                    # Get declination values
                    dec1 = float(p1_data['declination'])
                    dec2 = float(p2_data['declination'])

                    # Check for parallel (when both N or both S)
                    if (dec1 * dec2) > 0:  # Same sign
                        dec_diff = abs(dec1 - dec2)
                        if dec_diff <= PARALLEL_ORB:
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

                    # Check for contraparallel (when one N and one S)
                    if (dec1 * dec2) < 0:  # Different signs
                        dec_sum = abs(dec1) + abs(dec2)
                        if abs(dec_sum - 46.2868) <= PARALLEL_ORB:
                            linkages.append({
                                'person1_name': person1_data['subject']['name'],
                                'person2_name': person2_data['subject']['name'],
                                'planet1_name': p1_name,
                                'planet2_name': p2_name,
                                'aspect_name': 'contraparallel',
                                'aspect_degrees': 180,
                                'orbit': round(abs(dec_sum - 46.2868), 4),
                                'actual_degrees': round(dec_sum, 4)
                            })

            return linkages

        except Exception as e:
            logger.error(f"Error in find_sexual_linkages: {str(e)}")
            raise