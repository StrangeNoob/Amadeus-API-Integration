from django.urls import path
from .views import FlightPriceView, PingView

# API URLs for the Flight Price API
urlpatterns = [
    path('ping/', PingView.as_view(), name='ping'),  # Ping endpoint for health checks
    path('price/', FlightPriceView.as_view(), name='flight-price')  # Flight price endpoint
]
