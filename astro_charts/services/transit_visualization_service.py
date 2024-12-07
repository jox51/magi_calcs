import altair as alt
import pandas as pd
from typing import Dict, Any, List
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
            'Cinderella': '#00FF00',  # Green
            'Super': '#0000FF',       # Blue
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
        # Get unique dates
        dates = sorted(set(transit_data.keys()))
        
        for date_str in dates:
            data = transit_data[date_str]
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Get transit data
            transit = data.get('transit', {})
            
            # Count aspects by type
            aspect_counts = {
                'Cinderella': len(transit.get('cinderella_aspects', [])),
                'Super': len(transit.get('transit_super_aspects', [])),
                'Turbulent': len(transit.get('turbulent_transits', []))
            }
            
            # Only add records for aspects that exist
            for aspect_type, count in aspect_counts.items():
                if count > 0:
                    records.append({
                        'date': date,
                        'type': aspect_type,
                        'count': count
                    })
        
        # Create DataFrame and ensure we have data
        if not records:
            return pd.DataFrame(columns=['date', 'type', 'count'])
            
        df = pd.DataFrame(records)
        
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
        Create and save visualizations of transit aspects over time, split by month
        """
        try:
            # Prepare the data
            df = self.prepare_data(transit_data)
            df['date'] = pd.to_datetime(df['date'])
            
            if df.empty:
                logger.warning("No aspect data found for visualization")
                return None
            
            # Get subject name
            first_date = list(transit_data.keys())[0]
            subject_name = transit_data[first_date]['natal']['name']
            
            # Split data into monthly chunks
            monthly_chunks = self._split_into_monthly_chunks(df)
            
            # Create a chart for each month
            charts = []
            for month_df in monthly_chunks:
                chart = self.create_monthly_chart(month_df, subject_name)
                charts.append(chart)
            
            # Vertically concatenate all charts
            final_chart = alt.vconcat(*charts)
            
            # Save the combined chart
            final_chart.save(output_path)
            return output_path
                
        except Exception as e:
            logger.error(f"Error creating transit visualization: {str(e)}")
            raise