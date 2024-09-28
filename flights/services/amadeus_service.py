# The `AmadeusAPI` class in Python handles authentication and fetching flight offers from the Amadeus
# API with error handling and caching.
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from django.conf import settings
from django.core.cache import cache



class AmadeusAPI:
    """
    The `AmadeusAPI` class is responsible for handling authentication and fetching flight offers from
    the Amadeus API. It provides methods for retrieving access tokens, fetching flight offers, and
    handling errors and caching.
    """
    def __init__(self):
       
        self.client_id = settings.AMADEUS_CLIENT_ID
        self.client_secret = settings.AMADEUS_CLIENT_SECRET
        self.token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        self.api_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def get_access_token(self):
        """
        The function `get_access_token` retrieves an access token using client credentials and caches it
        for future use, handling potential errors gracefully.
        :return: The `get_access_token` method returns the access token retrieved from the token URL. If
        there is an error during the process of fetching the token, it returns `None`.
        """
        try:
            # Check if the token URL is in the cache
            cached_data = cache.get(self.token_url)
            if cached_data:
                return cached_data

            # Create the payload for the token request
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            # Send the token request and handle potential errors    
            response = requests.post(self.token_url, data=payload, timeout=10)  # Add timeout for the request
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            # Cache the access token for 30 minutes
            cache.set(self.token_url, response.json().get('access_token'), timeout=60 * 30)
            # Return the access token
            return response.json().get('access_token')
        except (RequestException, Timeout, HTTPError) as e:
            print(f"Failed to retrieve access token: {e}")
            return None  # Return None if there's an error fetching the token

    def fetch_flight_offers(self, origin, destination, departure_date, adults=1):
        """
        The function fetches flight offers using an API, handling errors and returning relevant data or
        error messages.
        
        :param origin: The `origin` parameter in the `fetch_flight_offers` function represents the
        location code of the origin airport from which the flight will depart. It is used to specify the
        starting point of the flight search
        :param destination: Destination is the airport code or location code where the flight will
        arrive. It is the location to which the passenger is traveling
        :param departure_date: The `departure_date` parameter in the `fetch_flight_offers` function is
        used to specify the date of departure for the flight offers being fetched. It is a required
        parameter and should be provided in the format specified by the API you are interacting with
        (e.g., YYYY-MM-DD). This date
        :param adults: The `adults` parameter in the `fetch_flight_offers` function represents the
        number of adult passengers for whom flight offers are being fetched. By default, it is set to 1,
        but you can specify a different number if needed. This parameter allows the function to
        customize the flight search based, defaults to 1 (optional)
        :return: The `fetch_flight_offers` method returns flight data if available in the API response,
        or an error message if there was an issue during the process of fetching flight offers.
        """
        # Get the access token
        token = self.get_access_token()
        # Check if the access token is available
        if not token:
            return {"error": "Could not fetch access token."}  # Early exit if token retrieval fails
        # Create the headers and parameters for the API request
        headers = {'Authorization': f'Bearer {token}'}
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': adults,
            'max': 1
        }
        try:
            # Send the API request and handle potential errors
            response = requests.get(self.api_url, headers=headers, params=params, timeout=10)
            # Raises an HTTPError for 4xx or 5xx responses
            response.raise_for_status()
            # Check if the response contains flight data
            data = response.json()
            # Check if the response contains flight data
            if 'data' not in data:
                return {"error": "No flight data found in API response."}
            # Return the flight data
            return data['data']
        # Handle errors
        except (RequestException, Timeout, HTTPError) as e:
            print(f"Failed to fetch flight offers: {e}")
            return {"error": "Failed to fetch flight offers due to an error."}
