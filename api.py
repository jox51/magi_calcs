from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from astro_charts.chart_creator import ChartCreator
import json
import logging
from dotenv import load_dotenv
from astro_charts.services.pocketbase_service import PocketbaseService
import os
import shutil
from astro_charts.services.transit_visualization_service import TransitVisualizationService
from astro_charts.services.synastry_visualization_service import SynastryVisualizationService
from astro_charts.services.alt_marriage_date_finder import AltMarriageDateFinder
from astro_charts.services.natal_visualization_service import NatalVisualizationService
from astro_charts.services.single_transit_visualization_service import SingleTransitVisualizationService
import time
from pathlib import Path
from astro_charts.services.transit_loop_midpoint_visualization_service import TransitLoopMidpointVisualizationService
from astro_charts.services.vedic_lucky_times_service import VedicLuckyTimesService

# Load environment variables at startup
load_dotenv()

app = FastAPI(title="Astrology Charts API")
logger = logging.getLogger(__name__)

# Base models for shared attributes
class BaseBirthData(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str
    nation: str
    user_id: str
    job_id: str
    zodiac_type: Optional[str] = None
    sidereal_mode: Optional[str] = None

class TransitDateData(BaseModel):
    transit_year: Optional[int] = None
    transit_month: Optional[int] = None
    transit_day: Optional[int] = None
    transit_hour: Optional[int] = None
    transit_minute: Optional[int] = None

class TransitLoopRequest(BaseModel):
    # Birth data
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str
    nation: str
    user_id: str
    job_id: str
    
    # Transit loop specific data
    from_date: str
    to_date: str
    transit_hour: int
    transit_minute: int
    
    # Optional parameters
    generate_chart: bool = False
    aspects_only: bool = False
    filter_orb: Optional[float] = None
    filter_aspects: Optional[List[str]] = None
    filter_planets: Optional[List[str]] = None
    zodiac_type: Optional[str] = None
    sidereal_mode: Optional[str] = None

class SynastryPerson(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str
    nation: str

class SynastryRequest(BaseModel):
    # First person's data
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str
    nation: str
    
    # Second person's data
    name2: str
    year2: int
    month2: int
    day2: int
    hour2: int
    minute2: int
    city2: str
    nation2: str
    
    # Job identifiers
    user_id: str
    job_id: str
    
    # New fields
    find_marriage_date: bool = False
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    transit_hour: Optional[int] = 12
    transit_minute: Optional[int] = 0
    zodiac_type: Optional[str] = None
    sidereal_mode: Optional[str] = None

class TransitChartRequest(BaseModel):
    birth_data: BaseBirthData
    transit_data: TransitDateData

class MidpointTransitLoopRequest(BaseModel):
    # Birth data
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str
    nation: str
    
    # Transit loop specific data
    from_date: str
    to_date: str
    transit_hour: int
    transit_minute: int
    
    # Job identifiers
    user_id: str
    job_id: str
    
    # Optional parameters
    filter_orb: Optional[float] = None
    filter_aspects: Optional[List[str]] = None
    filter_planets: Optional[List[str]] = None
    zodiac_type: Optional[str] = None
    sidereal_mode: Optional[str] = None

class LuckyTimesRequest(BaseModel):
    # Birth data
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str
    nation: str
    user_id: str
    job_id: str
    
    # Date to calculate lucky time for
    target_date: str  # Format: "YYYY-MM-DD"
    transit_hour: Optional[int] = 12
    transit_minute: Optional[int] = 0
    zodiac_type: Optional[str] = None
    sidereal_mode: Optional[str] = None

class VedicLuckyTimesRequest(BaseModel):
    # Birth data
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str
    nation: str
    user_id: str
    job_id: str
    
    # Date range for transit calculations
    from_date: str  # Format: "YYYY-MM-DD"
    # to_date: sstr    # Format: "YYYY-MM-DD"
    
    # Optional parameters
    include_nakshatras: bool = False  # For future implementation
    transit_hour: int = 12
    transit_minute: int = 0
    orb: float = 1.0  # Increased orb to 3 degrees
    zodiac_type: Optional[str] = None
    sidereal_mode: Optional[str] = None
    
    # Current location for location-specific Yogi point calculations
    current_city: Optional[str] = None
    current_nation: Optional[str] = None

# Add this sign mapping at the top of the file with other imports
ZODIAC_SIGNS = {
    "Ari": "Aries",
    "Tau": "Taurus",
    "Gem": "Gemini",
    "Can": "Cancer",
    "Leo": "Leo",
    "Vir": "Virgo",
    "Lib": "Libra",
    "Sco": "Scorpio",
    "Sag": "Sagittarius",
    "Cap": "Capricorn",
    "Aqu": "Aquarius",
    "Pis": "Pisces"
}

def cleanup_old_charts(days=7):
    """Remove chart files older than specified days"""
    try:
        charts_dir = Path('charts')
        if not charts_dir.exists():
            return
        
        current_time = time.time()
        max_age = days * 24 * 60 * 60  # Convert days to seconds
        
        for chart_file in charts_dir.glob('*'):
            if chart_file.is_file():
                file_age = current_time - chart_file.stat().st_mtime
                if file_age > max_age:
                    chart_file.unlink()
                    logger.info(f"Removed old chart file: {chart_file}")
    except Exception as e:
        logger.error(f"Error during chart cleanup: {str(e)}")

@app.post("/charts/natal")
async def create_natal_chart(data: BaseBirthData):
    cleanup_old_charts()
    try:
        # Create chart
        chart_creator = ChartCreator(
            name=data.name,
            year=data.year,
            month=data.month,
            day=data.day,
            hour=data.hour,
            minute=data.minute,
            city=data.city,
            nation=data.nation,
            zodiac_type=data.zodiac_type,
            sidereal_mode=data.sidereal_mode
        )
        
        # Get chart data
        chart_data = json.loads(chart_creator.get_chart_data_as_json())
        
        # Generate SVG chart
        _, _ = chart_creator.create_natal_chart()
        
         # Construct the actual file path where the chart was moved
        name_safe = data.name.replace(" ", "_")
        final_chart_path = os.path.join('charts', f"{name_safe}_natal.svg")
        
        logger.info(f"Using final chart path: {os.path.abspath(final_chart_path)}")
        
        # Create visualization
        viz_path = f"charts/{name_safe}_natal_viz.svg"
        viz_html_path = f"charts/{name_safe}_natal_viz.html"
        viz_service = NatalVisualizationService()
        
        try:
            viz_chart_path, viz_html_path = viz_service.create_visualization(
                chart_data, 
                viz_path,
                viz_html_path
            )
        except Exception as viz_error:
            logger.error(f"Visualization error: {str(viz_error)}")
            viz_chart_path = None
            viz_html_path = None
        
        # Save to PocketBase
        pb_service = PocketbaseService()
        record = pb_service.create_natal_chart(
            natal_data=chart_data,
            chart_path=final_chart_path,
            easy_chart=viz_chart_path,
            easy_chart_html=viz_html_path,
            user_id=data.user_id,
            job_id=data.job_id
        )
        
        # Return the data including the PocketBase record
        return {
            "chart_data": chart_data,
            "visualization_path": viz_chart_path if viz_chart_path else None,
            "visualization_html_path": viz_html_path if viz_html_path else None,
            "record": record
        }
        
    except Exception as e:
        logger.error(f"Error creating natal chart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/charts/transit")
async def create_transit_chart(request: TransitChartRequest):
    cleanup_old_charts()
    try:
        chart_creator = ChartCreator(
            name=request.birth_data.name,
            year=request.birth_data.year,
            month=request.birth_data.month,
            day=request.birth_data.day,
            hour=request.birth_data.hour,
            minute=request.birth_data.minute,
            city=request.birth_data.city,
            nation=request.birth_data.nation,
            zodiac_type=request.birth_data.zodiac_type,
            sidereal_mode=request.birth_data.sidereal_mode
        )
        
        # Get chart data and generate chart
        chart_data = await chart_creator.create_transit_chart(
            transit_year=request.transit_data.transit_year,
            transit_month=request.transit_data.transit_month,
            transit_day=request.transit_data.transit_day,
            transit_hour=request.transit_data.transit_hour,
            transit_minute=request.transit_data.transit_minute,
            zodiac_type=request.transit_data.zodiac_type if hasattr(request.transit_data, 'zodiac_type') else None,
            sidereal_mode=request.transit_data.sidereal_mode if hasattr(request.transit_data, 'zodiac_type') and hasattr(request.transit_data, 'sidereal_mode') else None
        )
        
        # Parse chart data
        chart_data = json.loads(chart_data)
        
        # Construct the file paths
        name_safe = request.birth_data.name.replace(" ", "_")
        transit_date = f"{request.transit_data.transit_year}_{request.transit_data.transit_month}_{request.transit_data.transit_day}"
        final_chart_path = os.path.join('charts', f"{name_safe}_transit_chart.svg")
        viz_path = f"charts/{name_safe}_transit_viz.svg"
        viz_html_path = f"charts/{name_safe}_transit_viz.html"
        
        logger.info(f"Using final chart path: {os.path.abspath(final_chart_path)}")
        
        # Verify file exists
        if not os.path.exists(final_chart_path):
            raise FileNotFoundError(f"Transit chart file not found at {final_chart_path}")
        
        # Create visualization
        viz_service = SingleTransitVisualizationService()
        try:
            viz_chart_path, viz_html_path = viz_service.create_visualization(
                chart_data, 
                viz_path,
                viz_html_path
            )
            if viz_chart_path:
                logger.info(f"Created easy visualization at {viz_chart_path}")
        except Exception as viz_error:
            logger.error(f"Visualization error: {str(viz_error)}")
            viz_chart_path = None
            viz_html_path = None
        
        # Save to PocketBase
        pb_service = PocketbaseService()
        record = pb_service.create_single_transit_chart(
            transit_data=chart_data,
            chart_path=final_chart_path,
            easy_chart=viz_chart_path,
            easy_chart_html=viz_html_path,
            user_id=request.birth_data.user_id,
            job_id=request.birth_data.job_id
        )
        
        # Return both chart data and PocketBase record
        return {
            "chart_data": chart_data,
            "visualization_path": viz_chart_path if viz_chart_path else None,
            "visualization_html_path": viz_html_path if viz_html_path else None,
            "record": record
        }
        
    except Exception as e:
        logger.error(f"Error creating transit chart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/charts/transit-loop")
async def create_transit_loop(request: TransitLoopRequest):
    cleanup_old_charts()
    try:
        chart_creator = ChartCreator(
            name=request.name,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            city=request.city,
            nation=request.nation,
            zodiac_type=request.zodiac_type,
            sidereal_mode=request.sidereal_mode
        )
        
        # Get transit loop results
        results = await chart_creator.create_transit_loop(
            from_date=request.from_date,
            to_date=request.to_date,
            generate_chart=request.generate_chart,
            aspects_only=request.aspects_only,
            filter_orb=request.filter_orb,
            filter_aspects=request.filter_aspects,
            filter_planets=request.filter_planets
        )
        
        logger.info(f"Transit Loop Results: {results}")

        # Create visualization
        name_safe = request.name.replace(" ", "_")
        viz_path = f"charts/{name_safe}_transit_loop_viz.svg"
        viz_html_path = f"charts/{name_safe}_transit_loop_viz.html"

        viz_service = TransitVisualizationService()
        try:
            viz_chart_path, viz_html_path = viz_service.create_visualization(
                results, 
                viz_path,
                viz_html_path
            )
        except Exception as viz_error:
            logger.error(f"Visualization error: {str(viz_error)}")
            viz_chart_path = None
            viz_html_path = None

        # Save to PocketBase
        try:
            pb_service = PocketbaseService()
            record = pb_service.create_transit_loop_charts(
                transit_loop_data={
                    "natal": results.get("natal", {}),
                    "transit_data": results,
                    "visualization_path": viz_chart_path,
                    "visualization_html_path": viz_html_path,
                    "date_range": {
                        "from_date": request.from_date,
                        "to_date": request.to_date
                    }
                },
                user_id=request.user_id,
                job_id=request.job_id
            )
        except Exception as pb_error:
            logger.error(f"PocketBase error: {str(pb_error)}")
            raise

        # Return results
        return {
            "chart_data": results,
            "visualization_path": viz_chart_path if viz_chart_path else None,
            "visualization_html_path": viz_html_path if viz_html_path else None,
            "daily_aspects": results.get("daily_aspects", {}),
            "turbulent_transits": results.get("turbulent_transits", {})
        }

    except Exception as e:
        logger.error(f"Error creating transit loop: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

# Add this function before initializing MarriageDateFinder
async def transit_loop_wrapper(
    name: str, 
    year: int, 
    month: int, 
    day: int, 
    hour: int, 
    minute: int, 
    city: str, 
    nation: str,
    from_date: str, 
    to_date: str, 
    transit_hour: int,
    transit_minute: int, 
    user_id: str, 
    job_id: str,
    filter_planets: Optional[List[str]] = None,
    generate_chart: bool = False,  # Add these optional parameters
    aspects_only: bool = False,
    filter_orb: Optional[float] = None,
    filter_aspects: Optional[List[str]] = None,
    zodiac_type: Optional[str] = None,
    sidereal_mode: Optional[str] = None
) -> Dict:
    """Wrapper function to convert parameters into TransitLoopRequest"""
    request = TransitLoopRequest(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        nation=nation,
        from_date=from_date,
        to_date=to_date,
        transit_hour=transit_hour,
        transit_minute=transit_minute,
        user_id=user_id,
        job_id=job_id,
        generate_chart=generate_chart,
        aspects_only=aspects_only,
        filter_orb=filter_orb,
        filter_aspects=filter_aspects,
        filter_planets=filter_planets,
        zodiac_type=zodiac_type,
        sidereal_mode=sidereal_mode
    )
    
    result = await create_transit_loop(request)
    return result.get("chart_data", {})

# Initialize new marriage finder
alt_marriage_finder = AltMarriageDateFinder(transit_loop_wrapper)

@app.post("/charts/synastry")
async def create_synastry_chart(request: SynastryRequest):
    cleanup_old_charts()
    try:
        chart_creator = ChartCreator(
            name=request.name,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            city=request.city,
            nation=request.nation,
            zodiac_type=request.zodiac_type,
            sidereal_mode=request.sidereal_mode
        )
        
        # Get chart data and generate chart
        chart_data = chart_creator.create_synastry_chart(
            name2=request.name2,
            year2=request.year2,
            month2=request.month2,
            day2=request.day2,
            hour2=request.hour2,
            minute2=request.minute2,
            city2=request.city2,
            nation2=request.nation2
        )
        
        # Parse chart data
        chart_data = json.loads(chart_data)
        is_marriage_request = False
        # print("chart_data in API", chart_data)
        
        # If marriage date finding is requested
        if request.find_marriage_date and request.from_date and request.to_date:
            logger.info("Finding potential marriage dates using alternative finder...")
            
            # Replace old marriage_finder with alt_marriage_finder
            marriage_dates = await alt_marriage_finder.find_matching_dates(
                chart_data,
                request.from_date,
                request.to_date,
                request.transit_hour or 12,
                request.transit_minute or 0,
                request.user_id,
                request.job_id
            )
            logger.info(f"Marriage dates found: {marriage_dates}")
            is_marriage_request = True
            
            # Add marriage dates to chart data
            chart_data["potential_marriage_dates"] = marriage_dates
        
        # Construct the file paths
        name_safe = f"{request.name}_{request.name2}".replace(" ", "_")
        final_chart_path = os.path.join('charts', f"{name_safe}_synastry.svg")
        easy_chart_path = os.path.join('charts', f"{name_safe}_synastry_easy.svg")
        easy_chart_html_path = os.path.join('charts', f"{name_safe}_synastry_easy.html")
        
        logger.info(f"Using final chart path: {os.path.abspath(final_chart_path)}")
        
        # Verify traditional chart exists
        if not os.path.exists(final_chart_path):
            raise FileNotFoundError(f"Synastry chart file not found at {final_chart_path}")
        
        # Create easy visualization
        viz_service = SynastryVisualizationService()
        viz_chart_path, easy_chart_html_path = viz_service.create_visualization(chart_data, easy_chart_path, easy_chart_html_path)

        if viz_chart_path:
            logger.info(f"Created easy visualization at {viz_chart_path}")
        
        # Save to PocketBase with both charts
        pb_service = PocketbaseService()
        record = pb_service.create_synastry_chart(
            synastry_data=chart_data,
            chart_path=final_chart_path,
            easy_chart_path=viz_chart_path,
            easy_chart_html_path=easy_chart_html_path,
            user_id=request.user_id,
            job_id=request.job_id,
            is_marriage_request=is_marriage_request
        )
        
        # Return both chart data, visualization path and PocketBase record
        return {
            "chart_data": chart_data,
            "visualization_path": viz_chart_path if viz_chart_path else None,
            "easy_chart_html_path": easy_chart_html_path if easy_chart_html_path else None,
            # "record": record
        }
        
    except Exception as e:
        logger.error(f"Error creating synastry chart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/charts/midpoint-transit-loop")
async def create_midpoint_transit_loop(request: MidpointTransitLoopRequest):
    cleanup_old_charts()
    try:
        chart_creator = ChartCreator(
            name=request.name,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            city=request.city,
            nation=request.nation,
            zodiac_type=request.zodiac_type,
            sidereal_mode=request.sidereal_mode
        )
        
        # Create natal chart and get data
        natal_data, source_path = chart_creator.create_natal_chart()
        
        # Calculate midpoints
        midpoints = chart_creator.calculate_natal_midpoints(natal_data)
        
        # Get transit loop data, passing the midpoints
        transit_data = await chart_creator.create_transit_loop(
            from_date=request.from_date,
            to_date=request.to_date,
            midpoints=midpoints,  # Pass midpoints here
            filter_orb=request.filter_orb,
            filter_aspects=request.filter_aspects,
            filter_planets=request.filter_planets
        )
        
        # logger.info(f"Transit data: {transit_data}")
        
         # Create visualization
        name_safe = request.name.replace(" ", "_")
        viz_path = f"charts/{name_safe}_transit_loop_mp_viz.svg"
        viz_html_path = f"charts/{name_safe}_transit_loop_mp_viz.html"

        
        
        # Create visualization
        viz_service = TransitLoopMidpointVisualizationService()
        viz_chart_path, viz_html_path = viz_service.create_visualization(
            transit_data, 
            viz_path,
            viz_html_path
        )
        
        # Save to PocketBase
        pb_service = PocketbaseService()
        record = pb_service.create_cosmo_chart(
            transit_data=transit_data,
            chart_path=viz_chart_path,
            chart_html_path=viz_html_path,
            user_id=request.user_id,
            job_id=request.job_id
        )
        
        return {
            "natal_data": natal_data,
            "midpoints": midpoints,
            "transit_data": transit_data,
            "chart_path": source_path,
            "record": record
        }

    except Exception as e:
        logger.error(f"Error creating midpoint transit loop: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/charts/planets")
async def get_planets(data: BaseBirthData):
    try:
        # Create chart
        chart_creator = ChartCreator(
            name=data.name,
            year=data.year,
            month=data.month,
            day=data.day,
            hour=data.hour,
            minute=data.minute,
            city=data.city,
            nation=data.nation,
            zodiac_type=data.zodiac_type,
            sidereal_mode=data.sidereal_mode
        )
        
        # Get chart data
        chart_data = json.loads(chart_creator.get_chart_data_as_json())
        
        # Extract just the planets data
        planets_data = chart_data["subject"]["planets"]
        
        # Convert abbreviated signs to full names
        for planet in planets_data.values():
            if "sign" in planet:
                planet["sign"] = ZODIAC_SIGNS.get(planet["sign"], planet["sign"])
        
        # Save to PocketBase
        pb_service = PocketbaseService()
        record = pb_service.create_planets_record(
            planets_data=planets_data,
            user_id=data.user_id,
            job_id=data.job_id
        )
        
        return {
            "planets": planets_data,
            "record": record
        }
        
    except Exception as e:
        logger.error(f"Error getting planetary positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/charts/lucky-times")
async def get_lucky_times(data: LuckyTimesRequest):
    try:
        # Create chart
        chart_creator = ChartCreator(
            name=data.name,
            year=data.year,
            month=data.month,
            day=data.day,
            hour=data.hour,
            minute=data.minute,
            city=data.city,
            nation=data.nation,
            zodiac_type=data.zodiac_type,
            sidereal_mode=data.sidereal_mode
        )
        
        # Get chart data
        chart_data = json.loads(chart_creator.get_chart_data_as_json())
        
        # Extract required positions
        ascendant_pos = chart_data["subject"]["houses"]["ascendant"]["abs_pos"]
        moon_pos = chart_data["subject"]["planets"]["moon"]["abs_pos"]
        sun_pos = chart_data["subject"]["planets"]["sun"]["abs_pos"]
        
        # Parse house number correctly from the house name
        sun_house_name = chart_data["subject"]["planets"]["sun"]["house"]
        
        # Convert word numbers to integers
        word_to_number = {
            "First": 1, "Second": 2, "Third": 3, "Fourth": 4, "Fifth": 5, "Sixth": 6,
            "Seventh": 7, "Eighth": 8, "Ninth": 9, "Tenth": 10, "Eleventh": 11, "Twelfth": 12
        }
        
        # Extract the word part before "_House"
        house_word = sun_house_name.split("_")[0]
        sun_house = word_to_number.get(house_word)
        
        if sun_house is None:
            logger.error(f"Could not parse house number from {sun_house_name}")
            raise ValueError(f"Invalid house name format: {sun_house_name}")
            
        logger.info(f"Sun house: {sun_house} (parsed from {sun_house_name})")
        
        # Calculate Part of Fortune based on whether it's a day or night chart
        if sun_house >= 7 and sun_house <= 12:  # Day chart
            pof_pos = (ascendant_pos + moon_pos - sun_pos) % 360
        else:  # Night chart
            pof_pos = (ascendant_pos + sun_pos - moon_pos) % 360
            
        # Determine POF sign and degree
        pof_sign_num = int(pof_pos / 30)
        pof_degree = pof_pos % 30
        
        # Convert sign number to sign name
        signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        pof_sign = signs[pof_sign_num]
        
        # Create POF data structure
        pof_data = {
            "name": "Part of Fortune",
            "sign": pof_sign,
            "position": pof_degree,
            "abs_pos": pof_pos,
            "is_day_chart": sun_house >= 7 and sun_house <= 12
        }
        
        # Calculate when POF degree rises on target date
        lucky_time = await chart_creator.find_degree_rising_time(
            date=data.target_date,
            degree=pof_degree,
            sign=pof_sign
        )
        
        # Extract planets data
        planets_data = chart_data["subject"]["planets"]

        
        # Convert abbreviated signs to full names
        for planet in planets_data.values():
            if "sign" in planet:
                planet["sign"] = ZODIAC_SIGNS.get(planet["sign"], planet["sign"])
        
        # Initialize response structure
        response = {
            "traditional_method": {
                "part_of_fortune": pof_data,
                "planets": planets_data,
                "lucky_time_details": {
                    "date": data.target_date,
                    "time": lucky_time["time"],
                    "timezone": lucky_time["timezone"],
                    "ascendant_position": lucky_time["ascendant_pos"],
                    "pof_degree": pof_degree,
                    "pof_sign": pof_sign,
                    "is_day_chart": pof_data["is_day_chart"]
                }
            }
        }
        
        # Find last Jupiter-POF conjunction
        # First get current Jupiter position relative to POF
        today = datetime.now()
        current_transit = await chart_creator.create_transit_chart(
            transit_year=today.year,
            transit_month=today.month,
            transit_day=today.day,
            transit_hour=data.transit_hour,
            transit_minute=data.transit_minute,
            zodiac_type=data.zodiac_type,
            sidereal_mode=data.sidereal_mode
        )
        current_transit = json.loads(current_transit)
        current_jupiter_pos = current_transit["transit"]["subject"]["planets"]["jupiter"]["abs_pos"]
        
        # Calculate current orb to POF
        current_jupiter_pof_diff = min(
            abs(current_jupiter_pos - pof_pos),
            abs(current_jupiter_pos - pof_pos - 360),
            abs(current_jupiter_pos - pof_pos + 360)
        )
        
        # Estimate months since last conjunction based on current orb
        # Jupiter moves about 30° per year, or 2.5° per month
        # We need to determine if Jupiter has already passed POF or not
        jupiter_past_pof = False
        
        # Check if Jupiter is ahead of POF in the zodiac
        if (current_jupiter_pos > pof_pos and (current_jupiter_pos - pof_pos) < 180) or \
           (current_jupiter_pos < pof_pos and (pof_pos - current_jupiter_pos) > 180):
            jupiter_past_pof = True
            
        # If Jupiter is past POF, we need to find how far it's gone
        # If not, we need to find how far it still needs to go to complete a full cycle
        if jupiter_past_pof:
            # Jupiter has passed POF, so the orb represents how far it's moved since conjunction
            months_since_conjunction = int(current_jupiter_pof_diff / 2.5)
        else:
            # Jupiter has not yet reached POF, so we need to find when it was last there (almost a full cycle ago)
            # A full cycle is 360°, so we subtract the current orb from 360
            months_since_conjunction = int((360 - current_jupiter_pof_diff) / 2.5)
        
        # Ensure we're looking back far enough (Jupiter's cycle is about 12 years)
        months_since_conjunction = min(months_since_conjunction, 12 * 12)  # Cap at 12 years
        months_since_conjunction = max(months_since_conjunction, 1)  # At least 1 month back
        
        # Start search from estimated last conjunction
        estimated_date = today - timedelta(days=months_since_conjunction * 30)
        search_start = estimated_date - timedelta(days=90)  # Look 3 months before estimate
        search_end = estimated_date + timedelta(days=90)    # Look 3 months after estimate
        
        logger.info(f"Estimated last conjunction around {estimated_date}, searching from {search_start} to {search_end}")
        
        last_conjunction = None
        closest_orb = float('inf')
        
        # Search bi-weekly (every 14 days) around the estimated date - look for closest orb
        current_date = search_start
        while current_date <= search_end and current_date <= today:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Get Jupiter's position for this date
            current_transit = await chart_creator.create_transit_chart(
                transit_year=current_date.year,
                transit_month=current_date.month,
                transit_day=current_date.day,
                transit_hour=data.transit_hour,
                transit_minute=data.transit_minute,
                zodiac_type=data.zodiac_type,
                sidereal_mode=data.sidereal_mode
            )
            current_transit = json.loads(current_transit)
            
            jupiter_pos = current_transit["transit"]["subject"]["planets"]["jupiter"]["abs_pos"]
            
            # Calculate orb to POF (shortest angular distance)
            jupiter_pof_diff = min(
                abs(jupiter_pos - pof_pos),
                abs(jupiter_pos - pof_pos - 360),
                abs(jupiter_pos - pof_pos + 360)
            )
            
            # If this is closer than our current closest, update
            if jupiter_pof_diff < closest_orb:
                closest_orb = jupiter_pof_diff
                last_conjunction = {
                    "date": date_str,
                    "jupiter_position": jupiter_pos,
                    "pof_position": pof_pos,
                    "orb": round(jupiter_pof_diff, 6),
                    "sign": signs[int(jupiter_pos / 30)],
                    "is_current_cycle": True
                }
            
            # Move forward two weeks (14 days)
            current_date += timedelta(days=14)
        
        # Add current position and last conjunction to response
        response["jupiter_pof_history"] = {
            "current_position": {
                "date": today.strftime("%Y-%m-%d"),
                "jupiter_position": current_jupiter_pos,
                "pof_position": pof_pos,
                "orb": round(current_jupiter_pof_diff, 6),
                "sign": signs[int(current_jupiter_pos / 30)]
            },
            "last_conjunction": last_conjunction,
            "search_period": {
                "start": search_start.strftime("%Y-%m-%d"),
                "end": min(search_end, today).strftime("%Y-%m-%d")
            }
        }
        
        # Estimate next Jupiter-POF conjunction
        # Jupiter cycle is approx 11.86 years
        if last_conjunction:
            # Parse the last conjunction date
            last_conjunction_date = datetime.strptime(last_conjunction["date"], "%Y-%m-%d")
            
            # Add about 12 years to get the estimated next conjunction date
            # The exact orbital period of Jupiter is 11.86 years
            estimated_next_date = last_conjunction_date + timedelta(days=int(365.25 * 11.86))
            
            logger.info(f"Starting next conjunction search around {estimated_next_date}")
            
            # For a comprehensive search, check a wider window around the estimated date
            # Jupiter can have some variation in its orbit, so we'll search a full year
            next_search_start = estimated_next_date - timedelta(days=180)
            next_search_end = estimated_next_date + timedelta(days=180)
            
            # Set up for tracking the closest approach
            next_conjunction = None
            closest_orb = float('inf')
            
            # Track dates when Jupiter is within 1 degree orb
            within_orb_dates = []
            
            # Search monthly first to find the approximate conjunction period
            current_date = next_search_start
            conjunction_month_found = False
            
            while current_date <= next_search_end:
                date_str = current_date.strftime("%Y-%m-%d")
                
                # Get Jupiter's position for this date
                current_transit = await chart_creator.create_transit_chart(
                    transit_year=current_date.year,
                    transit_month=current_date.month,
                    transit_day=current_date.day,
                    transit_hour=data.transit_hour,
                    transit_minute=data.transit_minute,
                    zodiac_type=data.zodiac_type,
                    sidereal_mode=data.sidereal_mode
                )
                current_transit = json.loads(current_transit)
                jupiter_pos = current_transit["transit"]["subject"]["planets"]["jupiter"]["abs_pos"]
                
                # Calculate orb to POF (shortest angular distance)
                jupiter_pof_diff = min(
                    abs(jupiter_pos - pof_pos),
                    abs(jupiter_pos - pof_pos - 360),
                    abs(jupiter_pos - pof_pos + 360)
                )
                
                # If we find a close approach (< 5 degrees), mark this month as containing the conjunction
                if jupiter_pof_diff < 5.0:
                    conjunction_month_found = True
                    logger.info(f"Found potential conjunction month: {current_date.year}-{current_date.month} with orb: {jupiter_pof_diff}")
                    
                    # Do a more targeted search within this time period using biweekly intervals
                    # Start from beginning of month and go to end of next month to ensure coverage
                    fine_search_start = datetime(current_date.year, current_date.month, 1)
                    if current_date.month == 12:
                        fine_search_end = datetime(current_date.year + 1, 2, 1)
                    else:
                        fine_search_end = datetime(current_date.year, min(current_date.month + 2, 12), 1)
                    
                    # Make sure we don't go beyond our overall search window
                    if fine_search_end > next_search_end:
                        fine_search_end = next_search_end
                    
                    # Search every two weeks within this period
                    fine_date = fine_search_start
                    while fine_date <= fine_search_end:
                        fine_date_str = fine_date.strftime("%Y-%m-%d")
                        
                        current_transit = await chart_creator.create_transit_chart(
                            transit_year=fine_date.year,
                            transit_month=fine_date.month,
                            transit_day=fine_date.day,
                            transit_hour=data.transit_hour,
                            transit_minute=data.transit_minute,
                            zodiac_type=data.zodiac_type,
                            sidereal_mode=data.sidereal_mode
                        )
                        current_transit = json.loads(current_transit)
                        fine_jupiter_pos = current_transit["transit"]["subject"]["planets"]["jupiter"]["abs_pos"]
                        
                        fine_jupiter_pof_diff = min(
                            abs(fine_jupiter_pos - pof_pos),
                            abs(fine_jupiter_pos - pof_pos - 360),
                            abs(fine_jupiter_pos - pof_pos + 360)
                        )
                        
                        # If this is closer than our current closest, update
                        if fine_jupiter_pof_diff < closest_orb:
                            closest_orb = fine_jupiter_pof_diff
                            next_conjunction = {
                                "date": fine_date_str,
                                "jupiter_position": fine_jupiter_pos,
                                "pof_position": pof_pos,
                                "orb": round(fine_jupiter_pof_diff, 6),
                                "sign": signs[int(fine_jupiter_pos / 30)],
                                "is_current_cycle": False
                            }
                        
                        # Track dates when Jupiter is within 1 degree orb
                        if fine_jupiter_pof_diff <= 1.0:
                            within_orb_dates.append({
                                "date": fine_date_str,
                                "orb": round(fine_jupiter_pof_diff, 6)
                            })
                        
                        # Move forward with biweekly intervals (14 days)
                        fine_date += timedelta(days=14)
                    
                    # If we found a good conjunction, no need to continue searching
                    if closest_orb < 2.0:
                        break
                
                # If conjunction month found, no need to continue monthly search
                if conjunction_month_found:
                    break
                
                # Move forward one month
                if current_date.month == 12:
                    current_date = datetime(current_date.year + 1, 1, 1)
                else:
                    current_date = datetime(current_date.year, current_date.month + 1, 1)
            
            # If we didn't find a close conjunction, do a broader search with weekly intervals
            if not conjunction_month_found or (next_conjunction and next_conjunction["orb"] > 5.0):
                logger.warning("No close conjunction found in monthly search, performing weekly search")
                current_date = next_search_start
                while current_date <= next_search_end:
                    date_str = current_date.strftime("%Y-%m-%d")
                    
                    # Get Jupiter's position for this date
                    current_transit = await chart_creator.create_transit_chart(
                        transit_year=current_date.year,
                        transit_month=current_date.month,
                        transit_day=current_date.day,
                        transit_hour=data.transit_hour,
                        transit_minute=data.transit_minute,
                        zodiac_type=data.zodiac_type,
                        sidereal_mode=data.sidereal_mode
                    )
                    current_transit = json.loads(current_transit)
                    jupiter_pos = current_transit["transit"]["subject"]["planets"]["jupiter"]["abs_pos"]

                    
                    # Calculate orb to POF (shortest angular distance)
                    jupiter_pof_diff = min(
                        abs(jupiter_pos - pof_pos),
                        abs(jupiter_pos - pof_pos - 360),
                        abs(jupiter_pos - pof_pos + 360)
                    )
                    
                    # If this is closer than our current closest, update
                    if jupiter_pof_diff < closest_orb:
                        closest_orb = jupiter_pof_diff
                        next_conjunction = {
                            "date": date_str,
                            "jupiter_position": jupiter_pos,
                            "pof_position": pof_pos,
                            "orb": round(jupiter_pof_diff, 6),
                            "sign": signs[int(jupiter_pos / 30)],
                            "is_current_cycle": False
                        }
                    
                    # Move forward one week
                    current_date += timedelta(days=7)
            
            # If we still don't have a conjunction with orb < 10 degrees, it's not a true conjunction
            # Return null or only return it if it's within some reasonable orb
            if next_conjunction and next_conjunction["orb"] <= 10.0:
                # Add next conjunction to response
                response["jupiter_pof_history"]["next_conjunction"] = next_conjunction
                
                # Add date range when Jupiter is within 1 degree orb
                if within_orb_dates:
                    first_date = within_orb_dates[0]["date"]
                    last_date = within_orb_dates[-1]["date"]
                    
                    response["jupiter_pof_history"]["within_1_degree_orb"] = {
                        "start_date": first_date,
                        "end_date": last_date,
                        "detailed_dates": within_orb_dates
                    }
                
                # Always calculate estimated date range when Jupiter will be within 1 degree orb
                # This is more precise than just using the biweekly sample points
                if next_conjunction["orb"] <= 5.0:  # Only provide estimates for reasonably close conjunctions
                    # Jupiter moves approximately 0.08 degrees per day on average
                    jupiter_daily_motion = 0.08
                    
                    # Calculate how many days before and after the conjunction Jupiter will be within 1 degree orb
                    # For a total 2 degree window (±1 degree from exact conjunction)
                    days_in_orb = int(2.0 / jupiter_daily_motion)  # Total days within 1 degree orb
                    
                    # If conjunction is already within 1 degree, adjust calculation
                    if next_conjunction["orb"] < 1.0:
                        # Calculate days from current orb to 1 degree
                        days_to_edge = int((1.0 - next_conjunction["orb"]) / jupiter_daily_motion)
                        # Days before = days to get from current orb to exact, plus days to get to 1 degree on other side
                        days_before = int(next_conjunction["orb"] / jupiter_daily_motion)
                        days_after = days_to_edge + days_before
                    else:
                        # Calculate days until exact conjunction
                        days_to_exact = int(next_conjunction["orb"] / jupiter_daily_motion)
                        # Days before conjunction = days to reach exact - days from 1 degree to exact
                        days_before = max(0, days_to_exact - int(1.0 / jupiter_daily_motion))
                        # Days after conjunction = total days in orb - days before
                        days_after = days_in_orb - days_before
                    
                    # Calculate the date range
                    conjunction_date = datetime.strptime(next_conjunction["date"], "%Y-%m-%d")
                    estimated_start_date = conjunction_date - timedelta(days=days_before)
                    estimated_end_date = conjunction_date + timedelta(days=days_after)
                    
                    # Format dates as strings
                    start_date_str = estimated_start_date.strftime("%Y-%m-%d")
                    end_date_str = estimated_end_date.strftime("%Y-%m-%d")
                    
                    # Add estimated range to response
                    response["jupiter_pof_history"]["estimated_within_1_degree_orb"] = {
                        "start_date": start_date_str,
                        "end_date": end_date_str,
                        "total_days": days_in_orb,
                        "before_exact_days": days_before,
                        "after_exact_days": days_after,
                        "note": "Estimated range based on average Jupiter motion of 0.08° per day"
                    }
                    
                    # Find dates within this range when the Moon forms specific aspects to the conjunction point
                    # These aspects are considered especially lucky: 0° (conjunction), 180° (opposition), 
                    # 120° (trine), 90° (square), 60° (sextile), 45° (semi-square)
                    lucky_moon_aspects = []
                    
                    # Define the aspects to check and their orbs
                    aspects_to_check = [
                        {
                            "name": "conjunction",
                            "angle": 0,
                            "orb": 2.0,
                            "interpretation": "Highly auspicious day for spiritual practices and important beginnings",
                            "strength": "Very Strong"
                        },
                        {
                            "name": "trine",
                            "angle": 120,
                            "orb": 2.0,
                            "interpretation": "Favorable flow of spiritual energy and opportunities",
                            "strength": "Strong"
                        },
                        {
                            "name": "sextile",
                            "angle": 60,
                            "orb": 2.0,
                            "interpretation": "Beneficial opportunities for spiritual growth",
                            "strength": "Moderate"
                        },
                        {
                            "name": "opposition",
                            "angle": 180,
                            "orb": 2.0,
                            "interpretation": "Significant awareness and potential for spiritual breakthrough",
                            "strength": "Strong but Challenging"
                        },
                        {
                            "name": "square",
                            "angle": 90,
                            "orb": 2.0,
                            "interpretation": "Dynamic period for spiritual growth through overcoming challenges",
                            "strength": "Moderate but Challenging"
                        }
                    ]
                    
                    # The conjunction point is the POF position
                    conjunction_point = pof_pos
                    
                    # Check each day in the estimated range
                    check_date = estimated_start_date
                    while check_date <= estimated_end_date:
                        check_date_str = check_date.strftime("%Y-%m-%d")
                        
                        # Get Moon's position for this date
                        current_transit = await chart_creator.create_transit_chart(
                            transit_year=check_date.year,
                            transit_month=check_date.month,
                            transit_day=check_date.day,
                            transit_hour=data.transit_hour,
                            transit_minute=data.transit_minute,
                            zodiac_type=data.zodiac_type,
                            sidereal_mode=data.sidereal_mode
                        )
                        current_transit = json.loads(current_transit)
                        moon_pos = current_transit["transit"]["subject"]["planets"]["moon"]["abs_pos"]
                        
                        # Check for each aspect
                        for aspect in aspects_to_check:
                            # Calculate the angular difference
                            angle_diff = abs(moon_pos - conjunction_point) % 360
                            if angle_diff > 180:
                                angle_diff = 360 - angle_diff
                            
                            # Check if it's within orb of the aspect
                            aspect_orb = abs(angle_diff - aspect["angle"])
                            if aspect_orb <= aspect["orb"]:
                                # This is a matching aspect
                                lucky_moon_aspects.append({
                                    "date": check_date_str,
                                    "aspect": aspect["name"],
                                    "aspect_angle": aspect["angle"],
                                    "moon_position": moon_pos,
                                    "conjunction_point": conjunction_point,
                                    "orb": round(aspect_orb, 2)
                                })
                                # No need to check other aspects for this day
                                break
                        
                        # Move to next day
                        check_date += timedelta(days=1)
                    
                    # Add the lucky Moon aspect dates to the response
                    if lucky_moon_aspects:
                        response["jupiter_pof_history"]["lucky_moon_aspects"] = {
                            "explanation": "Dates when the Moon forms specific aspects to the Jupiter-POF conjunction point, considered especially lucky",
                            "dates": lucky_moon_aspects
                        }
                
                response["jupiter_pof_history"]["next_search_period"] = {
                    "start": next_search_start.strftime("%Y-%m-%d"),
                    "end": next_search_end.strftime("%Y-%m-%d")
                }
            else:
                logger.warning(f"No true conjunction found within the search period. Closest orb: {closest_orb if next_conjunction else 'N/A'}")
                # Don't add a "next_conjunction" field if we don't have a real conjunction
        
        # Save to PocketBase
        pb_service = PocketbaseService()
        record = pb_service.create_lucky_times_record(
            planets_data=planets_data,
            pof_data=pof_data,
            lucky_times_data=response,
            user_id=data.user_id,
            job_id=data.job_id
        )
        
        # Add record to response
        response["record"] = record
        
        return response
        
    except Exception as e:
        logger.error(f"Error calculating lucky times: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/charts/vedic-lucky-times")
async def get_vedic_lucky_times(data: VedicLuckyTimesRequest):
    try:
        print("get_vedic_lucky_times")
        print("Data Received:")
        print(data)
        # Create chart creator
        chart_creator = ChartCreator(
            name=data.name,
            year=data.year,
            month=data.month,
            day=data.day,
            hour=data.hour,
            minute=data.minute,
            city=data.city,
            nation=data.nation,
            zodiac_type=data.zodiac_type,
            sidereal_mode=data.sidereal_mode
        )
        
        # Get natal chart data
        natal_data = json.loads(chart_creator.get_chart_data_as_json())
        
        # Get current positions
        today = datetime.now()
        try:
            current_transit = await chart_creator.create_transit_chart(
                transit_year=today.year,
                transit_month=today.month,
                transit_day=today.day,
                transit_hour=data.transit_hour,
                transit_minute=data.transit_minute,
                zodiac_type=data.zodiac_type,
                sidereal_mode=data.sidereal_mode
            )
            current_transit = json.loads(current_transit)
        except Exception as transit_error:
            logger.error(f"Error getting transit chart: {str(transit_error)}")
            # Provide a partial response without transit data
            return {
                "error": f"Could not calculate transit data: {str(transit_error)}",
                "natal_data": natal_data,
                "person_name": data.name,
                "partial_response": True
            }
        
        # Create birth date string
        birth_date = f"{data.year}-{data.month}-{data.day}"
        
        # Use the Vedic Lucky Times Service
        try:
            service = VedicLuckyTimesService()
            
            # Check if location-specific calculations are requested
            if data.current_city and data.current_nation:
                # Check if current location is different from birth location
                location_changed = (data.current_city != data.city) or (data.current_nation != data.nation)
                
                if location_changed:
                    # Create a separate chart creator for the current location
                    location_chart_creator = ChartCreator(
                        name=data.name,
                        year=data.year,
                        month=data.month,
                        day=data.day,
                        hour=data.hour,
                        minute=data.minute,
                        city=data.current_city,  # Use current location
                        nation=data.current_nation,  # Use current location
                        zodiac_type=data.zodiac_type,
                        sidereal_mode=data.sidereal_mode
                    )
                    
                    # Get transit chart for current location
                    today = datetime.now()
                    location_transit = await location_chart_creator.create_transit_chart(
                        transit_year=today.year,
                        transit_month=today.month,
                        transit_day=today.day,
                        transit_hour=data.transit_hour,
                        transit_minute=data.transit_minute,
                        zodiac_type=data.zodiac_type,
                        sidereal_mode=data.sidereal_mode
                    )
                    location_transit = json.loads(location_transit)
                    
                    # Log the fact that we're using a location-specific transit chart
                    logger.info(f"Created location-specific transit chart for {data.current_city}, {data.current_nation}")
                else:
                    # If locations are the same, reuse the existing transit chart
                    location_transit = current_transit
                    logger.info("Current location is same as birth location, reusing transit chart")
                
                # Get location-specific Yogi point alignments with the location-specific transit
                location_specific_alignments = service.calculate_location_specific_yogi_alignments(
                    natal_data=natal_data,
                    current_city=data.current_city,
                    current_nation=data.current_nation,
                    orb=data.orb,
                    transit_data=location_transit  # Pass the location-specific transit data
                )
                
                # Process standard Vedic lucky times, passing in the location_specific_alignments
                response = service.process_vedic_lucky_times(
                    natal_data=natal_data,
                    transit_data=current_transit,  # Still use original transit for standard calculations
                    birth_date=birth_date,
                    from_date=data.from_date,
                    name=data.name,
                    orb=data.orb,
                    location_specific_alignments=location_specific_alignments
                )
            else:
                # Just process standard Vedic lucky times without location-specific alignments
                response = service.process_vedic_lucky_times(
                    natal_data=natal_data,
                    transit_data=current_transit,
                    birth_date=birth_date,
                    from_date=data.from_date,
                    name=data.name,
                    orb=data.orb  # Pass the orb parameter
                )
                
        except Exception as service_error:
            logger.error(f"Error in VedicLuckyTimesService: {str(service_error)}")
            # Create basic response with just natal data
            return {
                "error": f"Error calculating Vedic lucky times: {str(service_error)}",
                "natal_data": natal_data,
                "transit_data_available": True,
                "service_error": True,
                "person_name": data.name
            }
        
        # Save to PocketBase
        try:
            pb_service = PocketbaseService()
            
            # Convert any datetime objects to strings before saving to PocketBase
            def convert_datetime_to_str(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, datetime):
                            obj[key] = value.isoformat()
                        elif isinstance(value, dict):
                            convert_datetime_to_str(value)
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    convert_datetime_to_str(item)
                return obj
            
            # Create a copy of the response to avoid modifying the original
            pb_response = convert_datetime_to_str(dict(response))
            
            record = pb_service.create_vedic_lucky_times_record(
                natal_data=natal_data,
                yogi_point_data=pb_response,
                user_id=data.user_id,
                job_id=data.job_id
            )
            # response["record"] = record
        except Exception as pb_error:
            logger.error(f"PocketBase error: {str(pb_error)}")
            # Add error to response but still return the calculated data
            response["pocketbase_error"] = str(pb_error)
        
        return response
        
    except Exception as e:
        # Log detailed error with traceback
        logger.error(f"Error calculating Vedic lucky times: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/charts/next-venus-aspects")
async def get_next_venus_aspects(data: VedicLuckyTimesRequest):
    try:
        # Create chart creator
        chart_creator = ChartCreator(
            name=data.name,
            year=data.year,
            month=data.month,
            day=data.day,
            hour=data.hour,
            minute=data.minute,
            city=data.city,
            nation=data.nation,
            zodiac_type=data.zodiac_type,
            sidereal_mode=data.sidereal_mode
        )
        
        # Get natal chart data
        natal_data = json.loads(chart_creator.get_chart_data_as_json())
        
        # Get current positions
        today = datetime.now()
        current_transit = await chart_creator.create_transit_chart(
            transit_year=today.year,
            transit_month=today.month,
            transit_day=today.day,
            transit_hour=data.transit_hour,
            transit_minute=data.transit_minute
        )
        current_transit = json.loads(current_transit)
        
        # Use the Vedic Lucky Times Service to process Venus aspects
        service = VedicLuckyTimesService()
        response = service.get_next_venus_aspects(
            natal_data=natal_data,
            transit_data=current_transit,
            orb=data.orb
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error calculating Venus aspects to Yogi Point: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def normalize_degrees(deg):
    """Normalize degrees to 0-360 range"""
    return deg % 360

def calculate_aspect_difference(pos1, pos2):
    """Calculate the smallest angle between two positions"""
    diff = abs(pos1 - pos2)
    if diff > 180:
        diff = 360 - diff
    return diff

def check_aspect_to_yogi_point(transit_pos, yogi_point_pos, orb=3.0):
    """Check if a transit position makes an aspect to the Yogi Point
    
    Args:
        transit_pos (float): Transit position in degrees
        yogi_point_pos (float): Yogi Point position in degrees
        orb (float): Maximum orb in degrees
        
    Returns:
        tuple: (bool, str, float) - (has_aspect, aspect_type, orb)
    """
    # Normalize positions to 0-360
    transit_pos = normalize_degrees(transit_pos)
    yogi_point_pos = normalize_degrees(yogi_point_pos)
    
    # Define aspects to check
    aspects = {
        'conjunction': 0,
        'opposition': 180,
        'trine': 120,
        'sextile': 60,
        'square': 90
    }
    
    # Calculate angular difference
    diff = calculate_aspect_difference(transit_pos, yogi_point_pos)
    
    # Check each aspect
    for aspect_name, aspect_angle in aspects.items():
        aspect_diff = abs(diff - aspect_angle)
        if aspect_diff <= orb:
            return True, aspect_name, aspect_diff
            
    return False, None, None