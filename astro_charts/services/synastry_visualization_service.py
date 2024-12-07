import altair as alt
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SynastryVisualizationService:
    def __init__(self):
        """Initialize the synastry visualization service with color schemes"""
        self.colors = {
            'Cinderella': '#90EE90',    # Light green
            'Romance': '#FFB6C1',        # Light pink
            'Sexual': '#DDA0DD',         # Plum
            'Marital': '#FFD700',        # Gold
            'Saturn Clashes': '#FF6B6B'  # Light red - moved to end and renamed
        }
        
        # Configure Altair settings
        alt.data_transformers.disable_max_rows()
    
    def prepare_data(self, synastry_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare data for visualization"""
        linkage_counts = {
            'Cinderella': len(synastry_data.get('cinderella_linkages', [])),
            'Romance': len(synastry_data.get('romance_linkages', [])),
            'Sexual': len(synastry_data.get('sexual_linkages', [])),
            'Marital': len(synastry_data.get('marital_linkages', [])),
            'Saturn Clashes': len(synastry_data.get('saturn_clashes', []))  # Renamed and moved to end
        }
        
        # Create DataFrame
        df = pd.DataFrame([
            {'type': k, 'count': v, 'description': self._get_aspect_descriptions(synastry_data, k.lower().replace(' clashes', ''))}
            for k, v in linkage_counts.items()
        ])
        
        return df
    
    def _get_aspect_descriptions(self, data: Dict[str, Any], aspect_type: str) -> str:
        """Get formatted descriptions of aspects for tooltips"""
        key = f"{aspect_type}_linkages" if aspect_type != "saturn" else "saturn_clashes"
        aspects = data.get(key, [])
        
        if not aspects:
            return "No aspects"
            
        descriptions = []
        for aspect in aspects:
            if aspect_type == "saturn":
                desc = f"⚠️ {aspect['saturn_person']}'s Saturn {aspect['aspect_name']} {aspect['planet_person']}'s {aspect['planet2_name'].title()}"  # Added warning emoji
            else:
                desc = f"{aspect['planet1_name'].title()} {aspect['aspect_name']} {aspect['planet2_name'].title()}"
            descriptions.append(desc)
            
        return "\n".join(descriptions)

    def create_visualization(self, synastry_data: Dict[str, Any], output_path: str) -> str:
        try:
            # Prepare the data for aspects
            df_aspects = self.prepare_data(synastry_data)
            
            # Prepare data for scores
            scores = synastry_data.get('compatibility_scores', {})
            df_scores = pd.DataFrame([
                {'category': 'Romance', 'score': scores.get('romance', 0)},
                {'category': 'Compatibility', 'score': scores.get('compatibility', 0)},
                {'category': 'Longevity', 'score': scores.get('longevity', 0)},
                {'category': 'Overall', 'score': scores.get('overall', 0)}
            ])
            
            # Get person names
            person1_name = synastry_data['person1']['subject']['name']
            person2_name = synastry_data['person2']['subject']['name']

            # Create charts without individual configurations
            aspects_chart = self._create_aspects_chart(df_aspects, person1_name, person2_name)
            scores_chart = self._create_scores_chart(df_scores)
            
            # Combine charts with single configuration
            final_chart = alt.vconcat(
                aspects_chart,
                scores_chart,
                title={
                    "text": f"Relationship Analysis: {person1_name} & {person2_name}",
                    "subtitle": "Hover over elements for details",
                    "fontSize": 20,
                    "anchor": "middle"
                }
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            ).configure_title(
                fontSize=16,
                anchor='middle'
            )
            
            # Save the chart
            final_chart.save(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating synastry visualization: {str(e)}")
            raise

    def _create_aspects_chart(self, df: pd.DataFrame, person1_name: str, person2_name: str) -> alt.Chart:
        """Create the aspects bar chart without configuration"""
        return alt.Chart(df).mark_bar(
            cornerRadius=5,
            size=40
        ).encode(
            x=alt.X('count:Q', title='Number of Linkages'),
            y=alt.Y('type:N', title=None),
            color=alt.Color('type:N', 
                scale=alt.Scale(domain=list(self.colors.keys()), 
                              range=list(self.colors.values())),
                legend=None),
            tooltip=[
                alt.Tooltip('type:N', title='Type'),
                alt.Tooltip('count:Q', title='Count'),
                alt.Tooltip('description:N', title='Details')
            ]
        ).properties(
            width=600,
            height=200,
            title="Linkages"
        )

    def _create_scores_chart(self, df: pd.DataFrame) -> alt.Chart:
        """Create the compatibility scores chart without configuration"""
        color_scale = alt.Scale(
            domain=[0, 50, 100],
            range=['#ff6b6b', '#ffd93d', '#4CAF50']
        )
        
        base = alt.Chart(df).encode(
            y=alt.Y('category:N', 
                    title=None,
                    sort=['Romance', 'Compatibility', 'Longevity', 'Overall']),
            x=alt.X('score:Q',
                    scale=alt.Scale(domain=[0, 100]),
                    title='Score')
        )

        background = base.mark_bar(
            color='#eee',
            height=30
        ).encode(
            x=alt.value(100)
        )

        bars = base.mark_bar(
            height=30,
            cornerRadius=5
        ).encode(
            color=alt.Color('score:Q', scale=color_scale),
            tooltip=[
                alt.Tooltip('category:N', title='Category'),
                alt.Tooltip('score:Q', title='Score', format='.0f')
            ]
        )

        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=5,
            color='white',
            fontSize=14
        ).encode(
            text=alt.Text('score:Q', format='.0f')
        )

        return alt.layer(background, bars, text).properties(
            width=600,
            height=200,
            title="Compatibility Scores"
        )
