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
            'Super Success': '#32CD32',      # Lime Green
            'Super Fame': '#FF8C00',         # Dark Orange
            'Super Success General': '#FF4500', # Orange Red
            'Cinderella': '#FF69B4',         # Pink
            'Sexual': '#FF0000',             # Red
            'Romance': '#9370DB'             # Purple
        }
        
        # Configure Altair settings
        alt.data_transformers.disable_max_rows()
    
    def prepare_data(self, natal_data: Dict[str, Any]) -> pd.DataFrame:
        """Transform natal data into a pandas DataFrame suitable for visualization"""
        records = []
        
        # Process non-Super aspects first
        for aspect_type in ['Cinderella', 'Sexual', 'Romance']:
            aspects = natal_data.get(f'{aspect_type.lower()}_aspects', [])
            details = []
            for aspect in aspects:
                detail = (
                    f"{aspect['planet1_name'].title()}-{aspect['planet2_name'].title()} "
                    f"({aspect['aspect_name'].title()}, "
                    f"orbit: {round(aspect['orbit'], 4)}°)"
                )
                details.append(detail)
            
            records.append({
                'type': aspect_type,
                'subtype': aspect_type,  # Same as type for non-Super aspects
                'count': len(aspects),
                'details': '\n'.join(details) if details else 'None',
            })
        
        # Process Super aspects separately
        super_aspects = natal_data.get('super_aspects', [])
        super_success = []
        super_fame = []
        super_success_general = []
        
        for aspect in super_aspects:
            planets = {aspect['planet1_name'].lower(), aspect['planet2_name'].lower()}
            detail = (
                f"{aspect['planet1_name'].title()}-{aspect['planet2_name'].title()} "
                f"({aspect['aspect_name'].title()}, "
                f"orbit: {round(aspect['orbit'], 4)}°)"
            )
            
            if planets == {'jupiter', 'pluto'}:
                super_success.append(detail)
            elif planets == {'jupiter', 'uranus'}:
                super_fame.append(detail)
            elif planets == {'jupiter', 'chiron'}:
                super_success_general.append(detail)
        
        # Add Super aspects to records
        super_categories = [
            ('Super Success', super_success),
            ('Super Fame', super_fame),
            ('Super Success General', super_success_general)
        ]
        
        for category, aspects in super_categories:
            if aspects:  # Only add categories that have aspects
                records.append({
                    'type': 'Super',  # All are type 'Super' for grouping
                    'subtype': category,  # But different subtypes for coloring
                    'count': len(aspects),
                    'details': '\n'.join(aspects),
                })
        
        # Create DataFrame
        df = pd.DataFrame(records)
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
                       sort=['Super', 'Cinderella', 'Sexual', 'Romance']),
                y=alt.Y('count:Q',
                       title='Number of Aspects',
                       stack=True,
                       scale=alt.Scale(domain=[0, max_count + 1]),
                       axis=alt.Axis(
                           values=tick_values,  # Explicitly set tick values
                           grid=True,
                           gridDash=[2, 2]  # Optional: make grid lines dashed
                       )),
                color=alt.Color('subtype:N',
                    scale=alt.Scale(
                        domain=list(self.colors.keys()),
                        range=list(self.colors.values())
                    ),
                    legend=alt.Legend(title='Aspect Types')
                ),
                tooltip=[
                    alt.Tooltip('subtype:N', title='Aspect Type'),
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
            
            # Combine chart, labels, and watermark
            final_chart = (aspect_chart + text + watermark).configure_axis(
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