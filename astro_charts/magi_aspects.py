from dataclasses import dataclass
from typing import List, Dict
import math

@dataclass
class MagiAspect:
    """Class to hold Magi Aspect data"""
    p1_name: str
    p2_name: str
    aspect_name: str
    aspect_degrees: float
    orbit: float
    actual_degrees: float
    is_harmonious: bool
    is_cinderella: bool = False
    is_sexual: bool = False
    is_romance: bool = False

class MagiAspectCalculator:
    """Calculate aspects according to Magi Astrology rules"""
    
    def __init__(self):
        # Define Magi aspect angles and their allowed orbs
        self.magi_aspects = {
            'conjunction': {'degrees': 0, 'orb': 3, 'harmonious': True},
            'opposition': {'degrees': 180, 'orb': 3, 'harmonious': False},
            'trine': {'degrees': 120, 'orb': 3, 'harmonious': True},
            'square': {'degrees': 90, 'orb': 3, 'harmonious': False},
            # 'sextile': {'degrees': 60, 'orb': 3, 'harmonious': True},
            'quincunx': {'degrees': 150, 'orb': 3, 'harmonious': False},
            'parallel': {'degrees': 0, 'orb': 1, 'harmonious': True},  # For declination
            'contraparallel': {'degrees': 180, 'orb': 1, 'harmonious': False}  # For declination
        }

        # Define Cinderella aspect combinations
        self.cinderella_pairs = [
            ('jupiter', 'chiron'),
            ('venus', 'chiron'),
            ('neptune', 'chiron')
        ]

        # Define Sexual aspect combinations
        self.sexual_pairs = [
            ('venus', 'mars'),
            ('venus', 'pluto'),
            ('mars', 'pluto')
        ]

        # Define Romance aspect combinations
        self.romance_pairs = [
            ('venus', 'chiron'),
            ('venus', 'neptune'),
            ('chiron', 'neptune')
        ]

    def calculate_angle_distance(self, pos1: float, pos2: float) -> float:
        """Calculate the shortest angular distance between two positions"""
        diff = abs(pos1 - pos2)
        if diff > 180:
            diff = 360 - diff
        return diff

    def is_cinderella_aspect(self, p1_name: str, p2_name: str) -> bool:
        """
        Determine if an aspect between two planets is a Cinderella aspect.
        According to Magi Astrology, Cinderella aspects occur when:
        - Jupiter makes a magical angle to natal Chiron
        - Venus makes a magical angle to natal Chiron
        - Neptune makes a magical angle to natal Chiron
        (or vice versa in all cases)
        """
        # Convert planet names to lowercase for comparison
        p1_name = p1_name.lower()
        p2_name = p2_name.lower()
        
        # Check if this pair of planets forms a Cinderella aspect
        for pair in self.cinderella_pairs:
            if (p1_name in pair and p2_name in pair):
                return True
        return False

    def is_sexual_aspect(self, p1_name: str, p2_name: str) -> bool:
        """
        Determine if an aspect between two planets is a Sexual aspect.
        Sexual aspects occur between:
        - Venus and Mars
        - Venus and Pluto
        - Mars and Pluto
        (or vice versa in all cases)
        """
        # Convert planet names to lowercase for comparison
        p1_name = p1_name.lower()
        p2_name = p2_name.lower()
        
        # Check if this pair of planets forms a Sexual aspect
        for pair in self.sexual_pairs:
            if (p1_name in pair and p2_name in pair):
                return True
        return False

    def is_romance_aspect(self, p1_name: str, p2_name: str) -> bool:
        """
        Determine if an aspect between two planets is a Romance aspect.
        Romance aspects occur between:
        - Venus and Chiron
        - Venus and Neptune
        - Chiron and Neptune
        (or vice versa in all cases)
        """
        # Convert planet names to lowercase for comparison
        p1_name = p1_name.lower()
        p2_name = p2_name.lower()
        
        # Check if this pair of planets forms a Romance aspect
        for pair in self.romance_pairs:
            if (p1_name in pair and p2_name in pair):
                return True
        return False

    def get_aspect(self, pos1: float, pos2: float, p1_name: str, p2_name: str, orb: float = 3) -> Dict:
        """Determine if two positions form an aspect"""
        angle = self.calculate_angle_distance(pos1, pos2)
        
        for aspect_name, aspect_data in self.magi_aspects.items():
            # Skip declination aspects
            if aspect_name in ['parallel', 'contraparallel']:
                continue
                
            aspect_angle = aspect_data['degrees']
            allowed_orb = aspect_data['orb']
            
            if abs(angle - aspect_angle) <= allowed_orb:
                return {
                    'name': aspect_name,
                    'degrees': aspect_angle,
                    'orbit': abs(angle - aspect_angle),
                    'harmonious': aspect_data['harmonious'],
                    'is_cinderella': self.is_cinderella_aspect(p1_name, p2_name),
                    'is_sexual': self.is_sexual_aspect(p1_name, p2_name),
                    'is_romance': self.is_romance_aspect(p1_name, p2_name)
                }
        return None

    def get_declination_aspect(self, dec1: float, dec2: float, p1_name: str, p2_name: str) -> Dict:
        """Determine if two declinations form an aspect"""
        diff = abs(dec1 - dec2)
        
        if diff <= self.magi_aspects['parallel']['orb']:
            return {
                'name': 'parallel',
                'degrees': 0,
                'orbit': diff,
                'harmonious': True,
                'is_cinderella': self.is_cinderella_aspect(p1_name, p2_name),
                'is_sexual': self.is_sexual_aspect(p1_name, p2_name),
                'is_romance': self.is_romance_aspect(p1_name, p2_name)
            }
        elif abs(diff - 180) <= self.magi_aspects['contraparallel']['orb']:
            return {
                'name': 'contraparallel',
                'degrees': 180,
                'orbit': abs(diff - 180),
                'harmonious': False,
                'is_cinderella': self.is_cinderella_aspect(p1_name, p2_name),
                'is_sexual': self.is_sexual_aspect(p1_name, p2_name),
                'is_romance': self.is_romance_aspect(p1_name, p2_name)
            }
        return None

    def calculate_all_aspects(self, planets_data: Dict) -> List[MagiAspect]:
        """Calculate all aspects between planets"""
        aspects = []
        planet_names = list(planets_data.keys())
        
        for i in range(len(planet_names)):
            for j in range(i + 1, len(planet_names)):
                p1_name = planet_names[i]
                p2_name = planet_names[j]
                p1_data = planets_data[p1_name]
                p2_data = planets_data[p2_name]
                
                # Check longitude aspects
                aspect = self.get_aspect(
                    p1_data['abs_pos'], 
                    p2_data['abs_pos'],
                    p1_name,
                    p2_name
                )
                
                if aspect:
                    aspects.append(MagiAspect(
                        p1_name=p1_name,
                        p2_name=p2_name,
                        aspect_name=aspect['name'],
                        aspect_degrees=aspect['degrees'],
                        orbit=aspect['orbit'],
                        actual_degrees=self.calculate_angle_distance(
                            p1_data['abs_pos'], 
                            p2_data['abs_pos']
                        ),
                        is_harmonious=aspect['harmonious'],
                        is_cinderella=aspect['is_cinderella'],
                        is_sexual=aspect['is_sexual'],
                        is_romance=aspect['is_romance']
                    ))
                
                # Check declination aspects
                if 'declination' in p1_data and 'declination' in p2_data:
                    dec_aspect = self.get_declination_aspect(
                        p1_data['declination'],
                        p2_data['declination'],
                        p1_name,
                        p2_name
                    )
                    
                    if dec_aspect:
                        aspects.append(MagiAspect(
                            p1_name=p1_name,
                            p2_name=p2_name,
                            aspect_name=dec_aspect['name'],
                            aspect_degrees=dec_aspect['degrees'],
                            orbit=dec_aspect['orbit'],
                            actual_degrees=abs(p1_data['declination'] - p2_data['declination']),
                            is_harmonious=dec_aspect['harmonious'],
                            is_cinderella=dec_aspect['is_cinderella'],
                            is_sexual=dec_aspect['is_sexual'],
                            is_romance=dec_aspect['is_romance']
                        ))
        
        return aspects

