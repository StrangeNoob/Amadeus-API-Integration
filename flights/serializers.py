# The FlightOfferSerializer class defines a serializer for flight offers with fields for price,
# origin, destination, departure date, and return date.
from rest_framework import serializers

class FlightOfferSerializer(serializers.Serializer):
    # These lines of code are defining the fields for the FlightOfferSerializer class. Each field
    # corresponds to a specific attribute of a flight offer object. Here's a breakdown of each field:
    price = serializers.CharField()
    origin = serializers.CharField()
    destination = serializers.CharField()
    departure_date = serializers.DateField()
    return_date = serializers.DateField(required=False)

    def to_representation(self, instance):
        # This method is responsible for converting the flight offer object into a dictionary
        # representation. It iterates through the itineraries and segments of the flight offer,
        # extracting the departure and arrival information, and then formats the data into a
        # dictionary with the necessary fields. 
        itinerary = instance['itineraries'][0] if 'itineraries' in instance and instance['itineraries'] else {}
        departure = itinerary['segments'][0]['departure'] if 'segments' in itinerary and itinerary['segments'] else {}
        arrival = itinerary['segments'][-1]['arrival'] if 'segments' in itinerary and itinerary['segments'] else {}
        price_data = instance['price']

        # This line of code retrieves the location dictionary from the context, which is a dictionary
        # containing information about the locations in the flight offer. It uses the destination
        # airport code to retrieve the city name.
        location_dict = self.context.get('location_dict', {})

        # This line of code retrieves the destination airport code from the arrival segment of the
        # flight offer. It then uses the location dictionary to retrieve the city name for the
        # destination airport.
        destination_iata = arrival.get('iataCode', 'N/A')
        destination_city = location_dict.get(destination_iata, {}).get('cityCode', destination_iata)

        # This line of code returns a dictionary containing the origin, destination, departure date,
        # and price information for the flight offer. It also includes the destination city name
        # retrieved from the location dictionary.
        return {
            'origin': departure.get('iataCode', 'N/A'),
            'destination': destination_city,
            'departure_date': departure.get('at', '').split('T')[0],
            'price': f"{price_data.get('total', 'N/A')} {price_data.get('currency', 'N/A')}"
        }

