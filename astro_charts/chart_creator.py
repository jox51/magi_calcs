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

    def __init__(self, name, year, month, day, hour, minute, city, nation):
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
        self.subject = AstrologicalSubject(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city,
            nation=nation,
            lat=self.latitude,
            lng=self.longitude,
            tz_str=self.timezone_str,
            online=False  # Prevent online lookups
        )
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

    def create_transit_chart(self, transit_year=None, transit_month=None, 
                             transit_day=None, transit_hour=None, transit_minute=None):
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
            self.transit_subject = AstrologicalSubject(
                name="Transit",
                year=transit_time.year,
                month=transit_time.month,
                day=transit_time.day,
                hour=transit_time.hour,
                minute=transit_time.minute,
                city=self.subject.city,
                nation=self.subject.nation,
                lat=self.latitude,
                lng=self.longitude,
                tz_str=self.timezone_str,
                online=False
            )
            logger.info("Transit subject created successfully")

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
                        "time": f"{self.subject.hour}:{self.subject.minute:02d}",
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

            # Add aspects to transit data
            transit_data["transit_super_aspects"] = transit_super_aspects
            transit_data["cinderella_aspects"] = cinderella_aspects

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
                "turbulent_transits": turbulent_transits
            }

            logger.info(f"Found {len(turbulent_transits)} turbulent transits")
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

            # Add aspects to chart data, including is_cinderella
            chart_data["subject"]["aspects"] = [
                {
                    'p1_name': aspect.p1_name,
                    'p2_name': aspect.p2_name,
                    'aspect_name': aspect.aspect_name,
                    'aspect_degrees': aspect.aspect_degrees,
                    'orbit': round(aspect.orbit, 4),
                    'actual_degrees': round(aspect.actual_degrees, 4),
                    'is_harmonious': aspect.is_harmonious,
                    'is_cinderella': aspect.is_cinderella
                }
                for aspect in aspects
            ]
            
            # Calculate Super aspects
            super_calc = SuperAspectCalculator()
            super_aspects = super_calc.find_super_aspects(chart_data)
            
            chart_data["super_aspects"] = super_aspects
            
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
            self.subject2 = AstrologicalSubject(
                name=name2,
                year=year2,
                month=month2,
                day=day2,
                hour=hour2,
                minute=minute2,
                city=city2,
                nation=nation2,
                lat=lat2,
                lng=lng2,
                tz_str=tz_str2,
                online=False
            )
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
                logger.info(f"Got declination for {planet_name} on {birth_date}: {declination}")

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
            
            # Create the final data structure
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
                "chart_path": chart_path
            }

            logger.info("Synastry chart data successfully converted to JSON")
            return json.dumps(chart_data, indent=2)

        except Exception as e:
            logger.error(f"Error converting synastry data to JSON: {str(e)}")
            raise
    def create_transit_loop(self, from_date, to_date, generate_chart=False, aspects_only=False, 
                          filter_orb=None, filter_aspects=None, filter_planets=None):
        """Create transit charts for a range of dates"""
        try:
            # Convert date strings to datetime objects
            start_date = datetime.strptime(from_date, "%Y-%m-%d")
            end_date = datetime.strptime(to_date, "%Y-%m-%d")
            
            # Initialize results dictionary
            results = {}
            
            # Loop through each date
            current_date = start_date
            while current_date <= end_date:
                # Create transit chart for current date (removed generate_chart parameter)
                transit_data = self.create_transit_chart(
                    transit_year=current_date.year,
                    transit_month=current_date.month,
                    transit_day=current_date.day,
                    transit_hour=14,  # Default to 2 PM
                    transit_minute=30
                )
                
                # Process the transit data based on filters
                if isinstance(transit_data, str):
                    try:
                        data = json.loads(transit_data)
                        
                         # Use Cython-optimized calculation with correct data structure
                        filtered_data = calculate_transit_data(
                            natal_data=data,  # Pass the full data object
                            transit_data=data.get('transit', {}),  # Get the transit section
                            filter_orb=-1.0 if filter_orb is None else float(filter_orb)
                            )
                
                        # Update the transit section in the original data
                        data['transit'] = filtered_data
                        
                        # Add turbulent transit analysis for each day
                        turbulent_transits = self.turbulent_transit_service.analyze_turbulent_transits(
                            natal_data={"subject": data["natal"]},
                            transit_data=data["transit"]["subject"]
                        )
                        
                        # Add turbulent transits to the data
                        data['transit']["turbulent_transits"] = turbulent_transits
                        
                        # Apply filters if specified
                        if aspects_only or filter_orb or filter_aspects or filter_planets:
                            filtered_data = self._filter_transit_data(
                                data,
                                aspects_only=aspects_only,
                                filter_orb=filter_orb,
                                filter_aspects=filter_aspects,
                                filter_planets=filter_planets
                            )
                            results[current_date.strftime("%Y-%m-%d")] = filtered_data
                        else:
                            results[current_date.strftime("%Y-%m-%d")] = data
                            
                    except json.JSONDecodeError:
                        results[current_date.strftime("%Y-%m-%d")] = transit_data
                else:
                    results[current_date.strftime("%Y-%m-%d")] = transit_data
                
                # Move to next day
                current_date += timedelta(days=1)
            
            return results
            
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