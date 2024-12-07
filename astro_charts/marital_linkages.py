from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime
import ephem
import logging
from astro_charts.utils.ecliptic_tilt import get_ecliptic_tilt

logger = logging.getLogger(__name__)

@dataclass
class MaritalLinkage:
    """Class to hold Marital Linkage data between two people"""
    person1_name: str
    person2_name: str
    planet1_name: str
    planet2_name: str
    aspect_name: str
    aspect_degrees: float
    orbit: float
    actual_degrees: float

class MaritalLinkageCalculator:
    """Calculate Marital linkages (Venus-Chiron) between two people's charts"""
    
    def __init__(self):
        # Define valid Marital planet pairs (both directions)
        self.marital_pairs = [
            ('venus', 'chiron'),
            ('chiron', 'venus')
        ]

    def calculate_ecliptic_tilt(self, date_str: str) -> float:
        """Get ecliptic tilt for a given date"""
        return get_ecliptic_tilt(date_str)

    def find_marital_linkages(self, person1_data: Dict, person2_data: Dict) -> List[Dict]:
        """Find all Marital linkages between two people's charts"""
        linkages = []
        PARALLEL_ORB = 5.0
        CONTRAPARALLEL_ORB = 1.5
        LONGITUDE_ORB = 3.0
        
        # Define valid longitude-based aspects
        VALID_ASPECTS = {
            'conjunction': {'angle': 0, 'orb': LONGITUDE_ORB},
            'trine': {'angle': 120, 'orb': LONGITUDE_ORB},
            'opposition': {'angle': 180, 'orb': LONGITUDE_ORB},
            'quincunx': {'angle': 150, 'orb': LONGITUDE_ORB}
        }
        
        try:
            # Get birth dates
            date1 = person1_data['subject']['birth_data']['date']
            date2 = person2_data['subject']['birth_data']['date']
            
            # Calculate average ecliptic tilt between both birth dates
            tilt1 = self.calculate_ecliptic_tilt(date1)
            tilt2 = self.calculate_ecliptic_tilt(date2)
            ecliptic_tilt = (tilt1 + tilt2) / 2
            
            logger.info(f"Calculated ecliptic tilt for marital linkages: {ecliptic_tilt}° "
                       f"(Person 1: {tilt1}°, Person 2: {tilt2}°)")

            person1_planets = person1_data['subject']['planets']
            person2_planets = person2_data['subject']['planets']

            # Check Venus-Chiron combinations
            for p1_name in ['venus', 'chiron']:
                for p2_name in ['venus', 'chiron']:
                    # Skip if same planet or not a valid marital pair
                    if p1_name == p2_name or (p1_name, p2_name) not in self.marital_pairs:
                        continue

                    p1_data = person1_planets[p1_name]
                    p2_data = person2_planets[p2_name]

                    # Get positions and declinations
                    pos1 = float(p1_data['abs_pos'])
                    pos2 = float(p2_data['abs_pos'])
                    dec1 = float(p1_data['declination'])
                    dec2 = float(p2_data['declination'])

                    # Check longitude-based aspects
                    angle_diff = abs(pos1 - pos2)
                    if angle_diff > 180:
                        angle_diff = 360 - angle_diff

                    # Check for all valid aspects
                    for aspect_name, aspect_data in VALID_ASPECTS.items():
                        if abs(angle_diff - aspect_data['angle']) <= aspect_data['orb']:
                            linkages.append({
                                'person1_name': person1_data['subject']['name'],
                                'person2_name': person2_data['subject']['name'],
                                'planet1_name': p1_name,
                                'planet2_name': p2_name,
                                'aspect_name': aspect_name,
                                'aspect_degrees': aspect_data['angle'],
                                'orbit': round(abs(angle_diff - aspect_data['angle']), 4),
                                'actual_degrees': round(angle_diff, 4)
                            })

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
            logger.error(f"Error in find_marital_linkages: {str(e)}")
            raise 