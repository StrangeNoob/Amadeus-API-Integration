from django.urls import path
from .views import FlightPriceView, PingView

urlpatterns = [
    path('ping/', PingView.as_view(), name='ping'),
    path('price/', FlightPriceView.as_view(), name='flight-price')
]
