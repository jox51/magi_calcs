from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from ..chart_creator import ChartCreator
import json

logger = logging.getLogger(__name__)

class AltMarriageDateFinder:
    def __init__(self, transit_loop_function):
        self.transit_loop_function = transit_loop_function
        # Define Cinderella planets
        self.cinderella_planets = ["chiron", "neptune", "venus"]
        # Define turbulent combinations
        self.turbulent_combinations = {
            "saturn": ["sun", "chiron", "jupiter"],  # Saturn making turbulent aspects
            "chiron": ["venus", "neptune"],  # Chiron turbulent aspects
            "venus": ["chiron", "neptune"],  # Venus turbulent aspects
            "neptune": ["chiron", "venus"]   # Neptune turbulent aspects
        }
        
    async def find_matching_dates(self, synastry_data: Dict, from_date: str, 
                                to_date: str, transit_hour: int, transit_minute: int,
                                user_id: str, job_id: str) -> Dict:
        try:
            logger.info(f"Synastry data: {synastry_data}")
            # Extract both persons' data
            person1 = synastry_data["person1"]["subject"]
            person2 = synastry_data["person2"]["subject"]
            
            # logger.info(f"Person 1 Synastry: {person1}")
            # logger.info(f"Person 2 Synastry: {person2}")
            
            # Get all relevant planets for filtering
            filter_planets = list(set(
                self.cinderella_planets + 
                list(self.turbulent_combinations.keys()) + 
                [p for sublist in self.turbulent_combinations.values() for p in sublist]
            ))
            
            logger.info(f"Filter planets: {filter_planets}")
            # Process transits for both people
            person1_transits = await self._get_transits(
                person1, from_date, to_date, transit_hour, transit_minute,
                user_id, job_id, filter_planets
            )
            logger.info(f"Person 1 transits: {person1_transits}")
            
            
            person2_transits = await self._get_transits(
                person2, from_date, to_date, transit_hour, transit_minute,
                user_id, job_id, filter_planets
            )
            logger.info(f"Person 2 transits: {person2_transits}")
            
            # Analyze transits for both people
            results = self._analyze_transits(person1_transits, person2_transits)
            return {"matching_dates": results}
            
        except Exception as e:
            logger.error(f"Error in alt marriage date finder: {str(e)}")
            logger.error(f"Error occurred at line: {e.__traceback__.tb_lineno}")
            return {"matching_dates": []}

    async def _get_transits(self, person: Dict, from_date: str, to_date: str,
                          transit_hour: int, transit_minute: int,
                          user_id: str, job_id: str,
                          filter_planets: List[str]) -> Dict:
        """Get transits using the specialized marriage transit loop"""
        try:
            # Extract birth data
            birth_data = person.get("birth_data", {})
            if not birth_data:
                raise ValueError(f"No birth data found for {person.get('name', 'unknown person')}")
            
            # Create chart creator instance
            chart_creator = ChartCreator(
                name=person["name"],
                year=int(birth_data["date"].split("-")[0]),
                month=int(birth_data["date"].split("-")[1]),
                day=int(birth_data["date"].split("-")[2]),
                hour=int(birth_data["time"].split(":")[0]),
                minute=int(birth_data["time"].split(":")[1]),
                city=birth_data["location"].split(",")[0].strip(),
                nation=birth_data["location"].split(",")[1].strip()
            )
            
            # Initialize results dictionary
            results = {}
            
            # Convert date strings to datetime objects
            start_date = datetime.strptime(from_date, "%Y-%m-%d")
            end_date = datetime.strptime(to_date, "%Y-%m-%d")
            current_date = start_date
            
            while current_date <= end_date:
                try:
                    # Format date string
                    date_key = current_date.strftime("%Y-%m-%d")
                    logger.debug(f"Processing date_key: {date_key}")
                    
                    # Split date_key into components
                    year, month, day = map(int, date_key.split('-'))
                    
                    # Create transit time using the split components
                    transit_time = datetime(
                        year=year,
                        month=month,
                        day=day,
                        hour=transit_hour if transit_hour is not None else 0,
                        minute=transit_minute if transit_minute is not None else 0
                    )
                    
                    logger.info(f"Creating transit chart for {person['name']} on {transit_time}")
                    transit_data = await chart_creator.create_transit_chart(transit_year=transit_time.year,
                transit_month=transit_time.month,
                transit_day=transit_time.day,
                transit_hour=transit_time.hour,
                transit_minute=transit_time.minute)
                    
                    logger.info(f"Transit data: {transit_data}")
                    
                    # Debug the incoming data type
                    logger.debug(f"Transit data type: {type(transit_data)}")
                    
                    # Parse the JSON string into a dictionary if it's a string
                    if isinstance(transit_data, str):
                        try:
                            transit_data = json.loads(transit_data)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse transit data JSON: {e}")
                            continue
                    
                    cinderella_aspects = []
                    turbulent_transits = []
                    
                    # Now we can safely use dictionary operations
                    transit_aspects = transit_data.get('transit', {}).get('transit_super_aspects', [])
                    natal_aspects = transit_data.get('natal_super_aspects', [])
                    
                    # Process all aspects
                    for aspect in transit_aspects + natal_aspects:
                        if self._is_cinderella_aspect(aspect):
                            cinderella_aspects.append(self._format_aspect(aspect))
                        if self._is_turbulent_aspect(aspect):
                            turbulent_transits.append(self._format_aspect(aspect))
                    
                    # Get all Cinderella aspects
                    cinderella_transits = []
                    if isinstance(transit_data.get('transit'), dict):
                        cinderella_transits.extend(transit_data['transit'].get('cinderella_aspects', []))
                    cinderella_transits.extend(transit_data.get('cinderella_aspects', []))
                    
                    # Store the transit data in results
                    results[date_key] = {
                        'date': date_key,
                        'time': f"{transit_hour}:{transit_minute}",
                        'natal_planets': transit_data.get('natal', {}).get('planets', {}),
                        'transit_planets': transit_data.get('transit', {}).get('subject', {}).get('planets', {}),
                        'cinderella_transits': cinderella_transits,
                        'turbulent_transits': transit_data.get('turbulent_transits', [])
                    }
                    
                    logger.debug(f"Successfully processed results for {date_key}")
                    
                except Exception as e:
                    logger.error(f"Error processing date {current_date} for {person['name']}: {str(e)}")
                    logger.error(f"Transit data: {transit_data if 'transit_data' in locals() else 'No transit chart created'}")
                    
                current_date += timedelta(days=1)
            
            logger.info(f"Completed transit calculations for {person['name']}")
            logger.info(f"Final results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error getting transits for {person.get('name', 'unknown person')}: {str(e)}")
            logger.error(f"Person data structure: {person}")
            return {}

    def _analyze_transits(self, person1_transits: Dict, person2_transits: Dict) -> List[Dict]:
        analyzed_dates = []
        
        # Look at all dates where we have data for both people
        for date in person1_transits.keys():
            # print("Person 1 transits: ", person1_transits)
            # print("Person 2 transits: ", person2_transits)
            if date in person2_transits:
                logger.debug(f"Analyzing date: {date}")
                logger.debug(f"Person 1 raw data: {person1_transits[date]}")
                logger.debug(f"Person 2 raw data: {person2_transits[date]}")
                
                date_analysis = {
                    'date': date,
                    'person1': {
                        'cinderella_transits': person1_transits[date].get('cinderella_transits', []),
                        'turbulent_transits': person1_transits[date].get('turbulent_transits', [])
                    },
                    'person2': {
                        'cinderella_transits': person2_transits[date].get('cinderella_transits', []),
                        'turbulent_transits': person2_transits[date].get('turbulent_transits', [])
                    }
                }
                
                logger.debug(f"Person 1 Cinderella aspects: {date_analysis['person1']['cinderella_transits']}")
                logger.debug(f"Person 1 Turbulent transits: {date_analysis['person1']['turbulent_transits']}")
                logger.debug(f"Person 2 Cinderella aspects: {date_analysis['person2']['cinderella_transits']}")
                logger.debug(f"Person 2 Turbulent transits: {date_analysis['person2']['turbulent_transits']}")
                
                # Only include dates with relevant transits
                if (date_analysis['person1']['cinderella_transits'] or 
                    date_analysis['person1']['turbulent_transits'] or
                    date_analysis['person2']['cinderella_transits'] or 
                    date_analysis['person2']['turbulent_transits']):
                    analyzed_dates.append(date_analysis)
                else:
                    logger.debug(f"No relevant transits found for date: {date}")
        
        logger.info(f"Found {len(analyzed_dates)} dates with relevant transits")
        return analyzed_dates

    def _is_cinderella_aspect(self, aspect: Dict) -> bool:
        """Check if aspect is a Cinderella transit"""
        planet1 = aspect.get('planet1_name', '').lower()
        planet2 = aspect.get('planet2_name', '').lower()
        aspect_type = aspect.get('aspect_type', '').lower()
        
        logger.debug(f"Checking Cinderella aspect: {planet1} {aspect_type} {planet2}")
        
        # Check if both planets are Cinderella planets
        is_cinderella = (planet1 in self.cinderella_planets and 
                         planet2 in self.cinderella_planets and 
                         aspect_type in ['trine', 'sextile', 'conjunction'])
        
        if is_cinderella:
            logger.debug(f"Found Cinderella aspect: {planet1} {aspect_type} {planet2}")
        
        return is_cinderella

    def _is_turbulent_aspect(self, aspect: Dict) -> bool:
        """Check if aspect is a Turbulent transit"""
        planet1 = aspect.get('planet1_name', '').lower()
        planet2 = aspect.get('planet2_name', '').lower()
        aspect_type = aspect.get('aspect_type', '').lower()
        
        logger.debug(f"Checking Turbulent aspect: {planet1} {aspect_type} {planet2}")
        
        # Check for square aspects (90 degrees)
        if aspect_type != 'square':
            return False
            
        # Check turbulent combinations
        for trigger_planet, affected_planets in self.turbulent_combinations.items():
            if ((planet1 == trigger_planet and planet2 in affected_planets) or
                (planet2 == trigger_planet and planet1 in affected_planets)):
                logger.debug(f"Found Turbulent aspect: {planet1} {aspect_type} {planet2}")
                return True
        
        return False

    def _format_aspect(self, aspect: Dict) -> Dict:
        """Format aspect data for output"""
        return {
            'planets': f"{aspect.get('planet1_name', '')} - {aspect.get('planet2_name', '')}",
            'aspect_type': aspect.get('aspect_type', ''),
            'orbit': aspect.get('orbit', 0)
        }
