import requests
import json
import logging
from typing import Dict, Any, Optional
import os
import aiohttp

logger = logging.getLogger(__name__)

class PocketbaseService:
    def __init__(self, base_url: str = "https://magi.pockethost.io"):
        """Initialize PocketBase service"""
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.headers = {
            'Content-Type': 'application/json'
        }
        # Authenticate on initialization
        self.authenticate()

    def authenticate(self) -> None:
        """Authenticate with PocketBase using credentials from environment"""
        try:
            email = os.getenv('POCKETBASE_EMAIL')
            password = os.getenv('POCKETBASE_PASSWORD')
            
            if not email or not password:
                raise ValueError("POCKETBASE_EMAIL and POCKETBASE_PASSWORD must be set in environment")

            endpoint = f"{self.base_url}/api/admins/auth-with-password"
            
            payload = {
                "identity": email,
                "password": password
            }
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            
            # Extract and store the token
            auth_data = response.json()
            self.token = auth_data['token']
            
            # Update headers with the new token
            self.headers['Authorization'] = f'Bearer {self.token}'
            
            logger.info("Successfully authenticated with PocketBase")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise

    def create_transit_chart(self, transit_data: Dict[str, Any], user_id: str = None, job_id: str = None) -> Dict[str, Any]:
        """Create a new transit chart record in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/transit_charts/records"
            
            # Prepare the data
            payload = {
                "transit_data": json.dumps(transit_data)
            }
            
            # Only add user_id and job_id if they are not None
            if user_id:
                payload["user_id"] = user_id
            if job_id:
                payload["job_id"] = job_id
            
            # Log the payload for debugging
            logger.info(f"Creating transit chart with payload: {payload}")
            
            # Make the request
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Log the response for debugging
            logger.info(f"PocketBase response: {response.json()}")
            
            # Return the created record
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating transit chart record: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise

    def create_transit_loop_charts(self, transit_loop_data: Dict[str, Any], user_id: str = None, job_id: str = None) -> Dict[str, Any]:
        """Create transit loop record with visualization in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/transit_charts/records"
            
            # Prepare the form data
            data = {
                'transit_data': json.dumps({
                    'daily_aspects': transit_loop_data.get('transit_data', {}).get('daily_aspects', {}),
                    'turbulent_transits': transit_loop_data.get('transit_data', {}).get('turbulent_transits', {}),
                    'date_range': transit_loop_data.get('date_range', {})
                })
            }
            
            if user_id:
                data['user_id'] = user_id
            if job_id:
                data['job_id'] = job_id
            
            # Get the visualization paths
            viz_path = transit_loop_data.get('visualization_path')
            viz_html_path = transit_loop_data.get('visualization_html_path')
            
            # Prepare files dictionary
            files = {}
            
            # Add SVG visualization if it exists
            if viz_path and os.path.exists(viz_path):
                files['loop_chart'] = ('visualization.svg', open(viz_path, 'rb'), 'image/svg+xml')
                logger.info(f"Adding visualization SVG from {viz_path}")
            
            # Add HTML visualization if it exists
            if viz_html_path and os.path.exists(viz_html_path):
                files['loop_chart_html'] = ('visualization.html', open(viz_html_path, 'rb'), 'text/html')
                logger.info(f"Adding visualization HTML from {viz_html_path}")
            
            # Remove Content-Type header for multipart request
            headers = {k: v for k, v in self.headers.items() if k != 'Content-Type'}
            
            # Log request details
            logger.info(f"Sending request to {endpoint}")
            logger.info(f"Data fields: {list(data.keys())}")
            if files:
                logger.info(f"File fields: {list(files.keys())}")
            
            try:
                # Make the request
                response = requests.post(
                    endpoint,
                    headers=headers,
                    data=data,
                    files=files if files else None
                )
                
                # Log response for debugging
                if response.status_code != 200:
                    logger.error(f"Response status: {response.status_code}")
                    logger.error(f"Response text: {response.text}")
                
                # Check if request was successful
                response.raise_for_status()
                
                return response.json()
                
            finally:
                # Clean up file handles
                for file_key in files:
                    files[file_key][1].close()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating transit loop record: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
                logger.error(f"Request data: {data}")
                if files:
                    logger.error(f"Files included: {list(files.keys())}")
            raise

    def create_natal_chart(self, natal_data: Dict[str, Any], chart_path: str = None, 
                          easy_chart: str = None, easy_chart_html: str = None, 
                          user_id: str = None, job_id: str = None) -> Dict[str, Any]:
        """Create a new natal chart record in PocketBase with chart files"""
        try:
            endpoint = f"{self.base_url}/api/collections/natal_charts/records"
            
            # Prepare the form data
            data = {
                'natal_data': json.dumps(natal_data) if isinstance(natal_data, dict) else natal_data,
            }
            
            if user_id:
                data['user_id'] = user_id
            if job_id:
                data['job_id'] = job_id
            
            # Prepare files dictionary
            files = {}
            
            # Add traditional chart if it exists
            if chart_path and os.path.exists(chart_path):
                files['chart'] = ('chart.svg', open(chart_path, 'rb'), 'image/svg+xml')
                logger.info(f"Adding traditional chart file from {chart_path}")
            
            # Add easy visualization SVG if it exists
            if easy_chart and os.path.exists(easy_chart):
                files['easy_chart'] = ('easy_chart.svg', open(easy_chart, 'rb'), 'image/svg+xml')
                logger.info(f"Adding easy visualization SVG from {easy_chart}")
            
            # Add easy visualization HTML if it exists
            if easy_chart_html and os.path.exists(easy_chart_html):
                files['easy_chart_html'] = ('easy_chart.html', open(easy_chart_html, 'rb'), 'text/html')
                logger.info(f"Adding easy visualization HTML from {easy_chart_html}")
            
            # Remove Content-Type header for multipart request
            headers = {k: v for k, v in self.headers.items() if k != 'Content-Type'}
            
            # Log request details
            logger.info(f"Sending request to {endpoint}")
            logger.info(f"Data fields: {list(data.keys())}")
            if files:
                logger.info(f"File fields: {list(files.keys())}")
            
            try:
                # Make the request
                response = requests.post(
                    endpoint,
                    headers=headers,
                    data=data,
                    files=files if files else None
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                return response.json()
                
            finally:
                # Clean up file handles
                for file_key in files:
                    files[file_key][1].close()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating natal chart record: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
                logger.error(f"Request data: {data}")
                if files:
                    logger.error(f"Files included: {list(files.keys())}")
            raise

    def create_single_transit_chart(
        self, 
        transit_data: Dict[str, Any], 
        chart_path: str = None,
        easy_chart: str = None,
        easy_chart_html: str = None,
        user_id: str = None, 
        job_id: str = None
    ) -> Dict[str, Any]:
        """Create a new transit chart record in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/single_transit_chart/records"
            
            # Prepare the form data
            data = {
                'transit_data': json.dumps(transit_data) if isinstance(transit_data, dict) else transit_data,
            }
            
            if user_id:
                data['user_id'] = user_id
            if job_id:
                data['job_id'] = job_id
            
            # Prepare files dictionary
            files = {}
            
            # Add traditional chart if it exists
            if chart_path and os.path.exists(chart_path):
                files['chart'] = ('chart.svg', open(chart_path, 'rb'), 'image/svg+xml')
                logger.info(f"Adding traditional chart file from {chart_path}")
            
            # Add easy visualization SVG if it exists
            if easy_chart and os.path.exists(easy_chart):
                files['easy_chart'] = ('easy_chart.svg', open(easy_chart, 'rb'), 'image/svg+xml')
                logger.info(f"Adding easy visualization SVG from {easy_chart}")
            
            # Add easy visualization HTML if it exists
            if easy_chart_html and os.path.exists(easy_chart_html):
                files['easy_chart_html'] = ('easy_chart_html.html', open(easy_chart_html, 'rb'), 'text/html')
                logger.info(f"Adding easy visualization HTML from {easy_chart_html}")
            
            # Remove Content-Type header for multipart request
            headers = {k: v for k, v in self.headers.items() if k != 'Content-Type'}
            
            try:
                # Make the request
                response = requests.post(
                    endpoint,
                    headers=headers,
                    data=data,
                    files=files if files else None
                )
                
                response.raise_for_status()
                return response.json()
                
            finally:
                # Clean up file handles
                for file_key in files:
                    files[file_key][1].close()
                
        except Exception as e:
            logger.error(f"Error creating transit chart record: {str(e)}")
            raise

    def create_synastry_chart(self, synastry_data: Dict[str, Any], chart_path: str = None, easy_chart_path: str = None, easy_chart_html_path: str = None, user_id: str = None, job_id: str = None, is_marriage_request: bool = False) -> Dict[str, Any]:
        """Create synastry record with visualization in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/synastry_charts/records"
            
            # Prepare the form data
            data = {
                'synastry_data': json.dumps(synastry_data)
            }
         
            
            if user_id:
                data['user_id'] = user_id
            if job_id:
                data['job_id'] = job_id
            if is_marriage_request:
                data['is_marriage_request'] = True
            else:
                data['is_marriage_request'] = False
                
            logger.info(f"Easy chart html path: {easy_chart_html_path}")
            # Prepare files
            files = {}
            if chart_path and os.path.exists(chart_path):
                files['chart'] = ('chart.svg', open(chart_path, 'rb'), 'image/svg+xml')
            if easy_chart_path and os.path.exists(easy_chart_path):
                files['easy_chart'] = ('easy_chart.svg', open(easy_chart_path, 'rb'), 'image/svg+xml')
            if easy_chart_html_path and os.path.exists(easy_chart_html_path):
                files['easy_chart_html'] = ('easy_chart_html.html', open(easy_chart_html_path, 'rb'), 'text/html')
        
              # Remove Content-Type header for multipart request
            headers = {k: v for k, v in self.headers.items() if k != 'Content-Type'}
            
            # Make the request
            response = requests.post(
                endpoint,
                headers=headers,
                data=data,
                files=files if files else None
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating synastry chart record: {str(e)}")
            raise

    def create_cosmo_chart(self, transit_data: Dict[str, Any], chart_path: str = None, chart_html_path: str = None, user_id: str = None, job_id: str = None) -> Dict[str, Any]:
        """Create a new cosmobiology chart record in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/cosmo_charts/records"
            
            # Prepare the data
            data = {
                'transit_data': json.dumps(transit_data)
            }
            
            # Add optional fields if provided
            if user_id:
                data['user_id'] = user_id
            if job_id:
                data['job_id'] = job_id
            
            # Prepare files
            files = {}
            if chart_path and os.path.exists(chart_path):
                files['cosmo_chart'] = ('chart.svg', open(chart_path, 'rb'), 'image/svg+xml')
            if chart_html_path and os.path.exists(chart_html_path):
                files['cosmo_chart_html'] = ('chart.html', open(chart_html_path, 'rb'), 'text/html')
            
            # Remove Content-Type header for multipart request
            headers = {k: v for k, v in self.headers.items() if k != 'Content-Type'}
            
            try:
                # Make the request
                response = requests.post(
                    endpoint,
                    headers=headers,
                    data=data,
                    files=files if files else None
                )
                
                response.raise_for_status()
                return response.json()
                
            finally:
                # Clean up file handles
                for file_key in files:
                    files[file_key][1].close()
                
        except Exception as e:
            logger.error(f"Error creating cosmobiology chart record: {str(e)}")
            raise


    def create_vedic_lucky_times_record(
        self,
        natal_data: Dict[str, Any],
        yogi_point_data: Dict[str, Any],
        user_id: str = None,
        job_id: str = None
    ) -> Dict[str, Any]:
        """Create a new Vedic lucky times record in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/lucky_times_vedic/records"
            
            # Add person's name to the lucky times data
            yogi_point_data["person_name"] = natal_data.get("subject", {}).get("name", "Unknown")
            
            # Prepare the data
            payload = {
                "lucky_times_data": json.dumps({
                    # "natal_data": natal_data,
                    "yogi_point_data": yogi_point_data
                }),
                "lucky_dates_summary": json.dumps({
                    "dates_summary": yogi_point_data["dates_summary"]
                })
            }
            
            if user_id:
                payload["user_id"] = user_id
            if job_id:
                payload["job_id"] = job_id
            
            # Make the request
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Vedic lucky times record: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise

    def create_sports_prediction_record(
        self,
        chart_data: Dict[str, Any],
        prediction_results: Dict[str, Any],
        event_name: str,
        favorite_name: str,
        underdog_name: str,
        user_id: str = None,
        job_id: str = None
    ) -> Dict[str, Any]:
        """Create a new sports prediction record in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/sports_predictions/records"
            
            # Prepare the data - structure for efficient retrieval
            payload = {
                "event_name": event_name,
                "favorite_name": favorite_name,
                "underdog_name": underdog_name,
                "prediction_data": json.dumps(prediction_results),
                "prediction_summary": json.dumps({
                    "predicted_winner": prediction_results.get("prediction", {}).get("predicted_winner", "Unknown"),
                    "confidence_level": prediction_results.get("prediction", {}).get("confidence_level", "Unknown"),
                    "is_tie": prediction_results.get("prediction", {}).get("is_tie", False),
                    "favorite_malefic_count": prediction_results.get("prediction", {}).get("favorite_malefic_count", 0),
                    "underdog_malefic_count": prediction_results.get("prediction", {}).get("underdog_malefic_count", 0),
                    "favorite_total_score": prediction_results.get("prediction", {}).get("favorite_total_score", 0),
                    "underdog_total_score": prediction_results.get("prediction", {}).get("underdog_total_score", 0),
                    "favorite_sky": prediction_results.get("prediction", {}).get("has_favorite_sky", False),
                    "underdog_sky": prediction_results.get("prediction", {}).get("has_underdog_sky", False),
                    "favorite_pky": prediction_results.get("prediction", {}).get("has_favorite_pky", False),
                    "underdog_pky": prediction_results.get("prediction", {}).get("has_underdog_pky", False),
                    "favorite_sky_count": prediction_results.get("prediction", {}).get("favorite_sky_count", 0),
                    "underdog_sky_count": prediction_results.get("prediction", {}).get("underdog_sky_count", 0),
                    "favorite_pky_count": prediction_results.get("prediction", {}).get("favorite_pky_count", 0),
                    "underdog_pky_count": prediction_results.get("prediction", {}).get("underdog_pky_count", 0),
                    "favorite_cuspal": prediction_results.get("prediction", {}).get("has_favorite_cuspal", False),
                    "underdog_cuspal": prediction_results.get("prediction", {}).get("has_underdog_cuspal", False),
                    "favorite_cuspal_score": prediction_results.get("prediction", {}).get("favorite_cuspal_score", 0),
                    "underdog_cuspal_score": prediction_results.get("prediction", {}).get("underdog_cuspal_score", 0),
                    "favorite_cuspal_count": prediction_results.get("prediction", {}).get("favorite_cuspal_count", 0),
                    "underdog_cuspal_count": prediction_results.get("prediction", {}).get("underdog_cuspal_count", 0),
                    "event_date": prediction_results.get("event_details", {}).get("event_date", "Unknown")
                })
            }
            
            # Add optional fields if provided
            if user_id:
                payload["user_id"] = user_id
            if job_id:
                payload["job_id"] = job_id
            
            # Make the request
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating sports prediction record: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
