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

    def create_natal_chart(self):
        """Create and save a natal chart"""
        try:
            # Generate custom filename from name
            name_safe = self.subject.name.replace(" ", "_")
            svg_filename = f"{name_safe}_natal.svg"
            
            # Create charts directory if it doesn't exist
            charts_dir = os.path.join(os.getcwd(), "charts")
            os.makedirs(charts_dir, exist_ok=True)
            logger.info(f"Charts directory created/verified at: {charts_dir}")
            
            # Create full path for the chart
            target_path = os.path.join(charts_dir, svg_filename)
            logger.info(f"Target path for chart: {target_path}")
            
            # Generate chart (it will create file in home directory by default)
            try:
                logger.info("Creating KerykeionChartSVG instance...")
                chart = KerykeionChartSVG(self.subject, chart_type="Natal")
                logger.info("KerykeionChartSVG instance created successfully")
                
                logger.info("Calling makeSVG()...")
                chart.makeSVG()
                logger.info("makeSVG() completed")
            except Exception as e:
                logger.error(f"Error during chart creation: {str(e)}")
                raise
            
            # Default file path used by the library
            default_path = os.path.join(os.path.expanduser("~"), f"{self.subject.name} - Natal Chart.svg")
            logger.info(f"Looking for generated chart at: {default_path}")
            
            # List files in home directory to debug
            home_dir = os.path.expanduser("~")
            files = os.listdir(home_dir)
            svg_files = [f for f in files if f.endswith('.svg')]
            logger.info(f"SVG files found in home directory: {svg_files}")
            
            # Move file to desired location if it exists
            if os.path.exists(default_path):
                shutil.move(default_path, target_path)
                logger.info(f"Chart moved to: {target_path}")
            else:
                logger.error(f"Chart not found at default location: {default_path}")
                raise FileNotFoundError(f"Generated chart file not found at {default_path}")
            
            # Verify final location
            if os.path.exists(target_path):
                logger.info(f"Chart successfully saved to: {target_path}")
            else:
                logger.error(f"Chart file not found at target location: {target_path}")
                raise FileNotFoundError(f"Chart not found at target location: {target_path}")
            
            # Get chart data and parse it
            chart_data = json.loads(self.get_chart_data_as_json())
            
            # Add Cinderella analysis
            cinderella_analysis = self.cinderella_analyzer.analyze_chart(chart_data)
            chart_data['cinderella_analysis'] = cinderella_analysis
            
            # Add chart path
            chart_data['chart_path'] = target_path
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error in create_natal_chart: {str(e)}")
            logger.exception("Full traceback:")
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

            # Create target directory and generate chart
            chart_path = os.path.join('charts', 'transit_chart.svg')
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
                return {
                    "name": planet_obj.name,
                    "sign": planet_obj.sign,
                    "position": round(planet_obj.position, 4),
                    "abs_pos": round(planet_obj.abs_pos, 4),
                    "house": planet_obj.house,
                    "retrograde": planet_obj.retrograde,
                    "declination": round(planet_obj.declination, 4) if hasattr(planet_obj, 'declination') else None
                }

            # Create data structures for both natal and transit
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

            transit_data = {
                "subject": {
                    "name": "Transit",
                    "birth_data": {
                        "date": f"{self.transit_subject.year}-{self.transit_subject.month}-{self.transit_subject.day}",
                        "time": f"{self.transit_subject.hour}:{self.transit_subject.minute:02d}",
                    },
                    "planets": {
                        planet: get_planet_details(getattr(self.transit_subject, planet))
                        for planet in ["sun", "moon", "mercury", "venus", "mars", 
                                     "jupiter", "saturn", "uranus", "neptune", 
                                     "pluto", "chiron"]
                    }
                }
            }

            # Calculate Cinderella aspects between natal and transit
            linkage_calc = MagiLinkageCalculator()
            cinderella_aspects = linkage_calc.find_cinderella_linkages(natal_data, transit_data)

            # Calculate Super aspects between natal and transit
            super_calc = SuperAspectCalculator()
            super_aspects = super_calc.find_super_aspects(natal_data)
            transit_super_aspects = super_calc.find_super_aspects(transit_data)
            
            chart_data = {
                "natal": natal_data["subject"],
                "transit": transit_data["subject"],
                "natal_super_aspects": super_aspects,
                "transit_super_aspects": transit_super_aspects,
                "cinderella_aspects": cinderella_aspects,
                "chart_path": chart_path
            }

            return json.dumps(chart_data, indent=2)

        except Exception as e:
            logger.error(f"Error converting transit data to JSON: {str(e)}")
            raise

    def get_horizons_data(self, planet_name):
        """Get planet data from Horizons API"""
        try:
            # Convert local time to UTC
            local_tz = pytz.timezone(self.subject.tz_str)
            local_dt = local_tz.localize(datetime(
                self.subject.year,
                self.subject.month,
                self.subject.day,
                self.subject.hour,
                self.subject.minute
            ))
            utc_dt = local_dt.astimezone(pytz.UTC)
            
            # Format time for Horizons (add a small time window)
            start_time = (utc_dt - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
            stop_time = (utc_dt + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
            
            # Use the longitude and latitude from the constructor
            observer_longitude = self.longitude  # Use class attribute
            observer_latitude = self.latitude    # Use class attribute
            
            # Set up query parameters
            params = {
                'format': 'text',
                'COMMAND': f"'{self.planet_mappings.get(planet_name.lower())}'",
                'EPHEM_TYPE': 'OBSERVER',
                'CENTER': 'coord@399',
                'COORD_TYPE': 'GEODETIC',
                'SITE_COORD': f"{observer_longitude},{observer_latitude},0",
                'START_TIME': start_time,
                'STOP_TIME': stop_time,
                'STEP_SIZE': '1m',
                'QUANTITIES': '1,2',  # RA/DEC and alt/az
                'REF_SYSTEM': 'J2000'
            }
            
            logger.debug(f"Sending request to Horizons with params: {params}")
            
            # Make request
            response = requests.get(self.horizons_url, params=params)
            response.raise_for_status()
            
            # Log the full response for debugging
            logger.debug(f"API Response for {planet_name}:\n{response.text}")
            
            # Parse the text response
            if '$$SOE' in response.text and '$$EOE' in response.text:
                data = response.text.split('$$SOE\n')[1].split('\n$$EOE')[0].strip()
                lines = data.split('\n')
                if lines:
                    # Parse the first line of data
                    fields = lines[0].split(',')
                    if len(fields) >= 4:  # We expect at least 4 fields
                        declination = float(fields[3].strip())
                        logger.info(f"Got declination from Horizons for {planet_name}: {declination}")
                        return declination
                
            raise ValueError(f"Could not parse declination from response for {planet_name}")
            
        except Exception as e:
            logger.error(f"Error getting Horizons data for {planet_name}: {str(e)}")
            logger.error(f"Response content: {response.text if 'response' in locals() else 'No response'}")
            return None

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
        Calculate declination using both longitude and latitude with date-specific obliquity
        
        Args:
            longitude (float): Ecliptic longitude in degrees
            latitude (float): Ecliptic latitude in degrees (optional)
        """
        try:
            # Get date-specific obliquity
            obliquity = self.calculate_obliquity(
                self.subject.year,
                self.subject.month,
                self.subject.day
            )
            
            # Convert to radians
            lon_rad = math.radians(longitude)
            lat_rad = math.radians(latitude)
            obliquity_rad = math.radians(obliquity)
            
            # Full formula including latitude
            declination = math.asin(
                math.sin(lat_rad) * math.cos(obliquity_rad) +
                math.cos(lat_rad) * math.sin(obliquity_rad) * math.sin(lon_rad)
            )
            
            result = round(math.degrees(declination), 4)
            logger.info(f"Calculated declination using obliquity {obliquity}° for lon:{longitude}, lat:{latitude}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating declination: {str(e)}")
            return None

    def get_declination(self, planet_name, abs_pos):
        """Get declination for a planet"""
        try:
            logger.info(f"Calculating declination for {planet_name} at position {abs_pos}")
            return self.calculate_declination(abs_pos)
            
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
                
                declination = self.get_declination(planet_name, abs_pos)
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
            def get_planet_details(planet_obj):
                return {
                    "name": planet_obj.name,
                    "sign": planet_obj.sign,
                    "position": round(planet_obj.position, 4),
                    "abs_pos": round(planet_obj.abs_pos, 4),
                    "house": planet_obj.house,
                    "retrograde": planet_obj.retrograde,
                    "declination": round(planet_obj.declination, 4) if hasattr(planet_obj, 'declination') else None
                }

            # Create the data structure for both charts
            person1_data = {
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

            person2_data = {
                "subject": {
                    "name": self.subject2.name,
                    "birth_data": {
                        "date": f"{self.subject2.year}-{self.subject2.month}-{self.subject2.day}",
                        "time": f"{self.subject2.hour}:{self.subject2.minute:02d}",
                        "location": f"{self.subject2.city}, {self.subject2.nation}",
                        "longitude": round(self.longitude, 4),
                        "latitude": round(self.latitude, 4)
                    },
                    "planets": {
                        planet: get_planet_details(getattr(self.subject2, planet))
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
            cinderella_linkages = linkage_calc.find_cinderella_linkages(person1_data, person2_data)

            # Calculate Super aspects for both charts
            super_calc = SuperAspectCalculator()
            person1_super_aspects = super_calc.find_super_aspects(person1_data)
            person2_super_aspects = super_calc.find_super_aspects(person2_data)
            
            # Create the final data structure
            chart_data = {
                "person1": person1_data,
                "person2": person2_data,
                "person1_super_aspects": person1_super_aspects,
                "person2_super_aspects": person2_super_aspects,
                "saturn_clashes": saturn_clashes,
                "cinderella_linkages": cinderella_linkages,
                "chart_path": chart_path
            }

            logger.info("Synastry chart data successfully converted to JSON")
            return json.dumps(chart_data, indent=2)

        except Exception as e:
            logger.error(f"Error converting synastry data to JSON: {str(e)}")
            raise