import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from django.conf import settings
from django.core.cache import cache


class AmadeusAPI:
    def __init__(self):
        self.client_id = settings.AMADEUS_CLIENT_ID
        self.client_secret = settings.AMADEUS_CLIENT_SECRET
        self.token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        self.api_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def get_access_token(self):
        try:

            cached_data = cache.get(self.token_url)
            if cached_data:
                return cached_data

            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            response = requests.post(self.token_url, data=payload, timeout=10)  # Add timeout for the request
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            cache.set(self.token_url, response.json().get('access_token'), timeout=60 * 30)
            return response.json().get('access_token')
        except (RequestException, Timeout, HTTPError) as e:
            print(f"Failed to retrieve access token: {e}")
            return None  # Return None if there's an error fetching the token

    def fetch_flight_offers(self, origin, destination, departure_date, adults=1):
        token = self.get_access_token()
        if not token:
            return {"error": "Could not fetch access token."}  # Early exit if token retrieval fails

        headers = {'Authorization': f'Bearer {token}'}
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': adults,
            'max': 1
        }

        try:
            response = requests.get(self.api_url, headers=headers, params=params, timeout=10)  # Add timeout
            response.raise_for_status()  # Raises an HTTPError for 4xx or 5xx responses
            data = response.json()
            if 'data' not in data:
                return {"error": "No flight data found in API response."}
            return data['data']
        except (RequestException, Timeout, HTTPError) as e:
            print(f"Failed to fetch flight offers: {e}")
            return {"error": "Failed to fetch flight offers due to an error."}  # Return a meaningful error response
