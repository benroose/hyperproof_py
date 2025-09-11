# utils.py
#
# This module provides utility functionality for interacting with the Hyperproof API, 
# including handling API authentication and sending HTTP requests to the Hyperproof API.
# Author: Virgil Vaduva
# Timestamp: 2024-09-25
# License: This project is licensed under the GNU General Public License (GPL).
#
# Description:
# The APIClient class handles authentication via OAuth, and it provides methods 
# for making GET, POST, PUT, and PATCH requests. The class ensures token-based 
# authorization is applied to every request. Error handling and logging are used to 
# capture and report request issues.

import requests
import logging
import time
import random
from requests.exceptions import HTTPError, RequestException, Timeout, ConnectionError
import json

# Set up logging
# A logger named 'Hyperproof API' is created to capture logs for this module.
logger = logging.getLogger('Hyperproof API')
logger.setLevel(logging.INFO)  # Default logging level set to INFO

# Create a console handler for the logger and set its logging level to DEBUG.
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Formatter is created to display logs in a specific format: time, logger name, 
# logging level, and the actual log message.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Attach the formatter to the console handler.
ch.setFormatter(formatter)

# Attach the console handler to the logger.
logger.addHandler(ch)

# OAuth token endpoint for Hyperproof's authentication.
TOKEN_ENDPOINT = "https://accounts.hyperproof.app/oauth/token"

# Default network timeout for all HTTP requests (in seconds)
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 1.0

