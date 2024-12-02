import requests
import json
import logging
from typing import Dict, Any, Optional
import os

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

    def create_transit_loop_charts(self, transit_loop_data: Dict[str, Any], user_id: str = None, job_id: str = None) -> list:
        """Create multiple transit chart records for a transit loop"""
        created_records = []
        
        try:
            # Log the received user_id and job_id
            logger.info(f"Creating transit loop charts with user_id: {user_id}, job_id: {job_id}")
            
            for date, transit_data in transit_loop_data.items():
                # Add the date to the transit data
                if isinstance(transit_data, str):
                    try:
                        transit_data = json.loads(transit_data)
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse transit data for {date} as JSON")
                        continue
                
                transit_data['date'] = date
                
                # Create the record with user_id and job_id
                record = self.create_transit_chart(
                    transit_data=transit_data,
                    user_id=user_id,
                    job_id=job_id
                )
                created_records.append(record)
            
            return created_records
            
        except Exception as e:
            logger.error(f"Error creating transit loop records: {str(e)}")
            raise

    def create_natal_chart(self, natal_data: Dict[str, Any], user_id: str = None, job_id: str = None) -> Dict[str, Any]:
        """Create a new natal chart record in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/natal_charts/records"
            
            # Ensure natal_data is properly formatted
            if isinstance(natal_data, str):
                try:
                    natal_data = json.loads(natal_data)
                except json.JSONDecodeError:
                    logger.warning("Could not parse natal data as JSON")
            
            # Prepare the data
            payload = {
                "natal_data": json.dumps(natal_data) if isinstance(natal_data, dict) else natal_data
            }
            
            # Add user_id and job_id if provided
            if user_id:
                payload["user_id"] = user_id
            if job_id:
                payload["job_id"] = job_id
            
            # Log the payload for debugging
            logger.info(f"Creating natal chart with payload: {payload}")
            
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
            logger.error(f"Error creating natal chart record: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
                logger.error(f"Attempted payload: {payload}")
            raise

    def create_single_transit_chart(self, transit_data: Dict[str, Any], user_id: str = None, job_id: str = None) -> Dict[str, Any]:
        """Create a new single transit chart record in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/single_transit_chart/records"
            
            # Ensure transit_data is properly formatted
            if isinstance(transit_data, str):
                try:
                    transit_data = json.loads(transit_data)
                except json.JSONDecodeError:
                    logger.warning("Could not parse transit data as JSON")
            
            # Prepare the data
            payload = {
                "transit_data": json.dumps(transit_data) if isinstance(transit_data, dict) else transit_data
            }
            
            # Add user_id and job_id if provided
            if user_id:
                payload["user_id"] = user_id
            if job_id:
                payload["job_id"] = job_id
            
            # Log the payload for debugging
            logger.info(f"Creating single transit chart with payload: {payload}")
            
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
            logger.error(f"Error creating single transit chart record: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
                logger.error(f"Attempted payload: {payload}")
            raise

    def create_synastry_chart(self, synastry_data: Dict[str, Any], user_id: str = None, job_id: str = None) -> Dict[str, Any]:
        """Create a new synastry chart record in PocketBase"""
        try:
            endpoint = f"{self.base_url}/api/collections/synastry_charts/records"
            
            # Ensure synastry_data is properly formatted
            if isinstance(synastry_data, str):
                try:
                    synastry_data = json.loads(synastry_data)
                except json.JSONDecodeError:
                    logger.warning("Could not parse synastry data as JSON")
            
            # Prepare the data
            payload = {
                "synastry_data": json.dumps(synastry_data) if isinstance(synastry_data, dict) else synastry_data
            }
            
            # Add user_id and job_id if provided
            if user_id:
                payload["user_id"] = user_id
            if job_id:
                payload["job_id"] = job_id
            
            # Log the payload for debugging
            logger.info(f"Creating synastry chart with payload: {payload}")
            
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
            logger.error(f"Error creating synastry chart record: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
                logger.error(f"Attempted payload: {payload}")
            raise
