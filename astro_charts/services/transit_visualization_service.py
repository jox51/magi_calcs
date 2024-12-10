import altair as alt
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

class TransitVisualizationService:
    """Service for creating visualizations of transit aspect data"""
    
    def __init__(self):
        """Initialize the visualization service with color schemes and settings"""
        self.colors = {
            'Cinderella': '#0000FF',  # Blue
            'Golden': '#FFD700',      # Gold
            'Turbulent': '#000000'    # Black
            #  'Super': '#0000FF',       # Blue

            # Removed Super aspects
        }
        
        # Configure Altair settings
        alt.data_transformers.disable_max_rows()
    
    def prepare_data(self, transit_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Transform transit data into a pandas DataFrame suitable for visualization
        """
        records = []
        
        # Get daily aspects from the nested structure
        daily_aspects = transit_data.get('daily_aspects', {})
        
        # Iterate through dates in daily_aspects
        for date_str, day_data in daily_aspects.items():
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                
                # Get transit data
                transit = day_data.get('transit', {})
                
                # Count aspects by type (including empty lists as 0)
                aspect_counts = {
                    'Cinderella': len(transit.get('cinderella_aspects', [])),
                    'Golden': len(transit.get('golden_transits', [])),  # Added Golden
                    'Turbulent': len(day_data.get('turbulent_transits', []))
                    # Removed Super aspects
                }
                
                # Add records for all types, even if count is 0
                for aspect_type, count in aspect_counts.items():
                    records.append({
                        'date': date,
                        'type': aspect_type,
                        'count': count
                    })
                        
            except ValueError as e:
                logger.error(f"Error parsing date {date_str}: {str(e)}")
                continue
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        if not df.empty:
            # Sort by date and type
            df = df.sort_values(['date', 'type'])
            
        return df

    def _split_into_monthly_chunks(self, df: pd.DataFrame) -> List[pd.DataFrame]:
        """Split dataframe into monthly chunks"""
        if df.empty:
            return [df]
        
        # Group by year and month
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        monthly_groups = [group for _, group in df.groupby('year_month')]
        
        # Drop the helper column
        for group in monthly_groups:
            group.drop('year_month', axis=1, inplace=True)
        
        return monthly_groups

    def create_monthly_chart(self, df: pd.DataFrame, subject_name: str) -> alt.Chart:
        """Create a chart for a single month of data"""
        # Get the month and year for the title
        first_date = df['date'].min()
        month_year = first_date.strftime('%B %Y')
        
        return alt.Chart(df).mark_bar(
            size=20
        ).encode(
            x=alt.X('utcyearmonthdate(date):T',
                   title='Date',
                   axis=alt.Axis(
                       format='%b %d',
                       labelAngle=0
                   ),
                   type='ordinal',  # Specify ordinal type
                   scale=alt.Scale(
                       nice=False
                   )),
            y=alt.Y('count:Q',
                   title='Number of Aspects',
                   scale=alt.Scale(
                       domain=[0, 10]
                   )),
            color=alt.Color('type:N',
                          scale=alt.Scale(
                              domain=list(self.colors.keys()),
                              range=list(self.colors.values())
                          ),
                          legend=alt.Legend(title='Aspect Type')),
            tooltip=[
                alt.Tooltip('utcyearmonthdate(date):T', title='Date', format='%b %d'),
                alt.Tooltip('type:N', title='Aspect Type'),
                alt.Tooltip('count:Q', title='Number of Aspects')
            ]
        ).properties(
            width=800,
            height=400,
            title=f'{subject_name} - Transit Aspects ({month_year})'
        )

    def create_visualization(self, transit_data: Dict[str, Any], output_path: str) -> str:
        """
        Create and save visualizations of transit aspects over time
        """
        try:
            # Prepare the data
            df = self.prepare_data(transit_data)
            
            # Even if no aspects found, create an empty visualization
            if df.empty:
                logger.warning("No aspect data found, creating empty visualization")
                
            # Get subject name from the first date's natal data
            daily_aspects = transit_data.get('daily_aspects', {})
            first_date = list(daily_aspects.keys())[0]
            subject_name = daily_aspects[first_date]['natal']['name']
            
            # Create the chart (will show empty if no data)
            chart = self.create_monthly_chart(df, subject_name)
            
            # Save the chart
            chart.save(output_path)
            
            return output_path
                
        except Exception as e:
            logger.error(f"Error creating transit visualization: {str(e)}")
            # Return a default path even if visualization fails
            return output_path