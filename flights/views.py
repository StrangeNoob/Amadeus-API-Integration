from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.cache import cache
import re
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi  
from .services.amadeus_service import AmadeusAPI
from .serializers import FlightOfferSerializer


class PingView(APIView):
    """
    The `PingView` class is a simple view that returns a JSON response with a "data" key set to "pong".
    This view is used to check if the API is running and responding to requests.
    """
    def get(self, request):
        return Response({"data": "pong"}, status=status.HTTP_200_OK)

class FlightPriceView(APIView):
    """
    The `FlightPriceView` class is a view that handles requests to fetch flight prices between two
    specified locations and a given date. It uses the `AmadeusAPI` class to fetch flight offers and
    the `FlightOfferSerializer` class to serialize the data into a format that can be easily consumed
    by the client.
    """

    def validate_parameters(self, origin, destination, date):
        """
        The `validate_parameters` method is a helper function that validates the parameters passed to
        the `FlightPriceView` view. It checks if the origin and destination IATA codes are in all caps,
        and if the date is in the correct format. If any of the validations fail, it returns `False`
        along with an error message.
        
        :param origin: The `origin` parameter is the IATA code of the origin airport.
        :param destination: The `destination` parameter is the IATA code of the destination airport.
        :param date: The `date` parameter is the date of departure for the flight offers being fetched.
        :return: The `validate_parameters` method returns `True` if all the parameters are valid, along
        with an empty string. If any of the parameters are invalid, it returns `False` along with an
        error message.
        """
        # Check if the origin and destination IATA codes are in all caps
        if not (origin.isupper() and destination.isupper()):
            return False, "Origin and destination IATA codes must be in all caps."
        # Check if the date is in the correct format
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, date):
            return False, "Date must be in the format YYYY-MM-DD."

        return True, ""
    

    @swagger_auto_schema(
        operation_description="Get flight prices between origin and destination",
        responses={200: 'Flight price details returned'},
        manual_parameters=[
            openapi.Parameter('origin', openapi.IN_QUERY, description="Origin IATA code", type=openapi.TYPE_STRING),
            openapi.Parameter('destination', openapi.IN_QUERY, description="Destination IATA code", type=openapi.TYPE_STRING),
            openapi.Parameter('date', openapi.IN_QUERY, description="Travel date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('nocache', openapi.IN_QUERY, description="Set to 1 to bypass cache and fetch fresh data", type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def get(self, request):
        """
        The `get` method is the main entry point for the `FlightPriceView` view. It retrieves the
        origin, destination, and date parameters from the request query parameters, validates them,
        and then fetches flight offers using the `AmadeusAPI` class. It then serializes the flight
        offers using the `FlightOfferSerializer` class and returns the response.
        
        :param request: The `request` parameter is an instance of the `Request` class, which represents
        an HTTP request made to the server. It contains information about the request, such as the
        query parameters, headers, and body.
        :return: The `get` method returns a response containing the serialized flight offers, along with
        an HTTP status code.        
        """
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        date = request.query_params.get('date')
        nocache = request.query_params.get('nocache')


        # Check if the origin, destination, and date parameters are present in the request
        if not origin or not destination or not date:
            return Response({"error": "Missing required parameters: origin, destination, or date."},
                            status=status.HTTP_400_BAD_REQUEST)
        # Validate the parameters
        valid, error_message = self.validate_parameters(origin, destination, date)
        if not valid:
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the cache is enabled and if the cache key exists
        cache_key = f"{origin}_{destination}_{date}"
        cached_data = cache.get(cache_key)

        # If the cache is enabled and the cache key exists, return the cached data
        if nocache != '1':
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response({ "data": cached_data }, status=status.HTTP_200_OK)

        # Fetch flight offers from the Amadeus API
        amadeus = AmadeusAPI()
        flight_data = amadeus.fetch_flight_offers(origin, destination, date)

        # Check if there was an error fetching flight offers
        if "error" in flight_data:
            return Response({"error": flight_data['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check if the response is a list and if there are flight offers available
        if isinstance(flight_data, list) and len(flight_data) > 0:
            flight_offer = flight_data[0]
            # Serialize the flight offer using the FlightOfferSerializer class
            serializer = FlightOfferSerializer(flight_offer)
            # Cache the serialized flight offer for 10 minutes
            response_data = serializer.data
            cache.set(cache_key, response_data, timeout=60 * 10)
            # Return the serialized flight offer
            return Response({"data": response_data}, status=status.HTTP_200_OK)
        # If the response is not a list or there are no flight offers available, return an error
        else:
            return Response({"error": "Unexpected response format from API."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
