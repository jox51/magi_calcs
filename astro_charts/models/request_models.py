from pydantic import BaseModel
from typing import Optional, List

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