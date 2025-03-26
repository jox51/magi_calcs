import altair as alt
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

class TransitLoopMidpointVisualizationService:
    """Service for creating visualizations of transit loop midpoint data"""
    
    def __init__(self):
        """Initialize the visualization service with color schemes and settings"""
        self.categories = {
            'success': '#FFD700',  # Gold
            'love': '#FF69B4',     # Hot Pink
            'challenging': '#4169E1',   # Royal Blue
            'health': '#808080'     # Gray
        }
        
        # Configure Altair settings
        alt.data_transformers.disable_max_rows()
    
    def prepare_data(self, transit_data: Dict[str, Any]) -> pd.DataFrame:
        """Transform transit loop midpoint data into a pandas DataFrame"""
        records = []
        
        # Get cosmobiology activations
        activations = transit_data.get('cosmobiology_activations', {})
        
        for date_str, day_activations in activations.items():
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Group activations by category for this date
            category_counts = {}
            for activation in day_activations:
                category = activation['category']
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Create a record for each category (even if count is 0)
            for category in self.categories.keys():
                records.append({
                    'date': date,
                    'category': category,
                    'count': category_counts.get(category, 0)  # Get count or 0 if no activations
                })
        
        df = pd.DataFrame(records)
        
        # Ensure all dates have all categories
        all_dates = df['date'].unique()
        all_categories = list(self.categories.keys())
        
        # Create a complete index
        idx = pd.MultiIndex.from_product([all_dates, all_categories], 
                                       names=['date', 'category'])
        
        # Reindex and fill missing values
        df = df.set_index(['date', 'category']).reindex(idx, fill_value=0).reset_index()
        
        return df.sort_values(['date', 'category'])

    def create_monthly_chart(self, df: pd.DataFrame, subject_name: str) -> alt.Chart:
        """Create a monthly visualization of transit loop midpoint activations"""
        base = alt.Chart(df).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('category:N', title='Category'),
            color=alt.Color('category:N', scale=alt.Scale(domain=list(self.categories.keys()),
                                                        range=list(self.categories.values()))),
            tooltip=['date', 'category', 'midpoint_planets', 'transit_planet', 'aspect', 'angle', 'orb']
        )

        points = base.mark_circle(size=60).encode(
            size=alt.Size('orb:Q', scale=alt.Scale(range=[100, 300]))
        )

        title = f"Transit Loop Midpoint Activations for {subject_name}"
        return points.properties(
            width=800,
            height=200,
            title=title
        )

    def create_yearly_chart(self, df: pd.DataFrame, subject_name: str) -> alt.Chart:
        """Create a yearly overview visualization of transit loop midpoint activations"""
        # Similar to monthly chart but with different dimensions and potentially simplified
        return self.create_monthly_chart(df, f"{subject_name} - Yearly Overview").properties(
            height=100
        )

    def _split_into_monthly_chunks(self, df: pd.DataFrame) -> List[pd.DataFrame]:
        """Split the data into monthly chunks for separate visualizations"""
        return [group for _, group in df.groupby(pd.Grouper(key='date', freq='M'))]

    def _calculate_bar_width(self, df: pd.DataFrame) -> int:
        """Calculate appropriate bar width based on number of dates"""
        num_dates = len(df['date'].unique())
        if num_dates <= 7:
            return 40  # Wider bars for few dates
        elif num_dates <= 14:
            return 30
        elif num_dates <= 30:
            return 20
        else:
            return 10  # Thinner bars for many dates

    def create_visualization(self, chart_data: Dict[str, Any], output_path: str, html_path: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            # Prepare the data
            df = self.prepare_data(chart_data)
            
            if df.empty:
                logger.warning("No data found for visualization")
                return None, None

            # Get date range and name
            date_range = f"{df['date'].min().strftime('%B %Y')}"
            if df['date'].min().month != df['date'].max().month:
                date_range += f" - {df['date'].max().strftime('%B %Y')}"
            logger.info(f"Chart Data: {chart_data}")
             # Get subject name
            daily_aspects = chart_data.get('daily_aspects', {})
            first_date = list(daily_aspects.keys())[0]
            name = daily_aspects[first_date]['natal']['name']

            # Create overall chart
            overall_chart = self._create_bar_chart(df, name, date_range, "Overall View")

            # Split by months if spanning multiple months
            df['month_str'] = df['date'].dt.strftime('%Y-%m')
            unique_months = sorted(df['month_str'].unique())

            if len(unique_months) > 1:
                charts = [overall_chart]  # Start with overall chart
                
                # Add monthly charts
                for month in unique_months:
                    month_df = df[df['month_str'] == month]
                    month_title = pd.to_datetime(month + '-01').strftime('%B %Y')
                    month_chart = self._create_bar_chart(month_df, name, month_title, "Monthly View")
                    charts.append(month_chart)

                # Combine charts vertically with proper spacing
                final_chart = alt.vconcat(*charts, spacing=20)
            else:
                final_chart = overall_chart

            # Save visualizations
            final_chart.save(output_path)
            final_chart.save(html_path)
            
            return output_path, html_path

        except Exception as e:
            logger.error(f"Error creating transit loop midpoint visualization: {str(e)}")
            return None, None

    def _create_bar_chart(self, df: pd.DataFrame, name: str, date_range: str, subtitle: str) -> alt.Chart:
        """Helper method to create a bar chart with consistent styling"""
        return alt.Chart(df).mark_bar(
            size=20  # Fixed size instead of dynamic width
        ).encode(
            x=alt.X('utcyearmonthdate(date):T',
                    title='Date',
                    axis=alt.Axis(
                        format='%b %d',
                        labelAngle=0
                    ),
                    type='ordinal',  # Specify ordinal type
                    scale=alt.Scale(
                        nice=False,
                        padding=10  # Add padding to prevent bars from extending past limits
                    )),
            y=alt.Y('count:Q',
                    title='Number of Activations',
                    stack=True,
                    axis=alt.Axis(
                        tickMinStep=1,
                        values=list(range(1, 6))
                    ),
                    scale=alt.Scale(domain=[0, max(5, df.groupby('date')['count'].sum().max())])),
            color=alt.Color('category:N',
                           scale=alt.Scale(
                               domain=list(self.categories.keys()),
                               range=list(self.categories.values())
                           )),
            tooltip=[
                alt.Tooltip('utcyearmonthdate(date):T', title='Date', format='%b %d'),
                'category',
                alt.Tooltip('count:Q', format='d')
            ]
        ).properties(
            title={
                'text': f"Transit Loop Midpoint Activations for {name} ({date_range})",
                'subtitle': subtitle
            },
            width=600,
            height=200
        )