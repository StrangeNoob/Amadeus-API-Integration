from rest_framework import serializers

class FlightOfferSerializer(serializers.Serializer):
    price = serializers.CharField()
    origin = serializers.CharField()
    destination = serializers.CharField()
    departure_date = serializers.DateField()
    return_date = serializers.DateField(required=False)

    def to_representation(self, instance):
        itinerary = instance['itineraries'][0] if 'itineraries' in instance and instance['itineraries'] else {}
        departure = itinerary['segments'][0]['departure'] if 'segments' in itinerary and itinerary['segments'] else {}
        arrival = itinerary['segments'][-1]['arrival'] if 'segments' in itinerary and itinerary['segments'] else {}
        price_data = instance['price']

        location_dict = self.context.get('location_dict', {})

        destination_iata = arrival.get('iataCode', 'N/A')
        destination_city = location_dict.get(destination_iata, {}).get('cityCode', destination_iata)

        return {
            'origin': departure.get('iataCode', 'N/A'),
            'destination': destination_city,
            'departure_date': departure.get('at', '').split('T')[0],
            'price': f"{price_data.get('total', 'N/A')} {price_data.get('currency', 'N/A')}"
        }

