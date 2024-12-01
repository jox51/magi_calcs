from typing import Dict, List

class MagiSynastryCalculator:
    """Calculate various synastry aspects according to Magi Astrology"""
    
    def __init__(self):
        self.saturn_clash_aspects = {
            'square': 90,      # 90-degree angle
            'quincunx': 150,   # 150-degree angle
            'opposition': 180   # 180-degree angle
        }
        self.personal_planets = [
            'sun', 'moon', 'mercury', 'venus', 'mars', 
            'jupiter', 'chiron', 'uranus', 'neptune', 'pluto'
        ]
        self.saturn_orb = 3.0  # degrees
        
    def check_saturn_clashes(self, person1_data: Dict, person2_data: Dict) -> List[Dict]:
        """Check for Saturn clashes between two charts"""
        clashes = []
        
        # Get Saturn positions for both people
        saturn1 = person1_data['subject']['planets']['saturn']
        saturn2 = person2_data['subject']['planets']['saturn']
        
        # Check Person 1's Saturn against Person 2's planets
        for planet_name, planet_data in person2_data['subject']['planets'].items():
            if planet_name in self.personal_planets:
                angle = self.calculate_angle_distance(
                    saturn1['abs_pos'],
                    planet_data['abs_pos']
                )
                
                # Check each aspect
                for aspect_name, aspect_data in self.saturn_clash_aspects.items():
                    orb = abs(angle - aspect_data)
                    if orb <= self.saturn_orb:
                        clashes.append({
                            'saturn_person': person1_data['subject']['name'],
                            'planet_person': person2_data['subject']['name'],
                            'planet2_name': planet_name,
                            'aspect_name': aspect_name,
                            'aspect_degrees': aspect_data,
                            'orbit': round(orb, 4),
                            'actual_degrees': round(angle, 4)
                        })
        
        # Check Person 2's Saturn against Person 1's planets
        for planet_name, planet_data in person1_data['subject']['planets'].items():
            if planet_name in self.personal_planets:
                angle = self.calculate_angle_distance(
                    saturn2['abs_pos'],
                    planet_data['abs_pos']
                )
                
                # Check each aspect
                for aspect_name, aspect_data in self.saturn_clash_aspects.items():
                    orb = abs(angle - aspect_data)
                    if orb <= self.saturn_orb:
                        clashes.append({
                            'saturn_person': person2_data['subject']['name'],
                            'planet_person': person1_data['subject']['name'],
                            'planet2_name': planet_name,
                            'aspect_name': aspect_name,
                            'aspect_degrees': aspect_data,
                            'orbit': round(orb, 4),
                            'actual_degrees': round(angle, 4)
                        })
        
        return clashes
    
    def calculate_angle_distance(self, pos1: float, pos2: float) -> float:
        """Calculate the shortest angular distance between two positions"""
        diff = abs(pos1 - pos2)
        return min(diff, 360 - diff)
