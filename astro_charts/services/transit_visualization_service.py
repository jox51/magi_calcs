import altair as alt
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
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
        logger.info(f"Dataframe Monthly Chart: {df}")
        
         # Create watermark
        watermark = alt.Chart(pd.DataFrame({'text': ['Magi Maps']})).mark_text(
        align='right',
        baseline='bottom',
        fontSize=14,
            opacity=0.3,
            color='gray',
            dx=-10,  # Offset from right
            dy=-10   # Offset from bottom
        ).encode(
            text='text:N'
        ).properties(
            width=400,
            height=300
        )
        
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
            width=400,
            height=300,
            title=f'{subject_name} - Transit Aspects ({month_year})'
        ) + watermark

    def create_yearly_chart(self, df: pd.DataFrame, subject_name: str) -> alt.Chart:
        """Create a chart for the full year overview"""
        # Get the year range for the title
        start_date = df['date'].min()
        end_date = df['date'].max()
        date_range = f"({start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')})"
        
        watermark = alt.Chart(pd.DataFrame({'text': ['Magi Maps']})).mark_text(
            align='right',
            baseline='bottom',
            fontSize=14,
            opacity=0.3,
            color='gray',
            dx=-10,
            dy=-10
        ).encode(
            text='text:N'
        )
        
        chart = alt.Chart(df).mark_bar(
            size=20
        ).encode(
            x=alt.X('utcyearmonthdate(date):T',
                   title='Date',
                   axis=alt.Axis(
                       format='%b %d',
                       labelAngle=-45
                   ),
                   scale=alt.Scale(
                       nice=False,
                       padding=10  # Add padding to prevent bars from extending past limits
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
            width=500,  # Wider width for yearly overview
            height=300,
            title=f'{subject_name} - Transit Aspects {date_range}'
        ) + watermark
        
        return chart

    def create_visualization(
        self, 
        transit_data: Dict[str, Any], 
        output_path: str,
        html_path: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Create and save visualizations of transit aspects over time"""
        try:
            # Prepare the data
            df = self.prepare_data(transit_data)
            
            if df.empty:
                logger.warning("No aspect data found, creating empty visualization")
                return None, None
            
            # Get subject name
            daily_aspects = transit_data.get('daily_aspects', {})
            first_date = list(daily_aspects.keys())[0]
            subject_name = daily_aspects[first_date]['natal']['name']
            
            # Create yearly overview chart
            yearly_chart = self.create_yearly_chart(df, subject_name)
            
            # Split data into monthly chunks and create monthly charts
            monthly_dfs = self._split_into_monthly_chunks(df)
            monthly_charts = [self.create_monthly_chart(month_df, subject_name) 
                            for month_df in monthly_dfs]
            
            # Combine all charts vertically
            all_charts = yearly_chart & alt.vconcat(*monthly_charts)
            
            # Save both SVG and HTML versions
            all_charts.save(output_path)
            all_charts.save(html_path)
            
            logger.info(f"Successfully saved visualizations to {output_path} and {html_path}")
            return output_path, html_path
                
        except Exception as e:
            logger.error(f"Error creating transit visualization: {str(e)}")
            return None, None