import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class CinderellaAnalyzer:
    """Analyzes astrological charts for Cinderella stock patterns"""
    
    def __init__(self):
        self.financial_planets = ['venus', 'chiron', 'neptune', 'pluto']
        self.harmonious_aspects = ['trine', 'sextile', 'conjunction']
    
    def analyze_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze chart data for Cinderella patterns"""
        try:
            aspects = chart_data.get('chart_data', {}).get('subject', {}).get('aspects', [])
            super_aspects = chart_data.get('chart_data', {}).get('super_aspects', [])
            
            if not aspects:
                raise ValueError("No aspects data found in chart")
            
            # Add financial analysis to the main chart_data structure
            chart_data['chart_data']['financial_analysis'] = {
                "standard_aspects": [],
                "super_aspects": [],
                "summary": {
                    "score": 0,
                    "potential": "",
                    "total_harmonious": 0,
                    "total_challenging": 0
                }
            }
            
            # Analyze regular aspects
            for aspect in aspects:
                if (aspect['p1_name'] in self.financial_planets and 
                    aspect['p2_name'] in self.financial_planets):
                    
                    financial_aspect = {
                        'planets': f"{aspect['p1_name'].title()}-{aspect['p2_name'].title()}",
                        'aspect': aspect['aspect_name'].title(),
                        'degrees': round(aspect['actual_degrees'], 2),
                        'is_harmonious': aspect['is_harmonious'],
                        'is_cinderella': aspect.get('is_cinderella', False)
                    }
                    chart_data['chart_data']['financial_analysis']['standard_aspects'].append(financial_aspect)
                    
                    if aspect['is_harmonious']:
                        chart_data['chart_data']['financial_analysis']['summary']['total_harmonious'] += 1
                    else:
                        chart_data['chart_data']['financial_analysis']['summary']['total_challenging'] += 1
            
            # Analyze super aspects
            for aspect in super_aspects:
                if (aspect['planet1_name'] in self.financial_planets or 
                    aspect['planet2_name'] in self.financial_planets):
                    
                    super_aspect = {
                        'planets': f"{aspect['planet1_name'].title()}-{aspect['planet2_name'].title()}",
                        'aspect': f"Super {aspect['aspect_name'].title()}",
                        'degrees': round(aspect['actual_degrees'], 2)
                    }
                    chart_data['chart_data']['financial_analysis']['super_aspects'].append(super_aspect)
                    chart_data['chart_data']['financial_analysis']['summary']['total_harmonious'] += 1
            
            # Calculate score and potential
            score = (chart_data['chart_data']['financial_analysis']['summary']['total_harmonious'] * 2 - 
                    chart_data['chart_data']['financial_analysis']['summary']['total_challenging'])
            
            chart_data['chart_data']['financial_analysis']['summary']['score'] = score
            chart_data['chart_data']['financial_analysis']['summary']['potential'] = (
                "High" if score >= 4 else "Medium" if score >= 1 else "Low"
            )
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error analyzing Cinderella patterns: {str(e)}")
            return chart_data