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
    def get(self, request):
        return Response({"data": "pong"}, status=status.HTTP_200_OK)

class FlightPriceView(APIView):


    def validate_parameters(self, origin, destination, date):

        if not (origin.isupper() and destination.isupper()):
            return False, "Origin and destination IATA codes must be in all caps."

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
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        date = request.query_params.get('date')
        nocache = request.query_params.get('nocache')


        if not origin or not destination or not date:
            return Response({"error": "Missing required parameters: origin, destination, or date."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        valid, error_message = self.validate_parameters(origin, destination, date)
        if not valid:
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        
        cache_key = f"{origin}_{destination}_{date}"
        cached_data = cache.get(cache_key)

        if nocache != '1':
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response({ "data": cached_data }, status=status.HTTP_200_OK)

        amadeus = AmadeusAPI()
        flight_data = amadeus.fetch_flight_offers(origin, destination, date)

        if "error" in flight_data:
            return Response({"error": flight_data['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if isinstance(flight_data, list) and len(flight_data) > 0:
            flight_offer = flight_data[0]
            serializer = FlightOfferSerializer(flight_offer)
            response_data = serializer.data
            cache.set(cache_key, response_data, timeout=60 * 10)
            return Response({"data": response_data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Unexpected response format from API."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
