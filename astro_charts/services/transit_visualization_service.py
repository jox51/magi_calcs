import altair as alt
import pandas as pd
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TransitVisualizationService:
    """Service for creating visualizations of transit aspect data"""
    
    def __init__(self):
        """Initialize the visualization service with color schemes and settings"""
        self.colors = {
            'Cinderella': '#0000FF',  # Blue
            'Super': '#FF0000',       # Red
            'Turbulent': '#000000'    # Black
        }
        
        # Configure Altair settings
        alt.data_transformers.disable_max_rows()
    
    def prepare_data(self, transit_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Transform transit data into a pandas DataFrame suitable for visualization
        
        Args:
            transit_data: Dictionary containing transit data by date
            
        Returns:
            DataFrame with columns: date, type, count
        """
        records = []
        
        for date_str, data in transit_data.items():
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Count aspects by type
            cinderella_count = len(data.get('transit', {}).get('cinderella_aspects', []))
            super_count = len(data.get('transit', {}).get('transit_super_aspects', []))
            # Update to look for turbulent_transits inside transit data
            turbulent_count = len(data.get('transit', {}).get('turbulent_transits', []))
            
            # Add records for each aspect type that has occurrences
            if cinderella_count > 0:
                records.append({
                    'date': date,
                    'type': 'Cinderella',
                    'count': cinderella_count
                })
            if super_count > 0:
                records.append({
                    'date': date,
                    'type': 'Super',
                    'count': super_count
                })
            if turbulent_count > 0:
                records.append({
                    'date': date,
                    'type': 'Turbulent',
                    'count': turbulent_count
                })
        
        return pd.DataFrame(records)

    def create_visualization(self, transit_data: Dict[str, Any], output_path: str) -> str:
        """
        Create and save a visualization of transit aspects over time
        
        Args:
            transit_data: Dictionary containing transit data by date
            output_path: Path where the visualization should be saved
            
        Returns:
            Path to the saved visualization file
        """
        try:
            # Prepare the data
            df = self.prepare_data(transit_data)
            
            if df.empty:
                logger.warning("No aspect data found for visualization")
                return None
            
            # Get subject name from the first date's natal data
            first_date = list(transit_data.keys())[0]
            subject_name = transit_data[first_date]['natal']['name']
            
            # Create the chart with personalized title
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('date:T', 
                       title='Date',
                       axis=alt.Axis(format='%Y-%m-%d')),
                y=alt.Y('count:Q',
                       title='Number of Aspects',
                       stack='zero'),
                color=alt.Color('type:N',
                              scale=alt.Scale(domain=list(self.colors.keys()),
                                            range=list(self.colors.values())),
                              legend=alt.Legend(title='Aspect Type')),
                tooltip=[
                    alt.Tooltip('date:T', title='Date', format='%Y-%m-%d'),
                    alt.Tooltip('type:N', title='Aspect Type'),
                    alt.Tooltip('count:Q', title='Number of Aspects')
                ]
            ).properties(
                width=800,
                height=400,
                title=f'{subject_name} - Transit Aspects Over Time'
            )
            
            # Save the chart
            chart.save(output_path)
            logger.info(f"Transit visualization saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating transit visualization: {str(e)}")
            raise