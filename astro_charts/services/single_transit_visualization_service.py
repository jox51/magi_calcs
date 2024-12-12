import altair as alt
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SingleTransitVisualizationService:
    """Service for creating visualizations of single transit chart data"""
    
    def __init__(self):
        """Initialize the visualization service with color schemes and settings"""
        self.colors = {
            'Cinderella': '#FF69B4',  # Pink
            'Golden': '#FFD700',      # Gold
            'Turbulent': '#FF4500'    # Red-Orange
        }
        
        # Configure Altair settings
        alt.data_transformers.disable_max_rows()
    
    def prepare_data(self, transit_data: Dict[str, Any]) -> pd.DataFrame:
        """Transform transit data into a pandas DataFrame suitable for visualization"""
        records = []
        
        try:
            # Get the transit date from the nested structure
            transit_date = (transit_data.get('transit', {})
                       .get('subject', {})
                       .get('birth_data', {})
                       .get('date'))
            
            if not transit_date:
                logger.error("No transit date found in nested data structure")
                return pd.DataFrame()
                
            date = datetime.strptime(transit_date, '%Y-%m-%d')
            
            # Count only Cinderella, Golden, and Turbulent aspects
            aspect_counts = {
                'Cinderella': len(transit_data.get('transit', {}).get('cinderella_aspects', [])),
                'Golden': len(transit_data.get('transit', {}).get('golden_transits', [])),
                'Turbulent': len(transit_data.get('transit', {}).get('turbulent_transits', []))
            }
            
            # Create records for each aspect type
            for aspect_type, count in aspect_counts.items():
                # Get the details of aspects for this type
                aspects_key = f"{aspect_type.lower()}_aspects"
                if aspect_type == 'Golden':
                    aspects_key = 'golden_transits'
                elif aspect_type == 'Turbulent':
                    aspects_key = 'turbulent_transits'
                    
                aspects = transit_data.get('transit', {}).get(aspects_key, [])
                
                # Create detail string for tooltip
                details = []
                for aspect in aspects:
                    if isinstance(aspect, dict):
                        if 'natal_planet' in aspect:  # Handle golden/turbulent transit format
                            detail = (
                                f"{aspect.get('natal_planet', '').title()}-"
                                f"{aspect.get('transit_planet', '').title()} "
                                f"({aspect.get('aspect_name', '').title()}, "
                                f"orbit: {round(aspect.get('orbit', 0), 4)}°)"
                            )
                        else:  # Handle regular aspect format
                            detail = (
                                f"{aspect.get('planet1_name', '').title()}-"
                                f"{aspect.get('planet2_name', '').title()} "
                                f"({aspect.get('aspect_name', '').title()}, "
                                f"orbit: {round(aspect.get('orbit', 0), 4)}°)"
                            )
                        details.append(detail)
            
                records.append({
                    'date': date,
                    'type': aspect_type,
                    'count': count,
                    'details': '\n'.join(details) if details else 'None'
                })
                
        except Exception as e:
            logger.error(f"Error preparing transit data: {str(e)}")
            return pd.DataFrame()
        
        return pd.DataFrame(records)

    def create_visualization(
        self, 
        transit_data: Dict[str, Any], 
        output_path: str,
        html_path: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Create and save visualization of single transit aspects"""
        try:
            # Prepare the data
            df = self.prepare_data(transit_data)
            
            if df.empty:
                logger.warning("No aspect data found for visualization")
                return None, None
            
            # Get subject name and transit date
            subject_name = transit_data.get('natal', {}).get('name', 'Unknown')
            transit_date = df['date'].iloc[0].strftime('%B %d, %Y')
            
            # Get the maximum count and create array of tick values
            max_count = max(df['count'])
            tick_values = list(range(0, max_count + 2))  # +2 to include max value and one above
            
            # Create the bar chart
            chart = alt.Chart(df).mark_bar(
                cornerRadius=6,
                width=40
            ).encode(
                x=alt.X('type:N',
                       title='Aspect Type',
                       sort=list(self.colors.keys())),
                y=alt.Y('count:Q',
                       title='Number of Aspects',
                       scale=alt.Scale(domain=[0, max_count + 1]),
                       axis=alt.Axis(
                           values=tick_values,  # Explicitly set tick values
                           grid=True
                       )),
                color=alt.Color('type:N',
                    scale=alt.Scale(
                        domain=list(self.colors.keys()),
                        range=list(self.colors.values())
                    ),
                    legend=None
                ),
                tooltip=[
                    alt.Tooltip('type:N', title='Aspect Type'),
                    alt.Tooltip('count:Q', title='Count', format='d'),
                    alt.Tooltip('details:N', title='Aspects')
                ]
            ).properties(
                width=400,
                height=300,
                title={
                    "text": [
                        f"{subject_name}",
                        f"Transit Aspects for {transit_date}"
                    ],
                    "color": "black",
                    "fontSize": 14,
                    "anchor": "middle"
                }
            )
            
            # Add text labels on top of bars
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5
            ).encode(
                text=alt.Text('count:Q', format='d')  # 'd' format for integers
            )
                    # Create watermark
            watermark = alt.Chart(pd.DataFrame({'text': ['Magi Charts']})).mark_text(
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
            
            # Combine chart and labels
            final_chart = (chart + text + watermark).configure_axis(
                labelFontSize=12,
                titleFontSize=14,
                grid=True
            ).configure_title(
                anchor='middle'
            )
            
            # Save both SVG and HTML versions
            final_chart.save(output_path)
            final_chart.save(html_path)
            
            logger.info(f"Successfully saved visualizations to {output_path} and {html_path}")
            return output_path, html_path
            
        except Exception as e:
            logger.error(f"Error creating transit visualization: {str(e)}")
            return None, None 