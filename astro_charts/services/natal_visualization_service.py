import altair as alt
import pandas as pd
from typing import Dict, Any, List
import logging
import os

logger = logging.getLogger(__name__)

class NatalVisualizationService:
    """Service for creating visualizations of natal chart aspect data"""
    
    def __init__(self):
        """Initialize the visualization service with color schemes and settings"""
        self.colors = {
            'Super': '#FFD700',      # Gold
            'Cinderella': '#FF69B4', # Pink
            'Sexual': '#FF0000',     # Red
            'Romance': '#9370DB'     # Purple
        }
        
        # Configure Altair settings
        alt.data_transformers.disable_max_rows()
    
    def prepare_data(self, natal_data: Dict[str, Any]) -> pd.DataFrame:
        """Transform natal data into a pandas DataFrame suitable for visualization"""
        # Get aspects from the nested structure
        aspects_data = {
            'Super': natal_data.get('super_aspects', []),
            'Cinderella': natal_data.get('cinderella_aspects', []),
            'Sexual': natal_data.get('sexual_aspects', []),
            'Romance': natal_data.get('romance_aspects', [])
        }
        
        records = []
        
        # Process each aspect type
        for aspect_type, aspects in aspects_data.items():
            # Create detail string for all aspects of this type
            details = []
            for aspect in aspects:
                detail = (
                    f"{aspect['planet1_name'].title()}-{aspect['planet2_name'].title()} "
                    f"({aspect['aspect_name'].title()}, "
                    f"orbit: {round(aspect['orbit'], 4)}°)"
                )
                details.append(detail)
            
            # Create record with count and details
            records.append({
                'type': aspect_type,
                'count': len(aspects),
                'details': '\n'.join(details) if details else 'None',
            })
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Add debug logging
        logger.info(f"Created DataFrame with aspect counts:\n{df}")
        
        return df
    
    def create_visualization(self, natal_data: Dict[str, Any], output_path: str, html_path: str) -> tuple[str, str]:
        """Create and save visualizations of natal aspects"""
        try:
            # Get subject name and birth details
            subject = natal_data.get('subject', {})
            name = subject.get('name', 'Unknown')
            birth_data = subject.get('birth_data', {})
            birth_details = (
                f"{name}\n"
                f"Born: {birth_data.get('date')} at {birth_data.get('time')}\n"
                f"Location: {birth_data.get('location')}"
            )
            
            # Prepare the data
            df = self.prepare_data(natal_data)
            
            if df.empty:
                logger.warning("No special aspects found in natal chart")
                return None, None
            
            # Get the maximum count and create array of tick values
            max_count = max(df['count'])
            tick_values = list(range(0, max_count + 2))  # +2 to include max value and one above
            
            aspect_chart = alt.Chart(df).mark_bar(
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
                           grid=True,
                           gridDash=[2, 2]  # Optional: make grid lines dashed
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
                    "text": [birth_details],
                    "subtitle": ["Natal Chart Special Aspects"],
                    "color": "black",
                    "fontSize": 14,
                    "anchor": "middle"
                }
            )
            
            # Add text labels on top of bars
            text = aspect_chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5
            ).encode(
                text=alt.Text('count:Q', format='d')  # 'd' format for integers
            )
            
            # Combine chart and labels
            final_chart = (aspect_chart + text).configure_axis(
                labelFontSize=12,
                titleFontSize=14,
                grid=True
            ).configure_title(
                anchor='middle'
            )
            
            # Save both SVG and HTML versions
            final_chart.save(output_path)
            final_chart.save(html_path)
            
            return output_path, html_path
            
        except Exception as e:
            logger.error(f"Error creating natal visualization: {str(e)}")
            return None, None 