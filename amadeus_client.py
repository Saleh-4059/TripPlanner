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
            'athen': 'ATH',
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
            return self._get_sample_flights(origin_code, destination_code, departure_date, adults)
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            params = {
                'originLocationCode': origin_code,
                'destinationLocationCode': destination_code,
                'departureDate': departure_date,
                'adults': adults,
                'max': 5,
                'currencyCode': 'USD'
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
                print(f"✅ Found {len(data.get('data', []))} real flights!")
                return data
            else:
                print(f"❌ API Error: {response.status_code}")
                return self._get_sample_flights(origin_code, destination_code, departure_date, adults)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._get_sample_flights(origin_code, destination_code, departure_date, adults)
    
    def _get_sample_flights(self, origin, destination, date, adults):
        """Generate realistic sample flight data"""
        airlines = ['American Airlines', 'Delta Airlines', 'United Airlines', 'Lufthansa', 'British Airways']
        prices = [299.99, 349.99, 399.99, 449.99, 499.99]
        
        flights = []
        for i in range(3):
            flights.append({
                'id': f'sample_{i}',
                'price': {'total': f'{prices[i]}', 'currency': 'USD'},
                'itineraries': [{
                    'duration': f'PT{i+4}H{i*10}M',
                    'segments': [{
                        'departure': {
                            'iataCode': origin,
                            'at': f'{date}T{8+i}:00:00'
                        },
                        'arrival': {
                            'iataCode': destination,
                            'at': f'{date}T{12+i}:00:00'
                        },
                        'carrierCode': airlines[i][:2].upper(),
                        'number': f'{100 + i}',
                        'duration': f'PT{i+4}H'
                    }]
                }],
                'travelerPricings': [{
                    'travelerId': '1',
                    'price': {'total': f'{prices[i]}'}
                }]
            })
        
        return {
            'meta': {'count': len(flights)},
            'data': flights,
            'dictionaries': {
                'carriers': {'AA': 'American Airlines', 'DL': 'Delta', 'UA': 'United', 'LH': 'Lufthansa', 'BA': 'British Airways'}
            },
            '_is_sample': True
        }