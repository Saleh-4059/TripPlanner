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
            'hotels': [], 
            'attractions': [],
            'activities': [],
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
            trip_plan['hotels'] = self._get_hotels(user_input)
            trip_plan['activities'] = self._get_activities(user_input)
            trip_plan['attractions'] = self._get_attractions(user_input)
            trip_plan['packing_list'] = self._get_packing_list(user_input)
            trip_plan['weather'] = self._get_weather(user_input) 
            
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
    
    def _get_activities(self, user_input):
        """Get activities from Amadeus API"""
        destination = user_input.get('destination', '')
        activities_data = self.amadeus.search_activities(destination)
        
        activities = []
        if activities_data and 'data' in activities_data:
            is_sample = activities_data.get('_is_sample', False)
            
            for activity in activities_data.get('data', [])[:10]:  # Limit to 10 activities
                activity_info = {
                    'name': activity.get('name', 'Activity'),
                    'description': activity.get('shortDescription', activity.get('description', 'No description available')),
                    'price': activity.get('price', {}).get('amount', 'N/A'),
                    'currency': activity.get('price', {}).get('currencyCode', 'EUR'),
                    'duration': activity.get('minimumDuration', 'Not specified'),
                    'booking_link': activity.get('bookingLink', '#'),
                    'is_sample': is_sample
                }
                
                # Clean up HTML from description
                if '<' in activity_info['description']:
                    import re
                    activity_info['description'] = re.sub('<[^<]+?>', '', activity_info['description'])
                
                # Truncate long descriptions
                if len(activity_info['description']) > 150:
                    activity_info['description'] = activity_info['description'][:147] + '...'
                
                activities.append(activity_info)
        
        return activities
    
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
    
    def _get_hotels(self, user_input):
        """Get hotel information for destination"""
        destination = user_input.get('destination', '')
        destination_code = self.amadeus.get_airport_code(destination)
        
        hotels_data = self.amadeus.search_hotels(
            city_code=destination_code,
            radius=5,
            radius_unit='KM'
        )
        
        hotels = []
        if hotels_data and 'data' in hotels_data:
            is_sample = hotels_data.get('_is_sample', False)
            
            for hotel in hotels_data.get('data', [])[:10]:  # Limit to 10 hotels
                hotel_info = {
                    'name': hotel.get('name', 'Hotel'),
                    'hotel_id': hotel.get('hotelId', ''),
                    'chain': hotel.get('chainCode', ''),
                    'address': hotel.get('address', {}),
                    'location': {
                        'latitude': hotel.get('geoCode', {}).get('latitude', 0),
                        'longitude': hotel.get('geoCode', {}).get('longitude', 0)
                    },
                    'distance': hotel.get('distance', {}),
                    'is_sample': is_sample
                }
                
                # Format address
                address_lines = []
                address_data = hotel_info['address']
                
                if 'lines' in address_data:
                    address_lines.extend(address_data['lines'][:2])
                
                city_info = []
                if address_data.get('cityName'):
                    city_info.append(address_data['cityName'])
                if address_data.get('stateCode'):
                    city_info.append(address_data['stateCode'])
                if address_data.get('countryCode'):
                    city_info.append(address_data['countryCode'])
                
                if city_info:
                    address_lines.append(', '.join(city_info))
                
                hotel_info['formatted_address'] = '\n'.join(address_lines) if address_lines else 'Address not available'
                
                # Format distance
                distance_data = hotel_info['distance']
                if distance_data and 'value' in distance_data and 'unit' in distance_data:
                    hotel_info['formatted_distance'] = f"{distance_data['value']} {distance_data['unit']} from center"
                else:
                    hotel_info['formatted_distance'] = ''
                
                hotels.append(hotel_info)
        
        return hotels
        
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
    
    ################### Get weather forecast ###################
    
    def _get_weather(self, user_input):
        """Get real weather forecast for the trip dates"""
        destination = user_input.get('destination', '')
        departure_date = user_input.get('departure_date', '')
        return_date = user_input.get('return_date', '')
        
        if not departure_date:
            return self._get_sample_weather_fallback()
        
        # Calculate date range (5 days forecast if no return date)
        if return_date:
            end_date = return_date
        else:
            # Add 4 days to departure for a 5-day forecast
            from datetime import datetime, timedelta
            dep_date = datetime.strptime(departure_date, '%Y-%m-%d')
            end_date = (dep_date + timedelta(days=4)).strftime('%Y-%m-%d')
        
        # Get weather data
        weather_data = self.amadeus.get_weather_forecast(
            city_name=destination,
            start_date=departure_date,
            end_date=end_date
        )
        
        # Parse weather data
        return self._parse_weather_data(weather_data, departure_date, end_date,destination)
        
    def _parse_weather_data(self, weather_data, start_date, end_date, city_name):
        """Parse weather data from API response"""
        if not weather_data or 'hourly' not in weather_data:
            return self._get_sample_weather_fallback(city_name)
        
        is_sample = weather_data.get('_is_sample', False)
        
        # Extract hourly data
        times = weather_data['hourly'].get('time', [])
        temperatures = weather_data['hourly'].get('temperature_2m', [])
        
        if not times or not temperatures:
            return self._get_sample_weather_fallback(city_name)
        
        # Group by day and calculate daily stats
        daily_forecasts = {}
        
        for i, time_str in enumerate(times):
            if i >= len(temperatures):
                break
                
            date = time_str.split('T')[0]  # Extract date part
            temp = temperatures[i]
            
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    'temps': [],
                    'times': []
                }
            
            daily_forecasts[date]['temps'].append(temp)
            daily_forecasts[date]['times'].append(time_str)
        
        # Calculate daily statistics
        forecast_days = []
        for date, data in sorted(daily_forecasts.items()):
            if data['temps']:
                avg_temp = sum(data['temps']) / len(data['temps'])
                min_temp = min(data['temps'])
                max_temp = max(data['temps'])
                
                # Determine weather condition based on temperature
                condition = self._get_weather_condition(avg_temp, data['temps'])
                
                forecast_days.append({
                    'date': date,
                    'date_display': datetime.strptime(date, '%Y-%m-%d').strftime('%b %d'),
                    'avg_temp': round(avg_temp, 1),
                    'min_temp': round(min_temp, 1),
                    'max_temp': round(max_temp, 1),
                    'condition': condition,
                    'icon': self._get_weather_icon(condition)
                })
        
        # Get overall forecast
        overall_temp = None
        if forecast_days:
            avg_temps = [day['avg_temp'] for day in forecast_days]
            overall_temp = round(sum(avg_temps) / len(avg_temps), 1)
        
        # Determine overall condition
        if forecast_days:
            conditions = [day['condition'] for day in forecast_days]
            overall_condition = max(set(conditions), key=conditions.count)
        else:
            overall_condition = 'Sunny'
        
        # Get packing recommendations based on weather
        packing_recommendations = self._get_weather_packing_recommendations(forecast_days)
        
        # Format city name nicely
        formatted_city_name = city_name.title()
        
        return {
            'is_sample': is_sample,
            'city': formatted_city_name,
            'overview': {
                'temperature': f"{overall_temp}°C" if overall_temp else 'N/A',
                'conditions': overall_condition,
                'recommendation': packing_recommendations.get('recommendation', ''),
                'date_range': f"{start_date} to {end_date}"
            },
            'daily_forecast': forecast_days[:5],  # Limit to 5 days
            'packing_recommendations': packing_recommendations.get('items', []),
            'unit': weather_data.get('hourly_units', {}).get('temperature_2m', '°C')
        }
            
    def _get_weather_condition(self, avg_temp, hourly_temps):
        """Determine weather condition based on temperature data"""
        if avg_temp > 25:
            return 'Hot'
        elif avg_temp > 15:
            return 'Warm'
        elif avg_temp > 5:
            return 'Mild'
        elif avg_temp > 0:
            return 'Chilly'
        elif avg_temp > -5:
            return 'Cold'
        else:
            return 'Freezing'
        
    def _get_weather_icon(self, condition):
        """Get weather icon based on condition"""
        icons = {
            'Hot': '☀️',
            'Warm': '🌤️',
            'Mild': '⛅',
            'Chilly': '🌥️',
            'Cold': '☁️',
            'Freezing': '❄️',
            'Rainy': '🌧️',
            'Stormy': '⛈️',
            'Windy': '💨',
            'Foggy': '🌫️'
        }
        return icons.get(condition, '🌈')
        
    def _get_weather_packing_recommendations(self, forecast_days):
        """Generate packing recommendations based on weather forecast"""
        if not forecast_days:
            return {
                'recommendation': 'Check local weather before packing.',
                'items': []
            }
        
        # Analyze temperatures
        all_temps = []
        for day in forecast_days:
            all_temps.extend([day['min_temp'], day['max_temp']])
        
        avg_temp = sum(all_temps) / len(all_temps)
        min_temp = min(all_temps)
        max_temp = max(all_temps)
        
        recommendations = []
        recommendation_text = ""
        
        if max_temp > 25:
            recommendations.extend(['Sunscreen', 'Sunglasses', 'Hat', 'Light clothing'])
            recommendation_text = "Hot weather expected. Stay hydrated!"
        elif max_temp > 15:
            recommendations.extend(['Light jacket', 'T-shirts', 'Comfortable shoes'])
            recommendation_text = "Pleasant weather. Perfect for exploring!"
        elif max_temp > 5:
            recommendations.extend(['Warm jacket', 'Sweaters', 'Long pants'])
            recommendation_text = "Cool weather. Layer your clothing."
        elif min_temp < 0:
            recommendations.extend(['Winter coat', 'Gloves', 'Scarf', 'Warm hat', 'Thermal layers'])
            recommendation_text = "Cold weather. Bundle up and stay warm!"
        
        # Add rain gear if any day has rainy condition
        if any('rain' in day['condition'].lower() for day in forecast_days):
            recommendations.extend(['Umbrella', 'Waterproof jacket', 'Waterproof shoes'])
            recommendation_text += " Rain expected. Bring rain gear."
        
        return {
            'recommendation': recommendation_text,
            'items': list(set(recommendations))  # Remove duplicates
        }
        
    def _get_sample_weather_fallback(self, city_name="Unknown"):
        """Fallback sample weather data"""
        formatted_city_name = city_name.title() if city_name != "Unknown" else "Your destination"
        
        return {
            'is_sample': True,
            'city': formatted_city_name,
            'overview': {
                'temperature': '75°F (24°C)',
                'conditions': 'Sunny with clear skies',
                'recommendation': 'Perfect for outdoor activities!',
                'date_range': 'Sample dates'
            },
            'daily_forecast': [
                {'date': '2024-01-15', 'date_display': 'Jan 15', 'avg_temp': 22, 'min_temp': 18, 'max_temp': 26, 'condition': 'Sunny', 'icon': '☀️'},
                {'date': '2024-01-16', 'date_display': 'Jan 16', 'avg_temp': 23, 'min_temp': 19, 'max_temp': 27, 'condition': 'Partly Cloudy', 'icon': '⛅'},
                {'date': '2024-01-17', 'date_display': 'Jan 17', 'avg_temp': 21, 'min_temp': 17, 'max_temp': 25, 'condition': 'Sunny', 'icon': '☀️'}
            ],
            'packing_recommendations': ['Sunscreen', 'Sunglasses', 'Light jacket'],
            'unit': '°C'
        }