class SuperAspectCalculator:
    """Calculate Super aspects between planets"""
    
    def __init__(self):
        # Define valid Super aspect planet pairs
        self.super_pairs = [
            ('jupiter', 'pluto'),
            ('jupiter', 'uranus'),
            ('jupiter', 'chiron')
        ]

        # Define valid magical angles and orbs for Super aspects
        self.valid_aspects = {
            'conjunction': {'angle': 0, 'orb': 3},
            'opposition': {'angle': 180, 'orb': 3},
            'trine': {'angle': 120, 'orb': 3},
            'square': {'angle': 90, 'orb': 3},
            # 'sextile': {'angle': 60, 'orb': 3},
            'quincunx': {'angle': 150, 'orb': 3},
            'parallel': {'angle': 0, 'orb': 1},  # For declination
            'contraparallel': {'angle': 180, 'orb': 1}  # For declination
        }

    def is_super_pair(self, planet1: str, planet2: str) -> bool:
        """Check if two planets form a valid Super aspect pair"""
        planet1, planet2 = planet1.lower(), planet2.lower()
        return (planet1, planet2) in self.super_pairs or (planet2, planet1) in self.super_pairs

    def calculate_angle_distance(self, pos1: float, pos2: float) -> float:
        """Calculate the shortest angular distance between two positions"""
        diff = abs(pos1 - pos2)
        return min(diff, 360 - diff)

    def find_super_aspects(self, chart_data: Dict) -> List[Dict]:
        """Find all Super aspects in a chart"""
        super_aspects = []
        
        # Get relevant planets
        planets = chart_data['subject']['planets']
        
        # Check each possible combination
        for p1_name, p1_data in planets.items():
            for p2_name, p2_data in planets.items():
                if p1_name >= p2_name:  # Skip duplicate combinations
                    continue
                    
                # Skip if not a Super pair
                if not self.is_super_pair(p1_name, p2_name):
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
                        super_aspects.append({
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
                        super_aspects.append({
                            'planet1_name': p1_name,
                            'planet2_name': p2_name,
                            'aspect_name': 'parallel',
                            'aspect_degrees': 0,
                            'orbit': round(dec_diff, 4),
                            'actual_degrees': round(dec_diff, 4)
                        })
                    
                    # Check contraparallel
                    elif abs(dec_diff - 180) <= self.valid_aspects['contraparallel']['orb']:
                        super_aspects.append({
                            'planet1_name': p1_name,
                            'planet2_name': p2_name,
                            'aspect_name': 'contraparallel',
                            'aspect_degrees': 180,
                            'orbit': round(abs(dec_diff - 180), 4),
                            'actual_degrees': round(dec_diff, 4)
                        })

        return super_aspects
