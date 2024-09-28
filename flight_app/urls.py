from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Define the schema view for the Swagger UI
schema_view = get_schema_view(
    openapi.Info(
        title="Flight API",
        default_version='v1',
        description="API documentation for the Flight app",
        terms_of_service="",
        contact=openapi.Contact(email="itsprateekkumarmohanty@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Define the URL patterns for the API
urlpatterns = [
    path('flights/', include('flights.urls')), # Include the flights URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # ReDoc
]
