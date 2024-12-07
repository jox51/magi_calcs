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
            print("Dataframe: ", df)
            
            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            if df.empty:
                logger.warning("No aspect data found for visualization")
                return None
            
            # Get subject name and year from the first date's data
            first_date = list(transit_data.keys())[0]
            subject_name = transit_data[first_date]['natal']['name']
            year = first_date[:4]
            
            # Create the chart
            chart = alt.Chart(df).mark_bar(
                size=20
            ).encode(
                x=alt.X('utcyearmonthdate(date):T',  # Use UTC time to avoid timezone issues
                       title='Date',
                       axis=alt.Axis(
                           format='%b %d',  # Format as "Nov 06"
                           labelAngle=0
                       ),
                       type='ordinal',
                       scale=alt.Scale(
                           nice=False  # Prevent extra padding
                       )),
                y=alt.Y('count:Q',
                       title='Number of Aspects',
                       scale=alt.Scale(
                           domain=[0, 3]
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
                title=f'{subject_name} - Transit Aspects ({year})'
            )
            
            # Save the chart
            chart.save(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating transit visualization: {str(e)}")
            raise

    def _split_into_monthly_chunks(self, df: pd.DataFrame) -> List[pd.DataFrame]:
        """Split dataframe into monthly chunks"""
        if len(df) == 0:
            return [df]
        
        # Group by year and month without creating Period objects
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        groups = [group for _, group in df.groupby('year_month')]
        
        # Drop the helper column
        for group in groups:
            group.drop('year_month', axis=1, inplace=True)
        
        return groups


        """Combine multiple HTML charts into a single PDF"""
        try:
            merger = PdfMerger()
            
            # Create temporary directory for intermediate PDFs
            with tempfile.TemporaryDirectory() as temp_dir:
                # Convert each HTML to PDF
                for i, chart_path in enumerate(chart_paths):
                    temp_pdf = os.path.join(temp_dir, f'chart_{i}.pdf')
                    pdfkit.from_file(chart_path, temp_pdf)
                    merger.append(temp_pdf)
                
                # Write the combined PDF
                merger.write(output_pdf_path)
                merger.close()
                
            return output_pdf_path
            
        except Exception as e:
            logger.error(f"Error combining charts to PDF: {str(e)}")
            raise