class APIClient:
    """
    The APIClient class handles authentication via OAuth2 and makes HTTP requests to the Hyperproof API.
    This class manages the access token required for authorization and includes methods to interact
    with the API (GET, POST, PUT, PATCH).
    """
    
    def __init__(self, client_id, client_secret):
        """
        Initializes the APIClient with the given client credentials and authenticates immediately.
        - client_id: The OAuth client ID for authenticating with Hyperproof.
        - client_secret: The OAuth client secret for authenticating with Hyperproof.
        
        The access_token is initially set to None. Upon initialization, the client attempts to 
        authenticate by calling the `_authenticate()` method.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None  # Access token will be set upon successful authentication.
        
        logger.debug(f"Initializing APIClient with client_id: {client_id}")
        
        try:
            self._authenticate()  # Attempt to authenticate upon initialization.
        except Exception as e:
            logger.error(f"Failed to authenticate: {e}")
            self.access_token = None  # Ensure token remains None if authentication fails.

    def _authenticate(self):
        """
        Handles OAuth authentication with Hyperproof to retrieve an access token.
        Sends a POST request to the TOKEN_ENDPOINT with the client credentials.
        If successful, the access token is stored for future requests.
        """
        logger.debug("Authenticating to get access token")
        
        # Parameters required for the OAuth2 client credentials grant type.
        params = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        logger.debug(f"Authentication params: {json.dumps(params, indent=2)}")
        
        try:
            # Sending POST request to OAuth token endpoint to obtain the access token.
            response = requests.post(TOKEN_ENDPOINT, data=params)
            
            # Log the status code and response details for debugging purposes.
            logger.debug(f"Token request status code: {response.status_code}")
            logger.debug(f"Token response headers: {json.dumps(dict(response.headers), indent=2)}")
            logger.debug(f"Token response body: {response.text}")

            if response.status_code == 200:
                # Parse and store the access token if authentication is successful.
                response_json = self._parse_json(response)
                self.access_token = response_json.get('access_token')
                logger.debug("Access token retrieved successfully")
            else:
                # Log an error if the token request fails (e.g., invalid credentials).
                logger.error(f"Failed to retrieve access token: {response.status_code} {response.text}")
                self.access_token = None
        except (HTTPError, ConnectionError, Timeout, RequestException) as err:
            # Catch common HTTP request errors and log them.
            logger.error(f"Error during authentication: {err}")
            self.access_token = None

    def _get_headers(self):
        """
        Constructs the headers required for API requests.
        If the access token is missing or expired, the client will attempt to re-authenticate.
        Returns the headers including the Authorization Bearer token.
        """
        if not self.access_token:
            logger.debug("Access token not found. Re-authenticating...")
            self._authenticate()  # Re-authenticate if no valid access token is available.
        
        # Headers for the API request. Do not set Content-Type here to allow
        # requests to set appropriate multipart boundaries for file uploads.
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        logger.debug(f"Request headers: {json.dumps(headers, indent=2)}")
        return headers

    def get(self, base_url, endpoint, params=None, raw=False):
        """
        Sends a GET request to the specified API endpoint.
        - base_url: The base URL for the API.
        - endpoint: The specific API endpoint to interact with.
        - params: Optional query parameters to include in the request.
        - raw: If True, returns the raw response body; otherwise, returns parsed JSON.
        """
        url = f"{base_url}{endpoint}"
        logger.debug(f"Sending GET request to: {url}")
        logger.debug(f"GET request params: {json.dumps(params, indent=2)}")
        
        return self._send_request("GET", url, params=params, raw=raw)

    def post(self, base_url, endpoint, data=None, files=None, raw=False):
        """
        Sends a POST request to the specified API endpoint.
        - base_url: The base URL for the API.
        - endpoint: The specific API endpoint to interact with.
        - data: Optional JSON payload to include in the request body.
        - files: Optional file payload for multipart requests.
        - raw: If True, returns the raw response body; otherwise, returns parsed JSON.
        """
        url = f"{base_url}{endpoint}"
        logger.debug(f"Sending POST request to: {url}")
        try:
            logger.debug(f"POST request data: {json.dumps(data, indent=2)}")
        except Exception:
            logger.debug("POST request data: <non-serializable or None>")
        logger.debug(f"POST request files: {files is not None}")
        return self._send_request("POST", url, json=data if not files else None, files=files, data=data if files else None, raw=raw)

    def put(self, base_url, endpoint, data=None, raw=False):
        """
        Sends a PUT request to the specified API endpoint.
        - base_url: The base URL for the API.
        - endpoint: The specific API endpoint to interact with.
        - data: Optional JSON payload to include in the request body.
        - raw: If True, returns the raw response body; otherwise, returns parsed JSON.
        """
        url = f"{base_url}{endpoint}"
        logger.debug(f"Sending PUT request to: {url}")
        logger.debug(f"PUT request data: {json.dumps(data, indent=2)}")
        
        return self._send_request("PUT", url, json=data, raw=raw)

    def patch(self, base_url, endpoint, data=None, raw=False):
        """
        Sends a PATCH request to the specified API endpoint.
        - base_url: The base URL for the API.
        - endpoint: The specific API endpoint to interact with.
        - data: Optional JSON payload to include in the request body.
        - raw: If True, returns the raw response body; otherwise, returns parsed JSON.
        """
        url = f"{base_url}{endpoint}"
        logger.debug(f"Sending PATCH request to: {url}")
        logger.debug(f"PATCH request data: {json.dumps(data, indent=2)}")
        
        return self._send_request("PATCH", url, json=data, raw=raw)

    def delete(self, base_url, endpoint, params=None, raw=False):
        """
        Sends a DELETE request to the specified API endpoint.
        - base_url: The base URL for the API.
        - endpoint: The specific API endpoint to interact with.
        - params: Optional query parameters to include in the request.
        - raw: If True, returns the raw response body; otherwise, returns parsed JSON.
        """
        url = f"{base_url}{endpoint}"
        logger.debug(f"Sending DELETE request to: {url}")
        return self._send_request("DELETE", url, params=params, raw=raw)

    def _send_request(self, method, url, params=None, json=None, files=None, data=None, raw=False):
        """
        Internal helper to send HTTP requests with retries and 401 refresh.
        Retries on 429 and 5xx responses, and on common transient exceptions.
        On 401, re-authenticates once and retries immediately.
        """
        filtered_params = {k: v for k, v in (params or {}).items() if v is not None}
        filtered_json = {k: v for k, v in (json or {}).items() if v is not None} if json else None
        filtered_data = {k: v for k, v in (data or {}).items() if v is not None} if data else None

        # Attempt counter for retryable status codes
        for attempt in range(0, MAX_RETRIES + 1):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=self._get_headers(),
                    params=filtered_params if filtered_params else None,
                    json=filtered_json if (files is None) else None,
                    files=files,
                    data=filtered_data if files else None,
                    timeout=REQUEST_TIMEOUT_SECONDS
                )

                status = response.status_code

                # Handle 401: try to refresh token once per request
                if status == 401:
                    logger.warning("Received 401 Unauthorized. Attempting to refresh token and retry once.")
                    self._authenticate()
                    response = requests.request(
                        method,
                        url,
                        headers=self._get_headers(),
                        params=filtered_params if filtered_params else None,
                        json=filtered_json if (files is None) else None,
                        files=files,
                        data=filtered_data if files else None,
                        timeout=REQUEST_TIMEOUT_SECONDS
                    )
                    status = response.status_code

                # Retry on 429 or 5xx
                if status == 429 or (500 <= status < 600):
                    if attempt < MAX_RETRIES:
                        retry_after_header = response.headers.get('Retry-After')
                        if retry_after_header:
                            try:
                                wait_seconds = float(retry_after_header)
                            except ValueError:
                                wait_seconds = BACKOFF_BASE_SECONDS * (2 ** attempt)
                        else:
                            wait_seconds = BACKOFF_BASE_SECONDS * (2 ** attempt)
                        # Add small jitter
                        wait_seconds += random.uniform(0, 0.5)
                        logger.warning(f"HTTP {status} received. Retrying in {wait_seconds:.2f}s (attempt {attempt + 1}/{MAX_RETRIES}).")
                        time.sleep(wait_seconds)
                        continue

                # Log and return via common handler
                logger.debug(f"{method} response status code: {response.status_code}")
                logger.debug(f"{method} response headers: {json.dumps(dict(response.headers), indent=2)}")
                logger.debug(f"{method} response body: {response.text}")
                return self._handle_response(response, raw=raw)

            except (ConnectionError, Timeout, RequestException) as err:
                if attempt < MAX_RETRIES:
                    wait_seconds = BACKOFF_BASE_SECONDS * (2 ** attempt) + random.uniform(0, 0.5)
                    logger.warning(f"{method} {url} failed due to network error: {err}. Retrying in {wait_seconds:.2f}s (attempt {attempt + 1}/{MAX_RETRIES}).")
                    time.sleep(wait_seconds)
                    continue
                logger.error(f"{method} {url} failed after retries due to network error: {err}")
                return None
            except Exception as e:
                logger.error(f"{method} {url} unexpected error: {e}")
                return None

        # Should not reach here
        logger.error(f"{method} {url} exhausted retries without success.")
        return None

    def _handle_response(self, response, raw=False):
        """
        Handles the response from an API request, raising exceptions for HTTP errors
        and parsing the response body as JSON (unless raw=True is specified).
        - response: The HTTP response object.
        - raw: If True, returns the raw response body; otherwise, parses as JSON.
        """
        try:
            # Raise an exception if the response contains an HTTP error status code.
            response.raise_for_status()
            
            if raw:
                return response.text  # Return raw text if specified.
            
            return self._parse_json(response)  # Parse JSON by default.
        except HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - {response.text}")
            return None
        except ValueError as val_err:
            logger.error(f"JSON decoding error: {val_err}")
            return None
        except Exception as err:
            logger.error(f"An error occurred when handling the response: {err}")
            return None

    def _parse_json(self, response):
        """
        Safely parses the JSON content of a response, handling content-type validation
        and logging errors for unexpected or invalid content.
        - response: The HTTP response object to parse.
        Returns the parsed JSON object or an empty dictionary if parsing fails.
        """
        try:
            # Ensure the response content-type is JSON before attempting to parse.
            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()  # Parse the response body as JSON.
            else:
                logger.error(f"Unexpected content type: {response.headers.get('Content-Type')}")
                return {}
        except ValueError as val_err:
            # Log the JSON parsing error and return an empty dictionary.
            logger.error(f"Error parsing JSON: {val_err}")
            return {}
