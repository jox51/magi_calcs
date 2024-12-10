from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from ..models.request_models import TransitLoopRequest
import logging
import json

logger = logging.getLogger(__name__)

class MarriageDateFinder:
    def __init__(self, transit_loop_function):
        self.transit_loop_function = transit_loop_function

    async def find_matching_dates(self, synastry_data: Dict, from_date: str, 
                                to_date: str, transit_hour: int, transit_minute: int,
                                user_id: str, job_id: str) -> Dict:
        try:
            # Extract person 1 data
            person1 = synastry_data["person1"]["subject"]
            logger.debug(f"Processing transits for {person1['name']}")
            
            # Include all relevant planets for comprehensive analysis
            marriage_planets = ["jupiter", "venus", "chiron", "sun", "moon", "saturn"]
            
            person1_transits = await self.transit_loop_function(
                name=person1["name"],
                year=int(person1["birth_data"]["date"].split("-")[0]),
                month=int(person1["birth_data"]["date"].split("-")[1]),
                day=int(person1["birth_data"]["date"].split("-")[2]),
                hour=int(person1["birth_data"]["time"].split(":")[0]),
                minute=int(person1["birth_data"]["time"].split(":")[1]),
                city=person1["birth_data"]["location"].split(",")[0],
                nation=person1["birth_data"]["location"].split(",")[1].strip(),
                from_date=from_date,
                to_date=to_date,
                transit_hour=transit_hour,
                transit_minute=transit_minute,
                user_id=user_id,
                job_id=job_id,
                filter_planets=marriage_planets,
                aspects_only=False,
                filter_orb=2.0
            )
            
            # Extract person 2 data
            person2 = synastry_data["person2"]["subject"]
            logger.debug(f"Processing transits for {person2['name']}")
            
            person2_transits = await self.transit_loop_function(
                name=person2["name"],
                year=int(person2["birth_data"]["date"].split("-")[0]),
                month=int(person2["birth_data"]["date"].split("-")[1]),
                day=int(person2["birth_data"]["date"].split("-")[2]),
                hour=int(person2["birth_data"]["time"].split(":")[0]),
                minute=int(person2["birth_data"]["time"].split(":")[1]),
                city=person2["birth_data"]["location"].split(",")[0],
                nation=person2["birth_data"]["location"].split(",")[1].strip(),
                from_date=from_date,
                to_date=to_date,
                transit_hour=transit_hour,
                transit_minute=transit_minute,
                user_id=user_id,
                job_id=job_id,
                filter_planets=marriage_planets,
                aspects_only=False,
                filter_orb=2.0
            )

            matching_dates = self._find_cinderella_matches(person1_transits, person2_transits)
            return {"matching_dates": matching_dates}
                
        except Exception as e:
            logger.error(f"Error in find_matching_dates: {str(e)}")
            logger.error(f"Error occurred at line: {e.__traceback__.tb_lineno}")
            return {"matching_dates": []}

    def _find_cinderella_matches(self, person1_transits: Dict, person2_transits: Dict) -> List[Dict]:
        matching_dates = []
        
        for date in person1_transits.keys():
            if date in person2_transits:
                # Debug logging
                logger.debug(f"\nDate: {date}")
                logger.debug(f"P1 transit keys: {person1_transits[date].keys()}")
                logger.debug(f"P2 transit keys: {person2_transits[date].keys()}")
                
                # Get the transit data
                p1_transit = person1_transits[date].get('transit', {})
                p2_transit = person2_transits[date].get('transit', {})
                
                logger.debug(f"P1 transit object keys: {p1_transit.keys()}")
                logger.debug(f"P2 transit object keys: {p2_transit.keys()}")
                
                # Get cinderella and turbulent aspects
                p1_cinderella = p1_transit.get('cinderella_aspects', [])
                p1_turbulent = p1_transit.get('turbulent_transits', [])
                
                p2_cinderella = p2_transit.get('cinderella_aspects', [])
                p2_turbulent = p2_transit.get('turbulent_transits', [])
                
                logger.debug(f"P1 cinderella aspects: {p1_cinderella}")
                logger.debug(f"P2 cinderella aspects: {p2_cinderella}")
                
                date_info = {
                    'date': date,
                    'score': 0,
                    'person1_transits': {
                        'favorable': p1_cinderella,  # Include all cinderella aspects as favorable
                        'challenging': [t for t in p1_turbulent if t.get('transit_type', '').lower() in ['nuclear', 'heartbreak', 'separation']],
                        'transformative': [t for t in p1_turbulent if t.get('transit_type', '').lower() in ['karmic', 'destiny', 'spiritual']]
                    },
                    'person2_transits': {
                        'favorable': p2_cinderella,  # Include all cinderella aspects as favorable
                        'challenging': [t for t in p2_turbulent if t.get('transit_type', '').lower() in ['nuclear', 'heartbreak', 'separation']],
                        'transformative': [t for t in p2_turbulent if t.get('transit_type', '').lower() in ['karmic', 'destiny', 'spiritual']]
                    }
                }
                
                # Calculate score
                for person_transits in [date_info['person1_transits'], date_info['person2_transits']]:
                    date_info['score'] += sum(5 for _ in person_transits['favorable'])  # +5 for each favorable
                    date_info['score'] -= sum(t.get('impact_score', 5) for t in person_transits['challenging'])
                    date_info['score'] += sum(3 for _ in person_transits['transformative'])  # +3 for each transformative
                
                matching_dates.append(date_info)
                
        # Sort dates by score (highest first)
        matching_dates.sort(key=lambda x: x['score'], reverse=True)
        return matching_dates

    def _calculate_date_score(self, p1_transits: List[Dict], p2_transits: List[Dict]) -> float:
        """Calculate a score for the date based on transit types and impact scores"""
        score = 0
        
        # Define impact multipliers for different transit types
        impact_multipliers = {
            'cinderella': 2.0,
            'romance': 1.5,
            'marriage': 2.0,
            'soulmate': 2.0,
            'heartbreak': -1.5,
            'nuclear': -1.0,
            'separation': -1.5,
            'karmic': 0.5,
            'destiny': 1.0,
            'spiritual': 0.5
        }
        
        # Process all transits
        for transit in p1_transits + p2_transits:
            transit_type = transit.get('transit_type', '').lower()
            impact_score = transit.get('impact_score', 5)  # Default impact score of 5
            multiplier = impact_multipliers.get(transit_type, 0)
            
            # Add to score
            score += impact_score * multiplier
            
            # Bonus for tight orbs (closer aspects are stronger)
            orbit = abs(transit.get('orbit', 0))
            if orbit < 1.0:
                score += 2
            elif orbit < 2.0:
                score += 1
        
        return round(score, 2)

    def _check_cinderella_planets(self, planets: Dict) -> List[Dict]:
        """Check for Jupiter and Chiron positions and aspects"""
        cinderella_aspects = []
        
        jupiter = planets.get('jupiter', {})
        chiron = planets.get('chiron', {})
        
        if jupiter and chiron:
            # Add positions to aspects list
            cinderella_aspects.append({
                'planet1': 'jupiter',
                'planet2': 'chiron',
                'position1': jupiter.get('abs_pos'),
                'position2': chiron.get('abs_pos')
            })
        
        return cinderella_aspects

    def _has_cinderella_transit(self, aspects: List[Dict]) -> Optional[List[Dict]]:
        cinderella_aspects = []
        logger.debug(f"Checking aspects for Cinderella transits: {aspects}")
        
        if not aspects:
            logger.debug("No aspects provided")
            return None
        
        if not isinstance(aspects, list):
            logger.debug(f"Aspects is not a list, it's a {type(aspects)}")
            return None
        
        for aspect in aspects:
            logger.debug(f"Checking aspect: {aspect}")
            if self._is_cinderella_aspect(aspect):
                logger.info(f"Found Cinderella aspect: {aspect}")
                cinderella_aspects.append(aspect)
        
        logger.debug(f"Found {len(cinderella_aspects)} Cinderella aspects")
        return cinderella_aspects if cinderella_aspects else None

    def _is_cinderella_aspect(self, aspect: Dict) -> bool:
        cinderella_planets = ["jupiter", "chiron"]
        try:
            planet1 = aspect.get("planet1_name", "").lower()
            planet2 = aspect.get("planet2_name", "").lower()
            
            logger.debug(f"Checking planets {planet1} and {planet2} for Cinderella aspect")
            
            is_cinderella = (
                planet1 in cinderella_planets or 
                planet2 in cinderella_planets
            )
            
            if is_cinderella:
                logger.debug(f"Found Cinderella planet in aspect: {aspect}")
            
            return is_cinderella
        except Exception as e:
            logger.error(f"Error checking Cinderella aspect: {str(e)}")
            return False 

  
        """
        Specialized transit loop for finding marriage-favorable dates.
        Only looks for aspects relevant to marriage potential.
        """
        transits = {}
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            
            # Calculate transit chart for the current date
            transit_data = self.calculator.calculate_transit_chart(
                person,
                date_str,
                "14:30"  # Using afternoon time as default
            )
            
            # Only include marriage-relevant aspects
            if (transit_data.get('transit', {}).get('cinderella_aspects') or 
                transit_data.get('transit', {}).get('turbulent_transits')):
                transits[date_str] = transit_data
            
            current += timedelta(days=1)
        
        return transits 