# amadeus_client.py
import requests
import base64
from config import Config

class AmadeusClient:
    def __init__(self):
        self.base_url = Config.AMADEUS_BASE_URL
        self.access_token = None
        self.authenticated = False
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Amadeus API"""
        if not Config.AMADEUS_API_KEY or not Config.AMADEUS_API_SECRET:
            print("⚠️  Amadeus API credentials not found. Using sample data.")
            return
        
        try:
            credentials = f"{Config.AMADEUS_API_KEY}:{Config.AMADEUS_API_SECRET}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            response = requests.post(
                f"{self.base_url}/v1/security/oauth2/token",
                headers=headers,
                data={'grant_type': 'client_credentials'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.authenticated = True
                print("✅ Amadeus API authentication successful!")
            else:
                print(f"❌ Amadeus authentication failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error authenticating: {e}")
    
    def get_airport_code(self, location):
        """Convert city name to IATA airport code"""
        location_lower = location.lower().strip()
        
        # Common city to airport mappings
        city_map = {
            'berlin': 'BER',
            'athens': 'ATH',
            'athens': 'ATH',
            'paris': 'CDG',
            'london': 'LHR',
            'rome': 'FCO',
            'new york': 'JFK',
            'los angeles': 'LAX',
            'chicago': 'ORD',
            'tokyo': 'HND',
            'dubai': 'DXB',
            'singapore': 'SIN',
            'sydney': 'SYD',
            'madrid': 'MAD',
            'frankfurt': 'FRA',
            'amsterdam': 'AMS',
            'barcelona': 'BCN',
            'milan': 'MXP',
            'munich': 'MUC',
            'vienna': 'VIE',
            'zurich': 'ZRH',
            'brussels': 'BRU',
            'copenhagen': 'CPH',
            'stockholm': 'ARN',
            'oslo': 'OSL',
            'helsinki': 'HEL',
            'dublin': 'DUB',
            'manchester': 'MAN',
            'edinburgh': 'EDI',
            'lisbon': 'LIS',
            'istanbul': 'IST',
            'moscow': 'SVO',
            'beijing': 'PEK',
            'shanghai': 'PVG',
            'hong kong': 'HKG',
            'seoul': 'ICN',
            'bangkok': 'BKK',
            'mumbai': 'BOM',
            'delhi': 'DEL',
            'doha': 'DOH',
            'abu dhabi': 'AUH',
            'riyadh': 'RUH',
            'cairo': 'CAI',
            'johannesburg': 'JNB',
            'nairobi': 'NBO',
            'mexico city': 'MEX',
            'sao paulo': 'GRU',
            'buenos aires': 'EZE',
            'santiago': 'SCL',
            'lima': 'LIM',
            'bogota': 'BOG'
        }
        
        # Check if already a 3-letter code
        if len(location) == 3 and location.isalpha() and location.isupper():
            return location
        
        # Check city map
        for city, code in city_map.items():
            if location_lower == city or location_lower in city or city in location_lower:
                return code
        
        # Fallback: take first 3 letters uppercase
        return location[:3].upper()
    
    def search_flights(self, origin, destination, departure_date, adults=1, return_date=None):
        """Search for flights using Amadeus API or sample data"""
        print(f"🔍 Searching flights: {origin} → {destination} on {departure_date}")
        
        # Convert to airport codes
        origin_code = self.get_airport_code(origin)
        destination_code = self.get_airport_code(destination)
        print(f"   Airport codes: {origin_code} → {destination_code}")
        
        # If not authenticated, return sample data
        if not self.authenticated:
            print("   Using sample flight data")
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            params = {
                'originLocationCode': origin_code,
                'destinationLocationCode': destination_code,
                'departureDate': departure_date,
                'adults': adults,
                'max': 5,
                'currencyCode': 'EUR'
            }
            
            if return_date:
                params['returnDate'] = return_date
            
            response = requests.get(
                f"{self.base_url}/v2/shopping/flight-offers",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f" Found {len(data.get('data', []))} real flights!")
                return data
            else:
                print(f" API Error: {response.status_code}")
                
                
        except Exception as e:
            print(f" Error: {e}")



    def search_activities(self, location, radius=5):
        """Search for tours and activities around a location"""
        print(f"🔍 Searching activities around: {location}")
        
        # Get coordinates for the location (using a simple mapping or geocoding API)
        # For now, using coordinates for major cities
        city_coordinates = {
            'barcelona': {'latitude': 41.397158, 'longitude': 2.160873},
            'madrid': {'latitude': 40.41436995, 'longitude': -3.69170868},
            'paris': {'latitude': 48.8566, 'longitude': 2.3522},
            'rome': {'latitude': 41.9028, 'longitude': 12.4964},
            'london': {'latitude': 51.5074, 'longitude': -0.1278},
            'berlin': {'latitude': 52.5200, 'longitude': 13.4050},
            'athens': {'latitude': 37.9838, 'longitude': 23.7275},
            'new york': {'latitude': 40.7128, 'longitude': -74.0060},
            'tokyo': {'latitude': 35.6762, 'longitude': 139.6503},
            'sydney': {'latitude': -33.8688, 'longitude': 151.2093},
            'dubai': {'latitude': 25.2048, 'longitude': 55.2708},
        }
        
        location_lower = location.lower().strip()
        coordinates = city_coordinates.get(location_lower)
        
        if not coordinates:
            print(f"   No coordinates found for {location}. Using Barcelona as default.")
            coordinates = city_coordinates.get('barcelona', {'latitude': 41.397158, 'longitude': 2.160873})
        
        # If not authenticated, return sample data
        if not self.authenticated:
            print("  NO activities data")
          
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            params = {
                'latitude': coordinates['latitude'],
                'longitude': coordinates['longitude'],
                'radius': radius
            }
            
            response = requests.get(
                f"{self.base_url}/v1/shopping/activities",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Found {len(data.get('data', []))} activities!")
                return data
            else:
                print(f"   API Error: {response.status_code}")
               
                
        except Exception as e:
            print(f"   Error: {e}")

    def search_hotels(self, city_code, radius=5, radius_unit='KM', amenities=None, ratings=None):
        """Search for hotels in a city using Amadeus API"""
        print(f"🔍 Searching hotels in: {city_code}")
        
        # If not authenticated, return sample data
        if not self.authenticated:
            print("   Using sample hotel data")
            # Return sample hotel data structure
            return {
                '_is_sample': True,
                'data': [
                    {
                        'name': f'Sample Hotel 1 in {city_code}',
                        'hotelId': 'SAMPLE001',
                        'chainCode': 'SH',
                        'address': {
                            'cityName': city_code,
                            'lines': ['123 Sample Street']
                        },
                        'geoCode': {
                            'latitude': 0.0,
                            'longitude': 0.0
                        },
                        'distance': {
                            'value': 0.5,
                            'unit': 'KM'
                        }
                    },
                    {
                        'name': f'Sample Hotel 2 in {city_code}',
                        'hotelId': 'SAMPLE002',
                        'chainCode': 'SH',
                        'address': {
                            'cityName': city_code,
                            'lines': ['456 Sample Avenue']
                        },
                        'geoCode': {
                            'latitude': 0.0,
                            'longitude': 0.0
                        },
                        'distance': {
                            'value': 1.2,
                            'unit': 'KM'
                        }
                    }
                ]
            }
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            params = {
                'cityCode': city_code,
                'radius': radius,
                'radiusUnit': radius_unit,
                'hotelSource': 'ALL'
            }
            
            # Add optional parameters if provided
            if amenities:
                params['amenities'] = ','.join(amenities)
            if ratings:
                params['ratings'] = ','.join(ratings)
            
            response = requests.get(
                f"{self.base_url}/v1/reference-data/locations/hotels/by-city",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Found {len(data.get('data', []))} hotels!")
                return data
            else:
                print(f"   API Error: {response.status_code}")
                return {'data': []}
                
        except Exception as e:
            print(f"   Error: {e}")
            return {'data': []}
        
    def get_weather_forecast(self, city_name, start_date, end_date):
        """Get weather forecast from Open-Meteo API"""
        print(f"🌤️  Getting weather forecast for: {city_name} ({start_date} to {end_date})")
        
        # Map cities to coordinates (you can expand this)
        city_coordinates = {
            'berlin': {'latitude': 52.52, 'longitude': 13.41},
            'paris': {'latitude': 48.8566, 'longitude': 2.3522},
            'london': {'latitude': 51.5074, 'longitude': -0.1278},
            'rome': {'latitude': 41.9028, 'longitude': 12.4964},
            'new york': {'latitude': 40.7128, 'longitude': -74.0060},
            'los angeles': {'latitude': 34.0522, 'longitude': -118.2437},
            'tokyo': {'latitude': 35.6762, 'longitude': 139.6503},
            'dubai': {'latitude': 25.2048, 'longitude': 55.2708},
            'singapore': {'latitude': 1.3521, 'longitude': 103.8198},
            'sydney': {'latitude': -33.8688, 'longitude': 151.2093},
            'madrid': {'latitude': 40.4168, 'longitude': -3.7038},
            'barcelona': {'latitude': 41.3851, 'longitude': 2.1734},
            'athens': {'latitude': 37.9838, 'longitude': 23.7275},
            'frankfurt': {'latitude': 50.1109, 'longitude': 8.6821},
            'amsterdam': {'latitude': 52.3676, 'longitude': 4.9041},
            'milan': {'latitude': 45.4642, 'longitude': 9.1900},
            'munich': {'latitude': 48.1351, 'longitude': 11.5820},
            'vienna': {'latitude': 48.2082, 'longitude': 16.3738},
            'zurich': {'latitude': 47.3769, 'longitude': 8.5417},
            'brussels': {'latitude': 50.8503, 'longitude': 4.3517},
        }
        
        location_lower = city_name.lower().strip()
        coordinates = city_coordinates.get(location_lower)
        
        if not coordinates:
            print(f"   No coordinates found for {city_name}. Using default.")
            coordinates = {'latitude': 52.52, 'longitude': 13.41}  # Berlin default
        
        try:
            # Open-Meteo API URL
            url = "https://api.open-meteo.com/v1/forecast"
            
            params = {
                'latitude': coordinates['latitude'],
                'longitude': coordinates['longitude'],
                'hourly': 'temperature_2m,weathercode',
                'start_date': start_date,
                'end_date': end_date,
                'timezone': 'auto'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Weather data retrieved for {len(data.get('hourly', {}).get('time', [])) // 24} days")
                return data
            else:
                print(f"   Weather API Error: {response.status_code}")
                return self._get_sample_weather(start_date, end_date)
                
        except Exception as e:
            print(f"   Weather Error: {e}")
            return self._get_sample_weather(start_date, end_date)
        
        def _get_sample_weather(self, start_date, end_date):
            """Generate sample weather data when API fails"""
            print("   Using sample weather data")
            return {
                '_is_sample': True,
                'latitude': 52.52,
                'longitude': 13.41,
                'hourly_units': {
                    'time': 'iso8601',
                    'temperature_2m': '°C'
                },
                'hourly': {
                    'time': [f"{start_date}T12:00", f"{end_date}T12:00"],
                    'temperature_2m': [22, 24]
                }
            }
                


                
    
  