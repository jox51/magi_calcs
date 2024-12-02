from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class TransitLoopService:
    def __init__(self, chart_creator):
        self.chart_creator = chart_creator

    def process_transit_loop(
        self,
        from_date: str,
        to_date: str,
        transit_hour: int,
        transit_minute: int
    ) -> Optional[Dict[str, Any]]:
        """
        Process transit charts for a date range
        
        Args:
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            transit_hour: Hour for transit calculations
            transit_minute: Minute for transit calculations
            
        Returns:
            List of transit chart data dictionaries
        """
        try:
            transit_data = []
            current_date = datetime.strptime(from_date, '%Y-%m-%d')
            end_date = datetime.strptime(to_date, '%Y-%m-%d')
            
            while current_date <= end_date:
                logger.info(f"Processing transit for {current_date.date()}")
                
                data = self.chart_creator.create_transit_chart(
                    transit_year=current_date.year,
                    transit_month=current_date.month,
                    transit_day=current_date.day,
                    transit_hour=transit_hour,
                    transit_minute=transit_minute
                )
                
                if data:  # Only append if we got valid data
                    # Parse the JSON string into a dictionary
                    chart_data = json.loads(data) if isinstance(data, str) else data
                    transit_data.append(chart_data)
                
                current_date += timedelta(days=1)
            
            logger.info(f"Processed {len(transit_data)} transit charts")
            
            if not transit_data:
                return None

            # Create the combined output structure
            output_data = {
                "natal": transit_data[0]["natal"],  # Use natal data from first chart
                "transit_loop": [
                    {
                        "date": chart["transit"]["subject"]["birth_data"]["date"],
                        "time": chart["transit"]["subject"]["birth_data"]["time"],
                        "planets": chart["transit"]["subject"]["planets"],
                        "transit_super_aspects": chart["transit"].get("transit_super_aspects", []),
                        "cinderella_aspects": chart["transit"].get("cinderella_aspects", [])
                    }
                    for chart in transit_data
                ],
                "natal_super_aspects": transit_data[0].get("natal_super_aspects", [])
            }
            
            # Print the formatted JSON to console
            print("\nTransit Chart Data:")
            print("==================")
            print(json.dumps(output_data, indent=2))
            
            return output_data
            
        except Exception as e:
            logger.error(f"Error in transit loop processing: {str(e)}")
            raise  # Re-raise the exception to handle it in the calling code 