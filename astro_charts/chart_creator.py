from kerykeion import AstrologicalSubject, KerykeionChartSVG, Report
import os
import shutil
import logging
import json
from datetime import datetime, timedelta
import pytz
import math
from datetime import date
import requests
from .magi_aspects import MagiAspectCalculator, SuperAspectCalculator
from .services.geo_service import GeoService
from timezonefinder import TimezoneFinder
from .magi_synastry import MagiSynastryCalculator
from .magi_linkages import MagiLinkageCalculator
from .services.cinderella_analyzer import CinderellaAnalyzer
from .sexual_linkages import SexualLinkageCalculator
from .services.nasa_horizons_service import NASAHorizonsService
from .services.turbulent_transit_service import TurbulentTransitService
from .romance_linkages import RomanceLinkageCalculator
from .marital_linkages import MaritalLinkageCalculator
from .transit_calculator import calculate_transit_data
from .services.synastry_score_calculator import SynastryScoreCalculator
from typing import Dict, List, Optional
from .cosmobiology_calculator import CosmobiologyCalculator



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartCreator:
    # Common timezone mappings
    TIMEZONE_MAPPINGS = {
        # Europe
        'IT': 'Europe/Rome',
        'UK': 'Europe/London',
        'ES': 'Europe/Madrid',
        'FR': 'Europe/Paris',
        'DE': 'Europe/Berlin',
        'PT': 'Europe/Lisbon',
        'IE': 'Europe/Dublin',
        'NL': 'Europe/Amsterdam',
        'BE': 'Europe/Brussels',
        'CH': 'Europe/Zurich',
        'AT': 'Europe/Vienna',
        'SE': 'Europe/Stockholm',
        'NO': 'Europe/Oslo',
        'DK': 'Europe/Copenhagen',
        'FI': 'Europe/Helsinki',
        'GR': 'Europe/Athens',
        
        # North America
        'US': 'America/New_York',  # Default to ET, but could be overridden
        'CA': 'America/Toronto',
        'MX': 'America/Mexico_City',
        
        # US Specific Timezones
        'US-ET': 'America/New_York',      # Eastern
        'US-CT': 'America/Chicago',       # Central
        'US-MT': 'America/Denver',        # Mountain
        'US-PT': 'America/Los_Angeles',   # Pacific
        'US-AK': 'America/Anchorage',     # Alaska
        'US-HI': 'Pacific/Honolulu',      # Hawaii
        
        # South America
        'BR': 'America/Sao_Paulo',
        'AR': 'America/Argentina/Buenos_Aires',
        'CL': 'America/Santiago',
        'CO': 'America/Bogota',
        'PE': 'America/Lima',
        
        # Asia
        'JP': 'Asia/Tokyo',
        'CN': 'Asia/Shanghai',
        'HK': 'Asia/Hong_Kong',
        'SG': 'Asia/Singapore',
        'IN': 'Asia/Kolkata',
        'KR': 'Asia/Seoul',
        'TH': 'Asia/Bangkok',
        'PH': 'Asia/Manila',
        
        # Oceania
        'AU': 'Australia/Sydney',         # Default to Sydney
        'AU-SYD': 'Australia/Sydney',     # Sydney specific
        'AU-MEL': 'Australia/Melbourne',  # Melbourne specific
        'AU-BRI': 'Australia/Brisbane',   # Brisbane specific
        'AU-PER': 'Australia/Perth',      # Perth specific
        'NZ': 'Pacific/Auckland',
        
        # Middle East
        'IL': 'Asia/Jerusalem',
        'AE': 'Asia/Dubai',
        'SA': 'Asia/Riyadh',
        'TR': 'Europe/Istanbul',
        
        # Africa
        'ZA': 'Africa/Johannesburg',
        'EG': 'Africa/Cairo',
        'MA': 'Africa/Casablanca',
        'NG': 'Africa/Lagos',
        'KE': 'Africa/Nairobi'
    }

    def __init__(self, name, year, month, day, hour, minute, city, nation, zodiac_type=None, sidereal_mode=None):
        # Initialize GeoService and get coordinates
        geonames_username = os.getenv('GEONAMES_USERNAME')
        self.geo_service = GeoService(geonames_username)
        
        # Get coordinates
        coordinates = self.geo_service.get_coordinates(city, nation)
        if not coordinates:
            raise ValueError(f"Could not find coordinates for {city}, {nation}")
            
        self.latitude, self.longitude = coordinates
        logger.info(f"Retrieved coordinates: lat={self.latitude}, lng={self.longitude}")

        # Get timezone from coordinates
        tf = TimezoneFinder()
        self.timezone_str = tf.timezone_at(lat=self.latitude, lng=self.longitude)
        if not self.timezone_str:
            raise ValueError(f"Could not determine timezone for coordinates: {self.latitude}, {self.longitude}")
        
        logger.info(f"Determined timezone: {self.timezone_str}")

        # Initialize natal subject with all required data
        logger.info(f"Creating natal subject with lat={self.latitude}, lng={self.longitude}, tz={self.timezone_str}")
        
        # Set up parameters for AstrologicalSubject
        subject_params = {
            "name": name,
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "city": city,
            "nation": nation,
            "lat": self.latitude,
            "lng": self.longitude,
            "tz_str": self.timezone_str,
            "online": False  # Prevent online lookups
        }
        
        # Add optional zodiac_type and sidereal_mode if provided
        if zodiac_type:
            subject_params["zodiac_type"] = zodiac_type
            logger.info(f"Using zodiac_type: {zodiac_type}")
            
            # If sidereal zodiac is specified, add sidereal_mode if provided
            if zodiac_type == "Sidereal" and sidereal_mode:
                subject_params["sidereal_mode"] = sidereal_mode
                logger.info(f"Using sidereal_mode: {sidereal_mode}")
                
        self.subject = AstrologicalSubject(**subject_params)
        logger.info("Natal subject created successfully")

        self.horizons_url = "https://ssd.jpl.nasa.gov/api/horizons.api"
        
        # Planet mappings for Horizons API
        self.planet_mappings = {
            'sun': '10',
            'moon': '301',
            'mercury': '199',
            'venus': '299',
            'mars': '499',
            'jupiter': '599',
            'saturn': '699',
            'uranus': '799',
            'neptune': '899',
            'pluto': '999',
            'chiron': '2060'
        }

        self.cinderella_analyzer = CinderellaAnalyzer()
        self.sexual_linkage_calculator = SexualLinkageCalculator()
        self.nasa_service = NASAHorizonsService()
        self.turbulent_transit_service = TurbulentTransitService()

        self.name = name
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.city = city
        self.nation = nation
        self.natal_subject = None
        self.transit_subject = None

    def get_natal_planets(self) -> Dict:
        """Return the natal planets data"""
        if self.natal_subject and hasattr(self.natal_subject, 'planets'):
            return self.natal_subject.planets
        return {}

    def get_transit_planets(self) -> Dict:
        """Return the transit planets data"""
        if self.transit_subject and hasattr(self.transit_subject, 'planets'):
            return self.transit_subject.planets
        return {}

    def get_cinderella_aspects(self) -> List[Dict]:
        """Return Cinderella aspects for current transit"""
        if hasattr(self, '_cinderella_aspects'):
            return self._cinderella_aspects
        return []

    def get_turbulent_transits(self) -> List[Dict]:
        """Return turbulent transits for current transit"""
        if hasattr(self, '_turbulent_transits'):
            return self._turbulent_transits
        return []

    def create_natal_chart(self):
        """Create and save a natal chart"""
        try:
            # Generate custom filename from name
            name_safe = self.subject.name.replace(" ", "_")
            svg_filename = f"{name_safe}_natal.svg"
            chart_path = os.path.join('charts', svg_filename)
            
            # Create charts directory if it doesn't exist
            os.makedirs('charts', exist_ok=True)
            logger.info(f"Creating natal chart for {self.subject.name}")
            
            # Generate natal chart only
            natal_chart = KerykeionChartSVG(self.subject, chart_type="Natal")
            natal_chart.makeSVG()
            
            # Move the generated chart
            expected_filename = f"{self.subject.name} - Natal Chart.svg"
            source_path = os.path.join(os.path.expanduser('~'), expected_filename)
            print("Source path: ", source_path)
            
            if os.path.exists(source_path):
                shutil.move(source_path, chart_path)
                logger.info(f"Natal chart moved from {source_path} to {os.path.abspath(chart_path)}")
            
            # Get chart data using existing method but only include natal data
            chart_data = json.loads(self.get_chart_data_as_json())
            
            # Create simplified natal-only data structure
            final_data = {
                "natal": chart_data["subject"],
                "super_aspects": chart_data.get("super_aspects", []),
                "chart_path": chart_path
            }
            
            return final_data, source_path
            
        except Exception as e:
            logger.error(f"Error creating natal chart: {str(e)}")
            raise

    async def create_transit_chart(self, transit_year=None, transit_month=None, 
                             transit_day=None, transit_hour=None, transit_minute=None,
                             zodiac_type=None, sidereal_mode=None):
        """Create a transit chart for a specific date (or current date if not specified)"""
        try:
            # Use provided transit date or current date
            if all([transit_year, transit_month, transit_day]):
                transit_time = datetime(
                    year=transit_year,
                    month=transit_month,
                    day=transit_day,
                    hour=transit_hour if transit_hour is not None else 0,
                    minute=transit_minute if transit_minute is not None else 0
                )
            else:
                transit_time = datetime.now()
            
            logger.info(f"Creating transit chart for date: {transit_time}")
            
            # Create transit subject with explicit coordinates and timezone
            transit_params = {
                "name": "Transit",
                "year": transit_time.year,
                "month": transit_time.month,
                "day": transit_time.day,
                "hour": transit_time.hour,
                "minute": transit_time.minute,
                "city": self.subject.city,
                "nation": self.subject.nation,
                "lat": self.latitude,
                "lng": self.longitude,
                "tz_str": self.timezone_str,
                "online": False
            }
            
            # Use provided zodiac settings if specified, otherwise use the natal chart settings
            if zodiac_type:
                transit_params["zodiac_type"] = zodiac_type
                logger.info(f"Using provided zodiac_type for transit: {zodiac_type}")
                
                # If sidereal zodiac is specified, also use the provided sidereal_mode
                if zodiac_type == "Sidereal" and sidereal_mode:
                    transit_params["sidereal_mode"] = sidereal_mode
                    logger.info(f"Using provided sidereal_mode for transit: {sidereal_mode}")
            # Fall back to natal chart settings if available
            elif hasattr(self.subject, 'zodiac_type'):
                transit_params["zodiac_type"] = self.subject.zodiac_type
                logger.info(f"Using zodiac_type from natal chart for transit: {self.subject.zodiac_type}")
                
                # If sidereal zodiac is specified, also use the same sidereal_mode
                if self.subject.zodiac_type == "Sidereal" and hasattr(self.subject, 'sidereal_mode'):
                    transit_params["sidereal_mode"] = self.subject.sidereal_mode
                    logger.info(f"Using sidereal_mode from natal chart for transit: {self.subject.sidereal_mode}")
            
            self.transit_subject = AstrologicalSubject(**transit_params)
            logger.info("`Transit subject` created successfully")

            # Generate a filename with the subject's name
            name_safe = self.subject.name.replace(" ", "_")
            svg_filename = f"{name_safe}_transit_chart.svg"
            chart_path = os.path.join('charts', svg_filename)
            os.makedirs('charts', exist_ok=True)
            
            transit_chart = KerykeionChartSVG(
                self.subject,
                "Transit",
                self.transit_subject
            )
            transit_chart.makeSVG()

            # Move the generated chart
            expected_filename = f"{self.subject.name} - Transit Chart.svg"
            source_path = os.path.join(os.path.expanduser('~'), expected_filename)
            
            if os.path.exists(source_path):
                shutil.move(source_path, chart_path)
                logger.info(f"Transit chart moved from {source_path} to {os.path.abspath(chart_path)}")

            return self._get_transit_data_as_json(chart_path)

        except Exception as e:
            logger.error(f"Error creating transit chart: {str(e)}")
            raise

    def _get_transit_data_as_json(self, chart_path):
        """Get transit chart data as JSON"""
        try:
            def get_planet_details(planet_obj):
            
                # Get planet name and position
                planet_name = planet_obj.name.lower()
                abs_pos = planet_obj.abs_pos
                
                # Calculate declination
                declination = self.get_declination(
                    planet_name=planet_name,
                    date_str=f"{self.transit_subject.year}-{self.transit_subject.month:02d}-{self.transit_subject.day:02d}",
                    abs_pos=abs_pos,
                    longitude=self.longitude,
                    latitude=self.latitude
                )
                logger.info(f"Got declination for {planet_name}: {declination}")

                return {
                    "name": planet_obj.name,
                    "sign": planet_obj.sign,
                    "position": round(planet_obj.position, 4),
                    "abs_pos": round(abs_pos, 4),
                    "house": planet_obj.house,
                    "retrograde": planet_obj.retrograde,
                    "declination": round(declination, 4) if declination is not None else None
                }

            # Create natal data first
            natal_data = {
                "subject": {
                    "name": self.subject.name,
                    "birth_data": {
                        "date": f"{self.subject.year}-{self.subject.month}-{self.subject.day}",
                        "time": f"{self.subject.hour}:{self.subject.minute}",
                        "location": f"{self.subject.city}, {self.subject.nation}",
                        "longitude": round(self.longitude, 4),
                        "latitude": round(self.latitude, 4)
                    },
                    "planets": {
                        planet: get_planet_details(getattr(self.subject, planet))
                        for planet in ["sun", "moon", "mercury", "venus", "mars", 
                                    "jupiter", "saturn", "uranus", "neptune", 
                                    "pluto", "chiron"]
                    }
                }
            }

            # Create transit data with same structure
            transit_data = {
                "subject": {
                    "name": "Transit",
                    "birth_data": {
                        "date": f"{self.transit_subject.year}-{self.transit_subject.month:02d}-{self.transit_subject.day:02d}",
                        "time": f"{self.transit_subject.hour}:{self.transit_subject.minute:02d}",
                        "location": f"{self.transit_subject.city}, {self.transit_subject.nation}",
                        "longitude": round(self.longitude, 4),
                        "latitude": round(self.latitude, 4)
                    },
                    "planets": {
                        planet: get_planet_details(getattr(self.transit_subject, planet))
                        for planet in ["sun", "moon", "mercury", "venus", "mars", 
                                    "jupiter", "saturn", "uranus", "neptune", 
                                    "pluto", "chiron"]
                    },
                    # Add house information to transit data 
                    "houses": {
                        "ascendant": {
                            "sign": self.transit_subject.first_house["sign"],
                            "position": self.transit_subject.first_house["position"],
                            "abs_pos": self.transit_subject.first_house["abs_pos"],
                            "house_num": 1
                        },
                        "midheaven": {
                            "sign": self.transit_subject.tenth_house["sign"],
                            "position": self.transit_subject.tenth_house["position"],
                            "abs_pos": self.transit_subject.tenth_house["abs_pos"],
                            "house_num": 10
                        }
                    }
                }
            }

            # Calculate aspects after both natal and transit data are created
            super_calc = SuperAspectCalculator()
            super_aspects = super_calc.find_super_aspects(natal_data)
            transit_super_aspects = super_calc.find_super_aspects(transit_data)

            # Calculate Cinderella aspects
            linkage_calc = MagiLinkageCalculator()
            cinderella_aspects = linkage_calc.find_cinderella_linkages(natal_data, transit_data)
            
            # Calculate Golden Transits
            golden_transits = linkage_calc.find_golden_transits(natal_data, transit_data)

            # Add aspects to transit data
            transit_data["transit_super_aspects"] = transit_super_aspects
            transit_data["cinderella_aspects"] = cinderella_aspects
            transit_data["cinderella_transits"] = cinderella_aspects
            transit_data["aspects"] = []  # Keep empty array for consistency
            transit_data["turbulent_transits"] = []  # Will be filled later
            transit_data["golden_transits"] = golden_transits  # Add golden transits

            # Add turbulent transit analysis
            turbulent_transits = self.turbulent_transit_service.analyze_turbulent_transits(
                natal_data=natal_data,
                transit_data=transit_data["subject"]
            )

            # Create final chart data
            chart_data = {
                "natal": natal_data["subject"],
                "transit": transit_data,
                "natal_super_aspects": super_aspects,
                "chart_path": chart_path,
                "turbulent_transits": turbulent_transits,
                "golden_transits": golden_transits,  # Add golden transits here too
                "cinderella_transits": cinderella_aspects
            }

            logger.info(f"Found {len(turbulent_transits)} turbulent transits")
            logger.info(f"Found {len(golden_transits)} golden transits")
            logger.info(f"Found {len(cinderella_aspects)} cinderella transits")
            return json.dumps(chart_data, indent=2)

        except Exception as e:
            logger.error(f"Error converting transit data to JSON: {str(e)}")
            raise

    def calculate_obliquity(self, year, month, day):
        """
        Calculate the mean obliquity of the ecliptic using IAU 1980 formula
        
        Args:
            year (int): Year
            month (int): Month
            day (int): Day
            
        Returns:
            float: Obliquity in degrees
        """
        try:
            # Calculate Julian Date
            if month <= 2:
                year -= 1
                month += 12
            
            a = int(year / 100)
            b = 2 - a + int(a / 4)
            
            jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
            
            # Calculate T (Julian centuries since J2000.0)
            T = (jd - 2451545.0) / 36525.0
            
            # IAU 1980 formula for mean obliquity
            # ε = 23° 26' 21.448" - 46.8150"T - 0.00059"T² + 0.001813"T³
            epsilon = (
                23.0 + 
                26.0/60.0 + 
                21.448/3600.0 - 
                (46.8150/3600.0) * T - 
                (0.00059/3600.0) * T**2 + 
                (0.001813/3600.0) * T**3
            )
            
            logger.info(f"Calculated obliquity for date {year}-{month}-{day}: {epsilon}°")
            return epsilon
            
        except Exception as e:
            logger.error(f"Error calculating obliquity: {str(e)}")
            return 23.4367  # Fallback to mean value if calculation fails

    def calculate_declination(self, longitude, latitude=0):
        """
        Calculate declination using astronomical formula
        
        Args:
            longitude (float): Ecliptic longitude in degrees
            latitude (float): Ecliptic latitude in degrees (optional)
            
        Returns:
            float: Declination in degrees
        """
        try:
            # Use existing obliquity calculation
            year = self.subject.year
            month = self.subject.month
            day = self.subject.day
            obliquity = self.calculate_obliquity(year, month, day)
            
            # Convert to radians
            lon_rad = math.radians(longitude)
            lat_rad = math.radians(latitude)
            obliquity_rad = math.radians(obliquity)
            
            # Calculate declination using the full spherical astronomy formula
            sin_dec = (
                math.sin(lat_rad) * math.cos(obliquity_rad) +
                math.cos(lat_rad) * math.sin(obliquity_rad) * math.sin(lon_rad)
            )
            
            # Convert to degrees and round
            declination = math.degrees(math.asin(sin_dec))
            result = round(declination, 4)
            
            logger.info(f"Calculated declination for lon:{longitude}, lat:{latitude}, obliquity:{obliquity}°: {result}°")
            return result
                
        except Exception as e:
            logger.error(f"Error calculating declination: {str(e)}")
            return None

    def get_declination(self, planet_name, date_str, abs_pos, longitude=None, latitude=None):
        """Get declination for a planet"""
        try:
            # Use provided coordinates or fall back to subject's coordinates
            lng = longitude if longitude is not None else self.subject.lng
            lat = latitude if latitude is not None else self.subject.lat
            
            print(f"Getting declination for {planet_name} on {date_str}")
            declination = self.nasa_service.get_declination(
                planet_name,
                date_str,
                lng,
                lat
            )
            
            # Only fall back to calculation if NASA API fails
            if declination is None:
                logger.warning(f"NASA API failed for {planet_name}, using calculation fallback")
                return self.calculate_declination(abs_pos)
                
            return declination
                
        except Exception as e:
            logger.error(f"Error in get_declination for {planet_name}: {str(e)}")
            return None

    def get_chart_data_as_json(self):
        """Get chart data as JSON including aspects"""
        try:
            def get_planet_details(planet_obj):
                planet_name = planet_obj["name"].lower()
                abs_pos = planet_obj["abs_pos"]
                logger.info(f"Processing planet {planet_name} at position {abs_pos}")
                
                date_str = f"{self.subject.year}-{self.subject.month:02d}-{self.subject.day:02d}"
            
                declination = self.get_declination(
                planet_name,
                date_str,
                abs_pos,
                longitude=self.subject.lng,
                latitude=self.subject.lat
            )
                logger.info(f"Got declination for {planet_name}: {declination}")
                
                return {
                    "name": planet_obj["name"],
                    "quality": planet_obj["quality"],
                    "element": planet_obj["element"],
                    "sign": planet_obj["sign"],
                    "sign_num": planet_obj["sign_num"],
                    "position": planet_obj["position"],
                    "abs_pos": abs_pos,
                    "emoji": planet_obj["emoji"],
                    "point_type": "Planet",
                    "house": planet_obj["house"],
                    "retrograde": planet_obj["retrograde"],
                    "declination": declination
                }

            # Get base chart data
            chart_data = {
                "subject": {
                    "name": self.subject.name,
                    "birth_data": {
                        "date": f"{self.subject.year}-{self.subject.month}-{self.subject.day}",
                        "time": f"{self.subject.hour}:{self.subject.minute}",
                        "location": f"{self.subject.city}, {self.subject.nation}",
                        "longitude": round(self.longitude, 4),
                        "latitude": round(self.latitude, 4)
                    },
                    "planets": {
                        "sun": get_planet_details(self.subject.sun),
                        "moon": get_planet_details(self.subject.moon),
                        "mercury": get_planet_details(self.subject.mercury),
                        "venus": get_planet_details(self.subject.venus),
                        "mars": get_planet_details(self.subject.mars),
                        "jupiter": get_planet_details(self.subject.jupiter),
                        "saturn": get_planet_details(self.subject.saturn),
                        "uranus": get_planet_details(self.subject.uranus),
                        "neptune": get_planet_details(self.subject.neptune),
                        "pluto": get_planet_details(self.subject.pluto),
                        "chiron": get_planet_details(self.subject.chiron)
                    },
                    "houses": {
                        "ascendant": {
                            "sign": self.subject.first_house["sign"],
                            "position": self.subject.first_house["position"],
                            "abs_pos": self.subject.first_house["abs_pos"],
                            "house_num": 1
                        },
                        "midheaven": {
                            "sign": self.subject.tenth_house["sign"],
                            "position": self.subject.tenth_house["position"],
                            "abs_pos": self.subject.tenth_house["abs_pos"],
                            "house_num": 10
                        }
                    }
                }
            }

            # Use MagiAspectCalculator to calculate aspects
            aspect_calculator = MagiAspectCalculator()
            aspects = aspect_calculator.calculate_all_aspects(chart_data["subject"]["planets"])

            # Add aspects to chart data
            chart_data["subject"]["aspects"] = [
                {
                    'p1_name': aspect.p1_name,
                    'p2_name': aspect.p2_name,
                    'aspect_name': aspect.aspect_name,
                    'aspect_degrees': aspect.aspect_degrees,
                    'orbit': round(aspect.orbit, 4),
                    'actual_degrees': round(aspect.actual_degrees, 4),
                    'is_harmonious': aspect.is_harmonious,
                    'is_cinderella': aspect.is_cinderella,
                    'is_sexual': aspect.is_sexual,
                    'is_romance': aspect.is_romance
                }
                for aspect in aspects
            ]

            # Extract Cinderella aspects into separate array
            cinderella_aspects = [
                {
                    'planet1_name': aspect.p1_name,
                    'planet2_name': aspect.p2_name,
                    'aspect_name': aspect.aspect_name,
                    'aspect_degrees': aspect.aspect_degrees,
                    'orbit': round(aspect.orbit, 4),
                    'actual_degrees': round(aspect.actual_degrees, 4)
                }
                for aspect in aspects if aspect.is_cinderella
            ]

            # Extract Sexual aspects into separate array
            sexual_aspects = [
                {
                    'planet1_name': aspect.p1_name,
                    'planet2_name': aspect.p2_name,
                    'aspect_name': aspect.aspect_name,
                    'aspect_degrees': aspect.aspect_degrees,
                    'orbit': round(aspect.orbit, 4),
                    'actual_degrees': round(aspect.actual_degrees, 4)
                }
                for aspect in aspects if aspect.is_sexual
            ]

            # Extract Romance aspects into separate array
            romance_aspects = [
                {
                    'planet1_name': aspect.p1_name,
                    'planet2_name': aspect.p2_name,
                    'aspect_name': aspect.aspect_name,
                    'aspect_degrees': aspect.aspect_degrees,
                    'orbit': round(aspect.orbit, 4),
                    'actual_degrees': round(aspect.actual_degrees, 4)
                }
                for aspect in aspects if aspect.is_romance
            ]

            # Calculate Super aspects
            super_calc = SuperAspectCalculator()
            super_aspects = super_calc.find_super_aspects(chart_data)

            # Add all aspect types to the final data
            chart_data["super_aspects"] = super_aspects
            chart_data["cinderella_aspects"] = cinderella_aspects
            chart_data["sexual_aspects"] = sexual_aspects
            chart_data["romance_aspects"] = romance_aspects

            logger.info("Chart data successfully converted to JSON")
            return json.dumps(chart_data, indent=2)

        except Exception as e:
            logger.error(f"Error converting chart data to JSON: {str(e)}")
            raise

    def create_synastry_chart(self, name2, year2, month2, day2, hour2, minute2, city2, nation2):
        """Create a synastry chart between two people"""
        try:
            # Get coordinates for second person
            coordinates2 = self.geo_service.get_coordinates(city2, nation2)
            if not coordinates2:
                raise ValueError(f"Could not find coordinates for {city2}, {nation2}")
            
            lat2, lng2 = coordinates2
            
            # Get timezone for second person
            tf = TimezoneFinder()
            tz_str2 = tf.timezone_at(lat=lat2, lng=lng2)
            if not tz_str2:
                raise ValueError(f"Could not determine timezone for coordinates: {lat2}, {lng2}")

            # Create second subject
            logger.info(f"Creating second subject with lat={lat2}, lng={lng2}, tz={tz_str2}")
            
            # Set up parameters for second subject
            subject2_params = {
                "name": name2,
                "year": year2,
                "month": month2,
                "day": day2,
                "hour": hour2,
                "minute": minute2,
                "city": city2,
                "nation": nation2,
                "lat": lat2,
                "lng": lng2,
                "tz_str": tz_str2,
                "online": False
            }
            
            # Use the same zodiac settings as the natal chart if they were specified
            if hasattr(self.subject, 'zodiac_type'):
                subject2_params["zodiac_type"] = self.subject.zodiac_type
                logger.info(f"Using zodiac_type for second subject: {self.subject.zodiac_type}")
                
                # If sidereal zodiac is specified, also use the same sidereal_mode
                if self.subject.zodiac_type == "Sidereal" and hasattr(self.subject, 'sidereal_mode'):
                    subject2_params["sidereal_mode"] = self.subject.sidereal_mode
                    logger.info(f"Using sidereal_mode for second subject: {self.subject.sidereal_mode}")
            
            self.subject2 = AstrologicalSubject(**subject2_params)
            logger.info("Second subject created successfully")

            # Generate custom filename from both names
            name1_safe = self.subject.name.replace(" ", "_")
            name2_safe = name2.replace(" ", "_")
            svg_filename = f"{name1_safe}_{name2_safe}_synastry.svg"
            chart_path = os.path.join('charts', svg_filename)
            os.makedirs('charts', exist_ok=True)
            
            synastry_chart = KerykeionChartSVG(
                self.subject,
                "Synastry",
                self.subject2
            )
            synastry_chart.makeSVG()

            # Move the generated chart to our charts directory
            expected_filename = f"{self.subject.name} - Synastry Chart.svg"
            source_path = os.path.join(os.path.expanduser('~'), expected_filename)
            
            if os.path.exists(source_path):
                shutil.move(source_path, chart_path)
                logger.info(f"Synastry chart moved from {source_path} to {os.path.abspath(chart_path)}")

            # Generate JSON data
            return self._get_synastry_data_as_json(chart_path)

        except Exception as e:
            logger.error(f"Error creating synastry chart: {str(e)}")
            raise

    def _get_synastry_data_as_json(self, chart_path):
        """Get synastry chart data as JSON"""
        try:
            def get_planet_details(planet_obj, birth_date, longitude=None, latitude=None):
                planet_name = planet_obj.name.lower()
                abs_pos = planet_obj.abs_pos
                
                # Pass abs_pos along with other parameters
                declination = self.get_declination(
                    planet_name=planet_name,
                    date_str=birth_date,
                    abs_pos=abs_pos,  # Add this parameter
                    longitude=longitude,
                    latitude=latitude
                )
                # logger.info(f"Got declination for {planet_name} on {birth_date}: {declination}")

                return {
                    "name": planet_obj.name,
                    "sign": planet_obj.sign,
                    "position": round(planet_obj.position, 4),
                    "abs_pos": round(planet_obj.abs_pos, 4),
                    "house": planet_obj.house,
                    "retrograde": planet_obj.retrograde,
                    "declination": round(declination, 4) if declination is not None else None
                }

            # Format dates for both people
            date1 = f"{self.subject.year}-{self.subject.month:02d}-{self.subject.day:02d}"
            date2 = f"{self.subject2.year}-{self.subject2.month:02d}-{self.subject2.day:02d}"

            # Create data structure with correct dates
            person1_data = {
                "subject": {
                    "name": self.subject.name,
                    "birth_data": {
                        "date": date1,
                        "time": f"{self.subject.hour}:{self.subject.minute:02d}",
                        "location": f"{self.subject.city}, {self.subject.nation}",
                        "longitude": round(self.longitude, 4),
                        "latitude": round(self.latitude, 4)
                    },
                    "planets": {
                        planet: get_planet_details(getattr(self.subject, planet), date1)
                        for planet in ["sun", "moon", "mercury", "venus", "mars", 
                                     "jupiter", "saturn", "uranus", "neptune", 
                                     "pluto", "chiron"]
                    }
                }
            }

            person2_data = {
                "subject": {
                    "name": self.subject2.name,
                    "birth_data": {
                        "date": date2,
                        "time": f"{self.subject2.hour}:{self.subject2.minute:02d}",
                        "location": f"{self.subject2.city}, {self.subject2.nation}",
                        "longitude": round(self.longitude, 4),
                        "latitude": round(self.latitude, 4)
                    },
                    "planets": {
                        planet: get_planet_details(getattr(self.subject2, planet), date2)
                        for planet in ["sun", "moon", "mercury", "venus", "mars", 
                                     "jupiter", "saturn", "uranus", "neptune", 
                                     "pluto", "chiron"]
                    }
                }
            }

            # Calculate Saturn clashes
            magi_calc = MagiSynastryCalculator()
            saturn_clashes = magi_calc.check_saturn_clashes(person1_data, person2_data)

            # Calculate Cinderella linkages
            linkage_calc = MagiLinkageCalculator()
            sexual_calc = SexualLinkageCalculator()
            cinderella_linkages = linkage_calc.find_cinderella_linkages(person1_data, person2_data)

            # Calculate Super aspects for both charts
            super_calc = SuperAspectCalculator()
            person1_super_aspects = super_calc.find_super_aspects(person1_data)
            person2_super_aspects = super_calc.find_super_aspects(person2_data)
            sexual_linkages = sexual_calc.find_sexual_linkages(person1_data, person2_data)

            # Calculate Romance linkages
            romance_calc = RomanceLinkageCalculator()
            romance_linkages = romance_calc.find_romance_linkages(person1_data, person2_data)
            
            # Calculate Marital linkages
            marital_calc = MaritalLinkageCalculator()
            marital_linkages = marital_calc.find_marital_linkages(person1_data, person2_data)
            
            # Calculate synastry score
            score_calculator = SynastryScoreCalculator()
            synastry_scores = score_calculator.calculate_scores({
                'saturn_clashes': saturn_clashes,
                'cinderella_linkages': cinderella_linkages,
                'sexual_linkages': sexual_linkages,
                'romance_linkages': romance_linkages,
                'marital_linkages': marital_linkages,
                'person1_super_aspects': person1_super_aspects,
                'person2_super_aspects': person2_super_aspects
            })

            # Add scores to chart data
            chart_data = {
                "person1": person1_data,
                "person2": person2_data,
                "person1_super_aspects": person1_super_aspects,
                "person2_super_aspects": person2_super_aspects,
                "saturn_clashes": saturn_clashes,
                "cinderella_linkages": cinderella_linkages,
                "sexual_linkages": sexual_linkages,
                "romance_linkages": romance_linkages,
                "marital_linkages": marital_linkages,
                "chart_path": chart_path,
                "compatibility_scores": synastry_scores
            }

            logger.info("Synastry chart data successfully converted to JSON")
            return json.dumps(chart_data, indent=2)

        except Exception as e:
            logger.error(f"Error converting synastry data to JSON: {str(e)}")
            raise

    async def create_transit_loop(
        self,
        from_date: str,
        to_date: str,
        midpoints: Optional[Dict] = None,  # Add midpoints parameter
        generate_chart: bool = False,
        aspects_only: bool = False,
        filter_orb: Optional[float] = None,
        filter_aspects: Optional[List[str]] = None,
        filter_planets: Optional[List[str]] = None
    ) -> Dict:
        """Create transit loop charts for a date range"""
        try:
            # Initialize cosmobiology calculator only if midpoints are provided
            cosmo_calc = CosmobiologyCalculator() if midpoints else None
            
            # Convert string dates to datetime objects
            start_date = datetime.strptime(from_date, "%Y-%m-%d")
            end_date = datetime.strptime(to_date, "%Y-%m-%d")
            logger.info(f"Creating transit loop from {start_date} to {end_date}")
            
            daily_aspects = {}
            turbulent_transits = {}
            cinderella_transits = {}
            golden_transits = {}
            cosmobiology_activations = {} if midpoints else None
            
            current_date = start_date
            while current_date <= end_date:
                # Create transit chart for current date
                transit_data = await self.create_transit_chart(  # Add await here
                    transit_year=current_date.year,
                    transit_month=current_date.month,
                    transit_day=current_date.day,
                    transit_hour=12,  # Default to noon
                    transit_minute=0
                )
                
                # Process the transit data and store results
                date_str = current_date.strftime("%Y-%m-%d")
                if isinstance(transit_data, str):
                    transit_data = json.loads(transit_data)
                    
                daily_aspects[date_str] = transit_data
                
                # Extract and add transit_date to each transit
                if "turbulent_transits" in transit_data:
                    turbulent_list = transit_data["turbulent_transits"]
                    for transit in turbulent_list:
                        transit['transit_date'] = date_str
                    turbulent_transits[date_str] = turbulent_list

                if "cinderella_transits" in transit_data:
                    cinderella_list = transit_data["cinderella_transits"]
                    for transit in cinderella_list:
                        transit['transit_date'] = date_str
                    cinderella_transits[date_str] = cinderella_list

                if "golden_transits" in transit_data:
                    golden_list = transit_data["golden_transits"]
                    for transit in golden_list:
                        transit['transit_date'] = date_str
                    golden_transits[date_str] = golden_list
                
                # Only process cosmobiology if midpoints were provided
                if midpoints and cosmo_calc:
                    daily_cosmo_activations = []
                    transit_planets = transit_data['transit']['subject']['planets']
                    
                    # Convert midpoints data to format needed by CosmobiologyCalculator
                    for mp_name, mp_data in midpoints.items():
                        # Split the midpoint name (format is "planet1-planet2")
                        p1, p2 = mp_name.split('-')
                        midpoint_planets = (p1, p2)
                        midpoint_pos = mp_data['midpoint']
                        
                        for transit_planet_name, transit_planet_data in transit_planets.items():
                            transit_pos = transit_planet_data['abs_pos']
                            
                            activation = cosmo_calc.analyze_transit_to_midpoint(
                                midpoint_pos=midpoint_pos,
                                transit_planet=transit_planet_name,
                                transit_pos=transit_pos,
                                midpoint_planets=midpoint_planets
                            )
                            
                            if activation:
                                activation['date'] = date_str
                                daily_cosmo_activations.append(activation)
                    
                    if daily_cosmo_activations:
                        cosmobiology_activations[date_str] = daily_cosmo_activations
                
                # Move to next day
                current_date += timedelta(days=1)
            
            result = {
                "daily_aspects": daily_aspects,
                "turbulent_transits": turbulent_transits,
                "cinderella_transits": cinderella_transits,
                "golden_transits": golden_transits,
            }
            
            # Only include cosmobiology data if it was calculated
            if cosmobiology_activations is not None:
                result["cosmobiology_activations"] = cosmobiology_activations
            
            return result
            
        except Exception as e:
            logger.error(f"Error in create_transit_loop: {str(e)}")
            raise

    def _filter_transit_data(self, data, aspects_only=False, filter_orb=None, 
                       filter_aspects=None, filter_planets=None):
        """Filter transit data based on specified criteria"""
        try:
            if aspects_only:
                return {
                    'aspects': data.get('aspects', []),
                    'turbulent_transits': data.get('turbulent_transits', [])
                }
            
            filtered_data = data.copy()
            
            # Filter regular aspects
            aspects = data.get('aspects', [])
            if filter_orb is not None:
                aspects = [a for a in aspects if abs(float(a.get('orbit', 0))) <= filter_orb]
            
            if filter_aspects:
                aspects = [a for a in aspects if a.get('aspect_name', '').lower() in 
                          [asp.lower() for asp in filter_aspects]]
            
            if filter_planets:
                filter_planets = [p.lower() for p in filter_planets]
                aspects = [a for a in aspects if 
                          a.get('planet1_name', '').lower() in filter_planets or 
                          a.get('planet2_name', '').lower() in filter_planets]
            
            filtered_data['aspects'] = aspects
            
            # Filter turbulent transits
            turbulent_transits = data.get('turbulent_transits', [])
            if filter_orb is not None:
                turbulent_transits = [t for t in turbulent_transits if abs(float(t.get('orbit', 0))) <= filter_orb]
            
            if filter_aspects:
                turbulent_transits = [t for t in turbulent_transits if t.get('aspect_name', '').lower() in 
                                    [asp.lower() for asp in filter_aspects]]
            
            if filter_planets:
                turbulent_transits = [t for t in turbulent_transits if 
                                    t.get('natal_planet', '').lower() in filter_planets or 
                                    t.get('transit_planet', '').lower() in filter_planets]
            
            filtered_data['turbulent_transits'] = turbulent_transits
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error in _filter_transit_data: {str(e)}")
            raise

 
    def get_synastry_as_data(self, person2_name, person2_birth_data):
        """Get synastry data as JSON"""
        try:
            # Create second subject
            self.create_second_subject(person2_name, person2_birth_data)
            
            # Generate SVG chart
            chart_filename = f"{self.subject.name} - Synastry Chart.svg"
            chart_path = os.path.join(os.path.expanduser("~"), chart_filename)
            
            # Create and save chart
            kerykeion_chart = KerykeionChartSVG(self.subject, self.second_subject, chart_path)
            kerykeion_chart.makeSVG()
            
            # Move chart to charts directory
            new_chart_path = f"charts/{self.subject.name}_{person2_name}_synastry.svg"
            new_chart_path = new_chart_path.replace(" ", "_")
            shutil.move(chart_path, new_chart_path)
            
            # Calculate aspects and linkages
            super_calc = SuperAspectCalculator(self.subject, self.second_subject)
            cinderella_calc = CinderellaAnalyzer(self.subject, self.second_subject)
            sexual_calc = SexualLinkageCalculator(self.subject, self.second_subject)
            
            # Get all aspects and linkages
            person1_super_aspects = super_calc.get_super_aspects(self.subject)
            person2_super_aspects = super_calc.get_super_aspects(self.second_subject)
            saturn_clashes = super_calc.get_saturn_clashes()
            cinderella_linkages = cinderella_calc.get_cinderella_linkages()
            sexual_linkages = sexual_calc.get_sexual_linkages()
            
            # Create data dictionary
            data = {
                "person1": {
                    "subject": self._get_subject_data(self.subject)
                },
                "person2": {
                    "subject": self._get_subject_data(self.second_subject)
                },
                "person1_super_aspects": person1_super_aspects,
                "person2_super_aspects": person2_super_aspects,
                "saturn_clashes": saturn_clashes,
                "cinderella_linkages": cinderella_linkages,
                "sexual_linkages": sexual_linkages,
                "chart_path": new_chart_path
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error in get_synastry_as_data: {str(e)}")
            raise

    def create_marriage_transit_loop(self, from_date: str, to_date: str, 
                               transit_hour: int = 12, transit_minute: int = 0) -> Dict:
        """
        Create specialized transit loop for marriage date analysis.
        Focuses specifically on Cinderella and Turbulent transits.
        """
        try:
            # Convert date strings to datetime objects
            start_date = datetime.strptime(from_date, "%Y-%m-%d")
            end_date = datetime.strptime(to_date, "%Y-%m-%d")
            
            # Initialize results dictionary
            results = {}
            
            # Define marriage-relevant planets to filter
            marriage_planets = ["chiron", "neptune", "venus", "saturn", "jupiter", "sun"]
            
            # Loop through each date
            current_date = start_date
            while current_date <= end_date:
                # Create transit chart for current date
                transit_data = self.create_transit_chart(
                    transit_year=current_date.year,
                    transit_month=current_date.month,
                    transit_day=current_date.day,
                    transit_hour=transit_hour,
                    transit_minute=transit_minute
                )
                
                if isinstance(transit_data, str):
                    try:
                        data = json.loads(transit_data)
                        
                        # Filter for marriage-relevant planets only
                        natal_planets = data["natal"]["planets"]
                        transit_planets = data["transit"]["subject"]["planets"]
                        
                        filtered_natal = {k: v for k, v in natal_planets.items() 
                                       if k.lower() in marriage_planets}
                        filtered_transit = {k: v for k, v in transit_planets.items() 
                                         if k.lower() in marriage_planets}
                        
                        # Update the data with filtered planets
                        data["natal"]["planets"] = filtered_natal
                        data["transit"]["subject"]["planets"] = filtered_transit
                        
                        # Get Cinderella aspects
                        linkage_calc = MagiLinkageCalculator()
                        cinderella_aspects = linkage_calc.find_cinderella_linkages(
                            {"subject": data["natal"]},
                            data["transit"]
                        )
                        
                        # Get turbulent transits
                        turbulent_transits = self.turbulent_transit_service.analyze_turbulent_transits(
                            natal_data={"subject": data["natal"]},
                            transit_data=data["transit"]["subject"]
                        )
                        
                        # Create final structure for this date
                        date_data = {
                            "date": current_date.strftime("%Y-%m-%d"),
                            "time": f"{transit_hour:02d}:{transit_minute:02d}",
                            "natal_planets": filtered_natal,
                            "transit_planets": filtered_transit,
                            "cinderella_aspects": cinderella_aspects,
                            "turbulent_transits": turbulent_transits
                        }
                        
                        # Only include dates with relevant aspects
                        if cinderella_aspects or turbulent_transits:
                            results[current_date.strftime("%Y-%m-%d")] = date_data
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding transit data for {current_date}: {e}")
                        continue
                    
                # Move to next day
                current_date += timedelta(days=1)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in create_marriage_transit_loop: {str(e)}")
            raise

    def calculate_natal_midpoints(self, natal_data):
        planets_data = natal_data['natal']['planets']
        midpoints = {}
        
        # List of planets we want to calculate midpoints for
        planet_list = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 
                       'saturn', 'uranus', 'neptune', 'pluto']
        
        # Calculate midpoints for each planet pair
        for i, p1 in enumerate(planet_list):
            for p2 in planet_list[i+1:]:  # Start from next planet to avoid duplicates
                if p1 in planets_data and p2 in planets_data:
                    pos1 = planets_data[p1]['abs_pos']
                    pos2 = planets_data[p2]['abs_pos']
                    
                    # Calculate midpoint
                    midpoint = (pos1 + pos2) / 2
                    if midpoint >= 360:
                        midpoint -= 360
                    
                    # Store the result
                    pair_name = f"{p1}-{p2}"
                    midpoints[pair_name] = {
                        'midpoint': midpoint,
                        'planet1': {
                            'name': p1,
                            'position': pos1
                        },
                        'planet2': {
                            'name': p2,
                            'position': pos2
                        }
                    }
        
        return midpoints

    async def find_degree_rising_time(self, date: str, degree: float, sign: str) -> Dict:
        """Find when a specific degree of a zodiac sign rises as the Ascendant.
        
        Uses a two-pass algorithm for better precision:
        1. First pass: Check every 4 minutes to find approximate time
        2. Second pass: Fine-tune around found time checking every minute
        
        Args:
            date (str): Date to check in YYYY-MM-DD format
            degree (float): Degree within sign (0-29.99)
            sign (str): Three-letter zodiac sign code
            
        Returns:
            Dict: Time details when the degree rises, or best approximation
        """
        # Convert date string to datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        
        # Get sign number (0-11)
        signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        sign_num = signs.index(sign)
        
        # Calculate absolute position (0-360)
        target_pos = (sign_num * 30) + degree
        
        # Initialize results list
        results = []
        best_match = None
        smallest_diff = float('inf')
        
        # First pass: Check every 4 minutes
        for hour in range(24):
            for minute in range(0, 60, 4):
                current_time = date_obj.replace(hour=hour, minute=minute)
                
                # Create base parameters for transit subject
                transit_params = {
                    "name": "Transit",
                    "year": current_time.year,
                    "month": current_time.month,
                    "day": current_time.day,
                    "hour": current_time.hour,
                    "minute": current_time.minute,
                    "city": self.subject.city,
                    "nation": self.subject.nation,
                    "lat": self.latitude,
                    "lng": self.longitude,
                    "tz_str": self.timezone_str,
                    "online": False
                }
                
                # Use the same zodiac settings as the natal chart if they were specified
                if hasattr(self.subject, 'zodiac_type'):
                    transit_params["zodiac_type"] = self.subject.zodiac_type
                    
                    # If sidereal zodiac is specified, also use the same sidereal_mode
                    if self.subject.zodiac_type == "Sidereal" and hasattr(self.subject, 'sidereal_mode'):
                        transit_params["sidereal_mode"] = self.subject.sidereal_mode
                
                # Create transit subject with the parameters
                transit_subject = AstrologicalSubject(**transit_params)
                
                # Get the Ascendant position
                asc_pos = transit_subject.first_house["abs_pos"]
                
                # Calculate difference, handling 360° wrap
                diff = min(
                    abs(asc_pos - target_pos),
                    abs(asc_pos - target_pos - 360),
                    abs(asc_pos - target_pos + 360)
                )
                
                # Keep track of best match
                if diff < smallest_diff:
                    smallest_diff = diff
                    best_match = (hour, minute, asc_pos)
                
                # If within initial orb, add to results
                if diff < 0.5:
                    results.append((hour, minute, asc_pos))
        
        # If we found any matches in first pass
        if results:
            # Second pass: Fine-tune each potential match
            refined_results = []
            for hour, minute, _ in results:
                # Check 5 minutes before and after in 1-minute increments
                for fine_minute in range(max(0, minute - 5), min(60, minute + 6)):
                    current_time = date_obj.replace(hour=hour, minute=fine_minute)
                    
                    # Create base parameters for transit subject
                    transit_params = {
                        "name": "Transit",
                        "year": current_time.year,
                        "month": current_time.month,
                        "day": current_time.day,
                        "hour": current_time.hour,
                        "minute": fine_minute,
                        "city": self.subject.city,
                        "nation": self.subject.nation,
                        "lat": self.latitude,
                        "lng": self.longitude,
                        "tz_str": self.timezone_str,
                        "online": False
                    }
                    
                    # Use the same zodiac settings as the natal chart if they were specified
                    if hasattr(self.subject, 'zodiac_type'):
                        transit_params["zodiac_type"] = self.subject.zodiac_type
                        
                        # If sidereal zodiac is specified, also use the same sidereal_mode
                        if self.subject.zodiac_type == "Sidereal" and hasattr(self.subject, 'sidereal_mode'):
                            transit_params["sidereal_mode"] = self.subject.sidereal_mode
                    
                    # Create transit subject with the parameters
                    transit_subject = AstrologicalSubject(**transit_params)
                    
                    asc_pos = transit_subject.first_house["abs_pos"]
                    diff = min(
                        abs(asc_pos - target_pos),
                        abs(asc_pos - target_pos - 360),
                        abs(asc_pos - target_pos + 360)
                    )
                    
                    if diff < 0.1:  # Tighter orb for refined results
                        # Convert to local time
                        local_tz = pytz.timezone(self.timezone_str)
                        local_time = current_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
                        
                        refined_results.append({
                            "time": local_time.strftime("%H:%M"),
                            "date": local_time.strftime("%Y-%m-%d"),
                            "timezone": str(local_time.tzinfo),
                            "ascendant_pos": asc_pos,
                            "difference": round(diff, 6)
                        })
            
            # Sort by smallest difference and return best match
            if refined_results:
                return min(refined_results, key=lambda x: x['difference'])
        
        # If no precise match found, use best approximation
        if best_match:
            hour, minute, asc_pos = best_match
            current_time = date_obj.replace(hour=hour, minute=minute)
            local_tz = pytz.timezone(self.timezone_str)
            local_time = current_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
            
            return {
                "time": local_time.strftime("%H:%M"),
                "date": local_time.strftime("%Y-%m-%d"),
                "timezone": str(local_time.tzinfo),
                "ascendant_pos": asc_pos,
                "difference": round(smallest_diff, 6),
                "is_approximate": True
            }
        
        # If all else fails
        raise ValueError(f"Could not find time when {degree}° {sign} rises on {date}")