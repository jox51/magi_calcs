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

    def create_visualization(self, synastry_data: Dict[str, Any], output_path: str, easy_chart_html_path: str) -> str:
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
            logger.info(f"Person 1 Name Specifically: {person1_name} ")
            logger.info(f"Person 2 Name Specifically: {person2_name} ")

            # Create charts without individual configurations
            aspects_chart = self._create_aspects_chart(df_aspects, person1_name, person2_name)
            scores_chart = self._create_scores_chart(df_scores)
            
            # Prepare marriage dates data if available
            marriage_dates = synastry_data.get('potential_marriage_dates', {}).get('matching_dates', [])
            if marriage_dates:
                df_marriage = self._prepare_marriage_dates_data(marriage_dates)
                marriage_chart = self._create_marriage_dates_chart(df_marriage)
                charts_to_concat = [aspects_chart, scores_chart, marriage_chart]
            else:
                charts_to_concat = [aspects_chart, scores_chart]
            
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
                width=600,
                height=200
            )

            # Add watermark to each chart
            aspects_chart = self._create_aspects_chart(df_aspects, person1_name, person2_name) + watermark
            scores_chart = self._create_scores_chart(df_scores) + watermark

            # Handle marriage dates chart if available
            if marriage_dates:
                df_marriage = self._prepare_marriage_dates_data(marriage_dates)
                # Adjust watermark height for marriage chart
                marriage_watermark = watermark.properties(height=300)
                marriage_chart = self._create_marriage_dates_chart(df_marriage) + marriage_watermark
                charts_to_concat = [aspects_chart, scores_chart, marriage_chart]
            else:
                charts_to_concat = [aspects_chart, scores_chart]

            # Combine charts with single configuration
            final_chart = alt.vconcat(
                *charts_to_concat,
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
            final_chart.save(easy_chart_html_path)
            
            
            return output_path, easy_chart_html_path
            
        except Exception as e:
            logger.error(f"Error creating synastry visualization: {str(e)}")
            raise

    def _create_aspects_chart(self, df: pd.DataFrame, person1_name: str, person2_name: str) -> alt.Chart:
        """Create the aspects bar chart with split coloring for critical Saturn Clashes"""
        # Get the maximum count and create array of tick values
        max_count = max(df['count'])
        tick_values = list(range(0, int(max_count) + 2))
        
        # Define critical planets for Saturn Clashes
        critical_planets = ['chiron', 'pluto', 'neptune', 'venus', 'jupiter', 'uranus', 'sun']
        
        # Create separate rows for critical and regular Saturn Clashes
        df = df.copy()
        new_rows = []
        
        for idx, row in df.iterrows():
            if row['type'] == 'Saturn Clashes':
                # Count critical clashes
                critical_count = sum(1 for planet in critical_planets 
                                   if planet in row['description'].lower())
                regular_count = row['count'] - critical_count
                
                if critical_count > 0:
                    new_rows.append({
                        'type': 'Saturn Clashes',
                        'subtype': 'Critical',
                        'count': critical_count,
                        'description': row['description']
                    })
                if regular_count > 0:
                    new_rows.append({
                        'type': 'Saturn Clashes',
                        'subtype': 'Regular',
                        'count': regular_count,
                        'description': row['description']
                    })
            else:
                # Add subtype for non-Saturn aspects
                new_rows.append({
                    'type': row['type'],
                    'subtype': row['type'],
                    'count': row['count'],
                    'description': row['description']
                })
        
        df_new = pd.DataFrame(new_rows)
        
        # Define colors including darker shade for critical Saturn Clashes
        colors = self.colors.copy()
        colors['Critical Saturn'] = '#B22222'  # Darker red for critical clashes
        colors['Regular Saturn'] = self.colors['Saturn Clashes']  # Original color
        
        return alt.Chart(df_new).mark_bar(
            cornerRadius=5,
            size=40
        ).encode(
            x=alt.X('count:Q', 
                    title='Number of Linkages',
                    axis=alt.Axis(
                        values=tick_values,
                        grid=True
                    ),
                    scale=alt.Scale(domain=[0, max_count + 1])),
            y=alt.Y('type:N', title=None),
            color=alt.Color('subtype:N',
                scale=alt.Scale(
                    domain=[
                        'Cinderella', 'Romance', 'Sexual', 'Marital',
                        'Critical', 'Regular'
                    ],
                    range=[
                        colors['Cinderella'], colors['Romance'],
                        colors['Sexual'], colors['Marital'],
                        colors['Critical Saturn'], colors['Regular Saturn']
                    ]
                ),
                legend=None),
            tooltip=[
                alt.Tooltip('type:N', title='Type'),
                alt.Tooltip('subtype:N', title='Subtype'),
                alt.Tooltip('count:Q', title='Count', format='d'),
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

    def _prepare_marriage_dates_data(self, marriage_dates: List[Dict]) -> pd.DataFrame:
        """Prepare marriage dates data for visualization"""
        records = []
        logger.info(f"Marriage Dates: {marriage_dates}")
        for date_info in marriage_dates:
            date = date_info['date']
            
            # Get person1 and person2 transits
            p1_cinderella = date_info['person1'].get('cinderella_transits', [])
            p1_turbulent = date_info['person1'].get('turbulent_transits', [])
            p2_cinderella = date_info['person2'].get('cinderella_transits', [])
            p2_turbulent = date_info['person2'].get('turbulent_transits', [])

            
            # Format Cinderella transits
            cinderella_details = []
            for transit in p1_cinderella:  # Person 1's transits

                detail = (
                    f"Transit {transit.get('planet2_name', '').title()} "
                    f"{transit.get('aspect_name', '').title()} to "
                    f"{transit.get('person1_name', '')}'s {transit.get('planet1_name', '').title()}"
                )
                cinderella_details.append(detail)
                
            for transit in p2_cinderella:  # Person 2's transits
                logger.info(f"P2 Cinderella Transit Details: {transit} ")
                detail = (
                    f"Transit {transit.get('planet2_name', '').title()} "
                    f"{transit.get('aspect_name', '').title()} to "
                    f"{transit.get('person1_name', '')}'s {transit.get('planet1_name', '').title()}"
                )
                cinderella_details.append(detail)
            
            # Format turbulent transits
            turbulent_details = []
            for transit in p1_turbulent:  # Person 1's turbulent transits
                logger.info(f"P1 Turbulent Transit Details: {transit} ")
                person_name = transit.get('natal_subject_name')  # Default or get from transit
                detail = (
                    f"Transit {transit.get('transit_planet', '').title()} "
                    f"{transit.get('aspect_name', '').title()} to "
                    f"{person_name}'s {transit.get('natal_planet', '').title()} "
                )
                # logger.info(f"TT Person 1: {detail} ")
                turbulent_details.append(detail)
                
            for transit in p2_turbulent:  # Person 2's turbulent transits
                logger.info(f"P2 Turbulent Transit Details: {transit} ")
                person_name = transit.get('natal_subject_name')  # Default or get from transit
                detail = (
                    f"Transit {transit.get('transit_planet', '').title()} "
                    f"{transit.get('aspect_name', '').title()} to "
                    f"{person_name}'s {transit.get('natal_planet', '').title()} "
                )
                # logger.info(f"TT Person 2: {detail} ")
                turbulent_details.append(detail)
            
            # Join details with commas
            cinderella_text = ", ".join(cinderella_details) if cinderella_details else "None"
            turbulent_text = ", ".join(turbulent_details) if turbulent_details else "None"
            
            records.append({
                'date': date,
                'Cinderella': len(p1_cinderella) + len(p2_cinderella),
                'Turbulent': len(p1_turbulent) + len(p2_turbulent),
                'score': (len(p1_cinderella) + len(p2_cinderella)) * 10 - (len(p1_turbulent) + len(p2_turbulent)) * 5,
                'cinderella_aspects': cinderella_text,
                'turbulent_aspects': turbulent_text
            })
        
        return pd.DataFrame(records)

    def _create_marriage_dates_chart(self, df: pd.DataFrame) -> alt.Chart:
        """Create the marriage dates visualization with stacked bars"""
        
        # Reshape data for stacked bars
        df_melted = pd.melt(
            df,
            id_vars=['date', 'score', 'cinderella_aspects', 'turbulent_aspects'],
            value_vars=['Cinderella', 'Turbulent'],
            var_name='transit_type',
            value_name='count'
        )
        
        # Calculate max count for y-axis scale
        max_count = df_melted.groupby('date')['count'].sum().max()
        tick_values = list(range(0, int(max_count) + 2))  # +2 to include max value and one above
        
        # Create stacked bar chart
        bars = alt.Chart(df_melted).mark_bar(size=20).encode(
            x=alt.X('date:O', 
                    title='Date',
                    axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('count:Q',
                    title='Number of Transits',
                    stack=True,
                    axis=alt.Axis(
                        values=tick_values,  # Explicitly set tick values
                        grid=True
                    ),
                    scale=alt.Scale(domain=[0, max_count + 1])),
            color=alt.Color('transit_type:N',
                           scale=alt.Scale(
                               domain=['Cinderella', 'Turbulent'],
                               range=[self.colors['Cinderella'], self.colors['Saturn Clashes']]
                           ),
                           legend=alt.Legend(
                               title='Transit Type'
                           )),
            tooltip=[
                alt.Tooltip('date:O', title='Date'),
                alt.Tooltip('count:Q', title='Count', format='d'),  # 'd' format for integers
                alt.Tooltip('transit_type:N', title='Type'),
                alt.Tooltip('cinderella_aspects:N', title='Cinderella Transits'),
                alt.Tooltip('turbulent_aspects:N', title='Turbulent Transits')
            ]
        ).properties(
            width=600,
            height=300,
            title={
                "text": "Potential Marriage Dates Analysis",
                "subtitle": "Hover over bars for details"
            }
        )
        
        # Add score line
        score_line = alt.Chart(df).mark_line(
            color='blue',
            strokeWidth=2
        ).encode(
            x='date:O',
            y=alt.Y('score:Q',
                    title='Date Score',
                    axis=alt.Axis(titleColor='blue')),
            tooltip=[
                alt.Tooltip('date:O', title='Date'),
                alt.Tooltip('score:Q', title='Date Score')
            ]
        )
        
        # Combine the visualizations
        marriage_chart = alt.layer(
            bars, score_line
        ).resolve_scale(
            y='independent'
        )
        
        return marriage_chart
