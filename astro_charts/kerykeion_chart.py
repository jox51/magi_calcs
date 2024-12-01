from kerykeion import KerykeionChartSVG as KerykeionChart
from typing import Optional
import os

class KerykeionChartSVG:
    """Class to handle creation of Kerykeion charts"""
    
    def __init__(self, subject1, chart_type: str, subject2=None, new_output_directory: Optional[str] = None):
        """
        Initialize the chart creator
        
        Args:
            subject1: First AstrologicalSubject
            chart_type: Type of chart to create (e.g., "Synastry")
            subject2: Optional second AstrologicalSubject for synastry charts
            new_output_directory: Optional directory to save the chart
        """
        self.chart = KerykeionChart(
            subject1,
            chart_type,
            subject2,
            new_output_directory=new_output_directory
        )

    def makeSVG(self):
        """Generate the SVG chart"""
        self.chart.makeSVG() 