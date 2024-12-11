from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
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

class TransitChartRequest(BaseModel):
    birth_data: BaseBirthData
    transit_data: TransitDateData


@app.post("/charts/natal")
async def create_natal_chart(data: BaseBirthData):
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
            nation=data.nation
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
    try:
        chart_creator = ChartCreator(
            name=request.birth_data.name,
            year=request.birth_data.year,
            month=request.birth_data.month,
            day=request.birth_data.day,
            hour=request.birth_data.hour,
            minute=request.birth_data.minute,
            city=request.birth_data.city,
            nation=request.birth_data.nation
        )
        
        # Get chart data and generate chart
        chart_data = await chart_creator.create_transit_chart(
            transit_year=request.transit_data.transit_year,
            transit_month=request.transit_data.transit_month,
            transit_day=request.transit_data.transit_day,
            transit_hour=request.transit_data.transit_hour,
            transit_minute=request.transit_data.transit_minute
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
        viz_service = TransitVisualizationService()
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
    try:
        chart_creator = ChartCreator(
            name=request.name,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            city=request.city,
            nation=request.nation
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
        viz_service = TransitVisualizationService()
        try:
            viz_chart_path = viz_service.create_visualization(results, viz_path)
        except Exception as viz_error:
            logger.error(f"Visualization error: {str(viz_error)}")
            viz_chart_path = None  # Continue even if visualization fails

        # Save to PocketBase
        try:
            pb_service = PocketbaseService()
            record = pb_service.create_transit_loop_charts(
                transit_loop_data={
                    "natal": results.get("natal", {}),
                    "transit_data": results,
                    "visualization_path": viz_chart_path,
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
    filter_aspects: Optional[List[str]] = None
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
        filter_planets=filter_planets
    )
    
    result = await create_transit_loop(request)
    return result.get("chart_data", {})

# Initialize new marriage finder
alt_marriage_finder = AltMarriageDateFinder(transit_loop_wrapper)

@app.post("/charts/synastry")
async def create_synastry_chart(request: SynastryRequest):
    try:
        chart_creator = ChartCreator(
            name=request.name,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            city=request.city,
            nation=request.nation
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