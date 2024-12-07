from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from astro_charts.chart_creator import ChartCreator
import json
import logging
from dotenv import load_dotenv
from astro_charts.services.pocketbase_service import PocketbaseService
import os
import shutil
from astro_charts.services.transit_visualization_service import TransitVisualizationService

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
        
        # Save to PocketBase
        pb_service = PocketbaseService()
        record = pb_service.create_natal_chart(
            natal_data=chart_data,
            chart_path=final_chart_path,
            user_id=data.user_id,
            job_id=data.job_id
        )
        
        # Return the data including the PocketBase record
        return {
            "chart_data": chart_data,
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
        chart_data = chart_creator.create_transit_chart(
            transit_year=request.transit_data.transit_year,
            transit_month=request.transit_data.transit_month,
            transit_day=request.transit_data.transit_day,
            transit_hour=request.transit_data.transit_hour,
            transit_minute=request.transit_data.transit_minute
        )
        
        # Parse chart data
        chart_data = json.loads(chart_data)
        
        # Construct the file path where the chart was moved
        name_safe = request.birth_data.name.replace(" ", "_")
        transit_date = f"{request.transit_data.transit_year}_{request.transit_data.transit_month}_{request.transit_data.transit_day}"
        final_chart_path = os.path.join('charts', f"{name_safe}_transit_chart.svg")
        
        logger.info(f"Using final chart path: {os.path.abspath(final_chart_path)}")
        
        # Verify file exists
        if not os.path.exists(final_chart_path):
            raise FileNotFoundError(f"Transit chart file not found at {final_chart_path}")
        
        # Save to PocketBase using the existing single transit chart method
        pb_service = PocketbaseService()
        record = pb_service.create_single_transit_chart(
            transit_data=chart_data,
            chart_path=final_chart_path,  # Add chart_path parameter
            user_id=request.birth_data.user_id,
            job_id=request.birth_data.job_id
        )
        
        # Return both chart data and PocketBase record
        return {
            "chart_data": chart_data,
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
        results = chart_creator.create_transit_loop(
            from_date=request.from_date,
            to_date=request.to_date,
            generate_chart=request.generate_chart,
            aspects_only=request.aspects_only,
            filter_orb=request.filter_orb,
            filter_aspects=request.filter_aspects,
            filter_planets=request.filter_planets
        )

        # Create visualization
        name_safe = request.name.replace(" ", "_")
        viz_path = os.path.join('charts', f"{name_safe}_transit_loop_viz.html")
        
        viz_service = TransitVisualizationService()
        viz_chart_path = viz_service.create_visualization(results, viz_path)

        if viz_chart_path:
            logger.info(f"Created visualization at {viz_chart_path}")
        
        # Save to PocketBase
        pb_service = PocketbaseService()
        record = pb_service.create_transit_loop_charts(
            transit_loop_data=results,
            user_id=request.user_id,
            job_id=request.job_id
        )

        # Return results with visualization path and PocketBase record
        return {
            "chart_data": results,
            "visualization_path": viz_chart_path if viz_chart_path else None,
            "record": record
        }

    except Exception as e:
        logger.error(f"Error creating transit loop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        
        # Construct the file path where the chart was moved
        name_safe = f"{request.name}_{request.name2}".replace(" ", "_")
        final_chart_path = os.path.join('charts', f"{name_safe}_synastry.svg")
        
        logger.info(f"Using final chart path: {os.path.abspath(final_chart_path)}")
        
        # Verify file exists
        if not os.path.exists(final_chart_path):
            raise FileNotFoundError(f"Synastry chart file not found at {final_chart_path}")
        
        # Save to PocketBase
        pb_service = PocketbaseService()
        record = pb_service.create_synastry_chart(
            synastry_data=chart_data,
            chart_path=final_chart_path,
            user_id=request.user_id,
            job_id=request.job_id
        )
        
        # Return both chart data and PocketBase record
        return {
            "chart_data": chart_data,
            "record": record
        }
        
    except Exception as e:
        logger.error(f"Error creating synastry chart: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 