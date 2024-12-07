from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
from datetime import datetime
from astro_charts.utils.ecliptic_tilt import get_ecliptic_tilt

logger = logging.getLogger(__name__)

@dataclass
class RomanceLinkage:
    """Class to hold Romance Linkage data between two people"""
    person1_name: str
    person2_name: str
    planet1_name: str
    planet2_name: str
    aspect_name: str
    aspect_degrees: float
    orbit: float
    actual_degrees: float

class RomanceLinkageCalculator:
    """Calculate Romance linkages between two people's charts"""
    
    def __init__(self):
        # Define valid Romance planet pairs (both directions)
        self.romance_pairs = [
            ('venus', 'chiron'),
            ('chiron', 'venus'),
            ('venus', 'neptune'),
            ('neptune', 'venus'),
            ('chiron', 'neptune'),
            ('neptune', 'chiron'),
            ('jupiter', 'chiron'),
            ('chiron', 'jupiter')
        ]

        # Define valid aspect angles and orbs
        self.valid_aspects = {
            'conjunction': {'angle': 0, 'orb': 3},
            'sextile': {'angle': 60, 'orb': 3},
            'trine': {'angle': 120, 'orb': 3},
            'opposition': {'angle': 180, 'orb': 3},
            'parallel': {'angle': 0, 'orb': 3},
            'contraparallel': {'angle': 180, 'orb': 3}
        }

    def is_romance_pair(self, planet1: str, planet2: str) -> bool:
        """Check if two planets form a valid Romance pair"""
        return (planet1.lower(), planet2.lower()) in self.romance_pairs

    def calculate_angle_distance(self, pos1: float, pos2: float) -> float:
        """Calculate the shortest angular distance between two positions"""
        diff = abs(pos1 - pos2)
        return 360 - diff if diff > 180 else diff

    def calculate_ecliptic_tilt(self, date_str):
        """Get ecliptic tilt for a given date"""
        return get_ecliptic_tilt(date_str)

    def find_romance_linkages(self, person1_data: Dict, person2_data: Dict) -> List[Dict]:
        """Find all Romance linkages between two people's charts"""
        linkages = []
        PARALLEL_ORB = 2.5
        CONTRAPARALLEL_ORB = 1.5
        
        try:
            # Get birth dates
            date1 = person1_data['subject']['birth_data']['date']
            date2 = person2_data['subject']['birth_data']['date']
            
            # Calculate average ecliptic tilt between both birth dates
            tilt1 = self.calculate_ecliptic_tilt(date1)
            tilt2 = self.calculate_ecliptic_tilt(date2)
            ecliptic_tilt = (tilt1 + tilt2) / 2
            
            logger.info(f"Calculated ecliptic tilt: {ecliptic_tilt}° "
                       f"(Person 1: {tilt1}°, Person 2: {tilt2}°)")

            person1_planets = person1_data['subject']['planets']
            person2_planets = person2_data['subject']['planets']

            # Check each combination
            for p1_name in ['venus', 'chiron', 'neptune', 'jupiter']:
                for p2_name in ['venus', 'chiron', 'neptune', 'jupiter']:
                    if not self.is_romance_pair(p1_name, p2_name):
                        continue

                    p1_data = person1_planets[p1_name]
                    p2_data = person2_planets[p2_name]

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
                        contra_diff = abs(dec_sum - ecliptic_tilt)
                        if contra_diff <= CONTRAPARALLEL_ORB:
                            linkages.append({
                                'person1_name': person1_data['subject']['name'],
                                'person2_name': person2_data['subject']['name'],
                                'planet1_name': p1_name,
                                'planet2_name': p2_name,
                                'aspect_name': 'contraparallel',
                                'aspect_degrees': 180,
                                'orbit': round(contra_diff, 4),
                                'actual_degrees': round(dec_sum, 4)
                            })

            return linkages

        except Exception as e:
            logger.error(f"Error in find_romance_linkages: {str(e)}")
            raise 