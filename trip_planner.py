# trip_planner.py
from amadeus_client import AmadeusClient
from datetime import datetime

class TripPlanner:
    def __init__(self):
        self.amadeus = AmadeusClient()
        print("✅ TripPlanner initialized")
    
    def create_trip_plan(self, user_input):
        """Create complete trip plan"""
        print(f"📝 Creating trip plan...")
        
        # Get airport codes
        origin_code = self.amadeus.get_airport_code(user_input.get('origin', ''))
        destination_code = self.amadeus.get_airport_code(user_input.get('destination', ''))
        
        trip_plan = {
            'trip_info': {
                'origin': user_input.get('origin', ''),
                'origin_code': origin_code,
                'destination': user_input.get('destination', ''),
                'destination_code': destination_code,
                'departure_date': user_input.get('departure_date', ''),
                'return_date': user_input.get('return_date', ''),
                'travelers': user_input.get('travelers', 1),
                'budget': user_input.get('budget', 'medium'),
                'interests': user_input.get('interests', [])
            },
            'flights': [],
            'attractions': [],
            'packing_list': {},
            'weather': {},
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Get flight data
            flight_data = self.amadeus.search_flights(
                origin=user_input.get('origin', ''),
                destination=user_input.get('destination', ''),
                departure_date=user_input.get('departure_date', ''),
                adults=user_input.get('travelers', 1),
                return_date=user_input.get('return_date')
            )
            
            trip_plan['flights'] = self._parse_flight_data(flight_data)
            trip_plan['attractions'] = self._get_attractions(user_input)
            trip_plan['packing_list'] = self._get_packing_list(user_input)
            trip_plan['weather'] = self._get_weather()
            
            print(f"✅ Trip plan created with {len(trip_plan['flights'])} flights")
            return trip_plan
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return trip_plan
    
    def _parse_flight_data(self, flight_data):
        """Parse flight data from API response"""
        flights = []
        
        if not flight_data or 'data' not in flight_data:
            return flights
        
        is_sample = flight_data.get('_is_sample', False)
        
        for flight in flight_data.get('data', [])[:20]:
            try:
                flight_info = {
                    'airline': 'Unknown',
                    'flight_number': '',
                    'price': flight.get('price', {}).get('total', 'N/A'),
                    'currency': flight.get('price', {}).get('currency', 'USD'),
                    'departure_time': 'N/A',
                    'arrival_time': 'N/A',
                    'departure_airport': 'N/A',
                    'arrival_airport': 'N/A',
                    'duration': 'N/A',
                    'stops': 0,
                    'is_sample': is_sample
                }
                
                if flight.get('itineraries'):
                    itinerary = flight['itineraries'][0]
                    flight_info['duration'] = itinerary.get('duration', 'PT0H').replace('PT', '').replace('H', 'h ').replace('M', 'm')
                    
                    if itinerary.get('segments'):
                        segment = itinerary['segments'][0]
                        
                        # Get airline name
                        carrier_code = segment.get('carrierCode', '')
                        if 'dictionaries' in flight_data and 'carriers' in flight_data['dictionaries']:
                            airline_name = flight_data['dictionaries']['carriers'].get(carrier_code, carrier_code)
                        else:
                            airline_name = carrier_code
                        
                        flight_info.update({
                            'airline': airline_name,
                            'flight_number': f"{carrier_code}{segment.get('number', '')}",
                            'departure_time': segment.get('departure', {}).get('at', 'N/A'),
                            'arrival_time': segment.get('arrival', {}).get('at', 'N/A'),
                            'departure_airport': segment.get('departure', {}).get('iataCode', 'N/A'),
                            'arrival_airport': segment.get('arrival', {}).get('iataCode', 'N/A'),
                            'stops': len(itinerary['segments']) - 1
                        })
                
                # Format times
                for time_key in ['departure_time', 'arrival_time']:
                    if flight_info[time_key] != 'N/A':
                        try:
                            dt = datetime.fromisoformat(flight_info[time_key].replace('Z', '+00:00'))
                            flight_info[f'{time_key}_display'] = dt.strftime('%b %d, %I:%M %p')
                        except:
                            flight_info[f'{time_key}_display'] = flight_info[time_key]
                
                flights.append(flight_info)
                
            except Exception as e:
                continue
        
        return flights
    
    def _get_attractions(self, user_input):
        """Generate attractions list"""
        destination = user_input.get('destination', 'Unknown')
        interests = user_input.get('interests', [])
        
        attractions = [
            f"Explore {destination} city center",
            f"Visit local markets in {destination}",
            "Try traditional cuisine",
            "Take a city tour"
        ]
        
        interest_map = {
            'beach': ['Relax at the beach', 'Try water sports', 'Watch sunset'],
            'hiking': ['Hike mountain trails', 'Visit nature reserves'],
            'culture': ['Visit museums', 'Explore historical sites'],
            'food': ['Food tasting tour', 'Cooking class'],
            'shopping': ['Shop at boutiques', 'Visit shopping malls']
        }
        
        for interest in interests:
            if interest in interest_map:
                attractions.extend(interest_map[interest])
        
        return list(set(attractions))[:8]
    
    def _get_packing_list(self, user_input):
        """Generate packing list"""
        packing_list = {
            'essentials': ['Passport/ID', 'Wallet', 'Phone + Charger', 'Travel documents'],
            'clothing': ['T-shirts', 'Pants', 'Underwear', 'Socks', 'Jacket', 'Comfortable shoes'],
            'toiletries': ['Toothbrush', 'Shampoo', 'Soap', 'Deodorant', 'Sunscreen'],
            'electronics': ['Phone charger', 'Power bank', 'Headphones']
        }
        
        interests = user_input.get('interests', [])
        special_items = []
        
        if 'beach' in interests:
            special_items.extend(['Swimsuit', 'Sunglasses', 'Beach towel'])
        if 'hiking' in interests:
            special_items.extend(['Hiking boots', 'Backpack', 'Water bottle'])
        
        if special_items:
            packing_list['special'] = special_items
        
        return packing_list
    
    def _get_weather(self):
        """Get weather information"""
        return {
            'temperature': '75°F (24°C)',
            'conditions': 'Sunny with clear skies',
            'recommendation': 'Perfect for outdoor activities!'
        }