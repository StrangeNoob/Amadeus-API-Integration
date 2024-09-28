# Flight Price API

This project is a **Flight Price API** that allows users to search for flight offers between origin and destination airports, using a specific travel date. The API integrates with the Amadeus API to fetch real-time flight data. It also provides a caching mechanism using Redis to reduce the number of external API calls and improve performance. The API is documented using **Swagger**, allowing easy exploration and testing of endpoints.

## Features

- Fetch flight offers between origin and destination airports.
- Caching using Redis to avoid unnecessary API calls.
- Swagger UI for API documentation and testing.
- No-cache parameter support for forcing fresh data retrieval.
- Simple response format with flight details such as origin, destination, price, and departure date.

## Getting Started

To get started, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/strangenoob/flight-price-api.git
   cd flight-price-api
   ```

2. **Create a .env file**:

   Copy the .env.example file to .env and fill in the required values:

   ```bash
   cp .env.example .env
   ```

3. **Update the .env file with your Amadeus API credentials, Django Secret Key, and Redis URL**:

   ```bash
   # Update the .env file with your Amadeus API credentials
   AMADEUS_CLIENT_ID=your_amadeus_client_id
   AMADEUS_CLIENT_SECRET=your_amadeus_client_secret

   # Update the .env file with your Django Secret Key
   SECRET_KEY=your_django_secret_key

   # Update the .env file with your Redis URL
   REDIS_URL=redis://your_redis_url
   # (Example: redis://localhost:6379/1 for local development, redis://redis:6379/1 for docker-compose, etc.)

   # Update the .env file with your allowed hosts
   ALLOWED_HOSTS=your_allowed_hosts (comma-separated list)
   # (Example: ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0 for local development, ALLOWED_HOSTS=0.0.0.0 for docker-compose, etc.)

   # Update the .env file with your debug mode
   DEBUG=True
   ```

## Installation

You can install the project dependencies using both local and Docker-based installation methods.

### Local Installation

1. **Create and activate a Python virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install the project dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run Django migrations**:

   ```bash
   python manage.py migrate
   ```

4. **Run Redis server**:

   - If Redis is installed locally, run it using the following command:

     ```bash
     redis-server
     ```

   - If Redis is installed using Docker, run it using the following command:

     ```bash
     docker-compose up -d
     ```

5. **Run the Django development server**:

   ```bash
   python manage.py runserver
   ```

6. **Access the API and Swagger UI**:

   - API Base URL: http://localhost:8000/
   - Swagger UI: http://localhost:8000/swagger/

### Docker Installation

1. **Build the Docker image**:

   ```bash
   docker-compose build
   ```

2. **Run the Docker container**:

   ```bash
   docker-compose up
   ```

3. **Access the API and Swagger UI**:

   - API Base URL: http://localhost:8000/
   - Swagger UI: http://localhost:8000/swagger/

## Usage

To interact with the API, you can use the Swagger UI or make HTTP requests directly. The Swagger UI provides a user-friendly interface for exploring and testing the API endpoints.

### Swagger UI

The Swagger UI is available at http://localhost:8000/swagger/. You can use it to explore the API endpoints, test different request parameters, and view the API documentation.

### HTTP Requests

To interact with the Flight Price API, you can make requests to the following endpoint:

- Get Flight Prices: /flights/price/

#### Example Request

```http
GET /flights/price/?origin=JFK&destination=LAX&date=2024-12-01
```

#### Example Response

```json
{
  "data": {
    "origin": "JFK",
    "destination": "LAX",
    "departure_date": "2024-12-01",
    "price": "250 USD"
  }
}
```

#### Force Fresh Data (No Cache)

You can add the nocache=1 parameter to the request to force the API to fetch fresh data from Amadeus and bypass the cache:

```http
GET /flights/price/?origin=JFK&destination=LAX&date=2024-12-01&nocache=1
```

## Known Issues

- The Amadeus API has rate limits, so repeated calls may result in limited or delayed responses.
- Cache is invalidated after 10 minutes.
