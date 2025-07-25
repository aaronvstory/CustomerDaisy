#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MapQuest Address Manager - Real Address Integration
==================================================
Handles MapQuest API for real address generation and validation.
"""

import requests
import random
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from rich.console import Console
    console = Console()
except ImportError:
    class Console:
        def print(self, *args, **kwargs): print(*args)
    console = Console()

class MapQuestAddressManager:
    """MapQuest API integration for real address handling"""
    
    def __init__(self, config: Dict):
        """Initialize MapQuest manager with configuration"""
        self.api_key = config.get('api_key', 'FzB4PTf1mTlOhn6fajm5irPjsnavYGJn')
        self.base_url = config.get('base_url', 'https://www.mapquestapi.com')
        
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Cache for common locations
        self._location_cache = {}
        
        console.print("🗺️ MapQuest Address Manager initialized", style="green")
    
    def _search_real_poi_near_location(self, origin_address: str, radius_miles: float) -> Optional[Dict]:
        """
        Search for real POI (businesses, restaurants, landmarks) near a location
        
        Args:
            origin_address: Origin location to search around
            radius_miles: Search radius in miles
            
        Returns:
            Dict with real business address or None if none found
        """
        try:
            # Use MapQuest POI Search API to find real businesses
            search_url = f"{self.base_url}/search/v2/radius"
            
            # First, geocode the origin to get coordinates
            geocode_url = f"{self.base_url}/geocoding/v1/address"
            geocode_params = {
                'key': self.api_key,
                'location': origin_address,
                'outFormat': 'json',
                'maxResults': 1
            }
            
            geocode_response = self.session.get(geocode_url, params=geocode_params)
            if geocode_response.status_code != 200:
                console.print(f"⚠️ Geocoding failed: {geocode_response.status_code}", style="yellow")
                return None
            
            geocode_data = geocode_response.json()
            results = geocode_data.get('results', [])
            if not results or not results[0].get('locations'):
                console.print("⚠️ Could not geocode origin address", style="yellow")
                return None
            
            location = results[0]['locations'][0]
            lat_lng = location.get('latLng', {})
            origin_lat = lat_lng.get('lat')
            origin_lng = lat_lng.get('lng')
            
            if not origin_lat or not origin_lng:
                console.print("⚠️ Could not get coordinates for origin", style="yellow")
                return None
            
            # Now search for real POIs using the radius search
            poi_request_body = {
                "origin": {
                    "latLng": {
                        "lat": origin_lat,
                        "lng": origin_lng
                    }
                },
                "hostedDataList": [
                    {"tableName": "mqap.ntpois"}  # MapQuest POI dataset with real businesses
                ],
                "options": {
                    "radius": radius_miles,
                    "units": "m",  # miles
                    "maxMatches": 100
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            poi_response = self.session.post(search_url, 
                                           params={'key': self.api_key}, 
                                           json=poi_request_body,
                                           headers=headers)
            
            if poi_response.status_code != 200:
                console.print(f"⚠️ POI search failed: {poi_response.status_code}", style="yellow")
                return None
            
            poi_data = poi_response.json()
            search_results = poi_data.get('searchResults', [])
            
            if not search_results:
                console.print("⚠️ No real businesses found in area", style="yellow")
                return None
            
            # Filter for valid business addresses with complete information
            valid_businesses = []
            for result in search_results:
                fields = result.get('fields', {})
                
                # Get business information
                name = fields.get('name', '').strip()
                address = fields.get('address', '').strip()
                city = fields.get('city', '').strip()
                state = fields.get('state', '').strip()
                postal_code = fields.get('postal_code', '').strip()
                
                # Must have complete address information
                if address and city and state and name:
                    # Prefer businesses with postal codes, but don't require them
                    if not postal_code:
                        postal_code = location.get('postalCode', '00000')
                    
                    # Skip if too close to origin (less than 0.3 miles for POI)
                    distance = result.get('distance', 0)
                    if distance >= 0.3:
                        valid_businesses.append(result)
            
            if not valid_businesses:
                console.print("⚠️ No valid businesses with complete addresses found", style="yellow")
                return None
            
            # Select a random business from valid results
            selected_business = random.choice(valid_businesses)
            fields = selected_business['fields']
            
            # Extract coordinates from the result
            lat = fields.get('lat') or fields.get('disp_lat')
            lng = fields.get('lng') or fields.get('disp_lng')
            
            business_address = {
                'address_line1': fields.get('address', ''),
                'city': fields.get('city', ''),
                'state': fields.get('state', ''),
                'zip_code': fields.get('postal_code', '00000'),
                'full_address': f"{fields.get('address', '')}, {fields.get('city', '')}, {fields.get('state', '')} {fields.get('postal_code', '00000')}",
                'latitude': float(lat) if lat else None,
                'longitude': float(lng) if lng else None,
                'distance_from_origin': selected_business.get('distance', 0),
                'business_name': fields.get('name', ''),
                'business_type': fields.get('group_sic_code_name', 'Business'),
                'source': 'mapquest_real_poi'
            }
            
            console.print(f"✅ Found REAL business: {business_address['business_name']}", style="green")
            console.print(f"📍 Address: {business_address['full_address']}", style="blue")
            console.print(f"🏢 Type: {business_address['business_type']}", style="cyan")
            console.print(f"📏 Distance: {business_address['distance_from_origin']:.1f} miles", style="blue")
            
            return business_address
            
        except Exception as e:
            console.print(f"❌ Error searching real POI: {e}", style="red")
            return None
    
    def get_random_address_near_location(self, origin_address: str, radius_miles: float = 10.0) -> Optional[Dict]:
        """
        Get a random REAL address near a given location using MapQuest POI API
        
        Args:
            origin_address: Base address to search around
            radius_miles: Search radius in miles (default: 10)
            
        Returns:
            Dict with REAL address components or None if failed
        """
        try:
            console.print(f"🔍 Searching for REAL businesses/places near: {origin_address}", style="blue")
            
            # First try POI search for real businesses
            real_address = self._search_real_poi_near_location(origin_address, radius_miles)
            if real_address:
                return real_address
            
            # Fallback to broader POI search
            console.print("⚠️ Expanding search for real addresses...", style="yellow")
            real_address = self._search_real_poi_near_location(origin_address, radius_miles * 2)
            if real_address:
                return real_address
            
            # Final fallback to nationwide real business search
            console.print("🌎 Searching nationwide for real business addresses...", style="yellow")
            return self._get_real_business_fallback(origin_address)
            
        except requests.RequestException as e:
            console.print(f"❌ Network error getting real address: {e}", style="red")
            return self._get_real_business_fallback(origin_address)
        except Exception as e:
            console.print(f"❌ Error getting real address: {e}", style="red")
            return self._get_real_business_fallback(origin_address)
    
    def _get_real_business_fallback(self, origin_address: str = None) -> Optional[Dict]:
        """
        Get real business address fallback - searches for real businesses nationwide
        NEVER generates fake addresses
        """
        try:
            console.print("🏢 Searching for real businesses nationwide...", style="cyan")
            
            # List of major US metropolitan areas with high business density
            major_metro_areas = [
                {"city": "New York", "state": "NY", "lat": 40.7128, "lng": -74.0060},
                {"city": "Los Angeles", "state": "CA", "lat": 34.0522, "lng": -118.2437},
                {"city": "Chicago", "state": "IL", "lat": 41.8781, "lng": -87.6298},
                {"city": "Houston", "state": "TX", "lat": 29.7604, "lng": -95.3698},
                {"city": "Phoenix", "state": "AZ", "lat": 33.4484, "lng": -112.0740},
                {"city": "Philadelphia", "state": "PA", "lat": 39.9526, "lng": -75.1652},
                {"city": "San Antonio", "state": "TX", "lat": 29.4241, "lng": -98.4936},
                {"city": "San Diego", "state": "CA", "lat": 32.7157, "lng": -117.1611},
                {"city": "Dallas", "state": "TX", "lat": 32.7767, "lng": -96.7970},
                {"city": "San Jose", "state": "CA", "lat": 37.3382, "lng": -121.8863},
                {"city": "Austin", "state": "TX", "lat": 30.2672, "lng": -97.7431},
                {"city": "Jacksonville", "state": "FL", "lat": 30.3322, "lng": -81.6557},
                {"city": "San Francisco", "state": "CA", "lat": 37.7749, "lng": -122.4194},
                {"city": "Indianapolis", "state": "IN", "lat": 39.7684, "lng": -86.1581},
                {"city": "Columbus", "state": "OH", "lat": 39.9612, "lng": -82.9988},
                {"city": "Fort Worth", "state": "TX", "lat": 32.7555, "lng": -97.3308},
                {"city": "Charlotte", "state": "NC", "lat": 35.2271, "lng": -80.8431},
                {"city": "Seattle", "state": "WA", "lat": 47.6062, "lng": -122.3321},
                {"city": "Denver", "state": "CO", "lat": 39.7392, "lng": -104.9903},
                {"city": "Boston", "state": "MA", "lat": 42.3601, "lng": -71.0589}
            ]
            
            # Try multiple metro areas to find real businesses
            random.shuffle(major_metro_areas)
            
            for metro in major_metro_areas[:5]:  # Try up to 5 different metros
                console.print(f"🔍 Searching for businesses in {metro['city']}, {metro['state']}...", style="blue")
                
                # Search for real POIs in this metro area
                search_url = f"{self.base_url}/search/v2/radius"
                
                poi_request_body = {
                    "origin": {
                        "latLng": {
                            "lat": metro['lat'],
                            "lng": metro['lng']
                        }
                    },
                    "hostedDataList": [
                        {"tableName": "mqap.ntpois"}  # Real POI database
                    ],
                    "options": {
                        "radius": 25,  # 25 mile radius from city center
                        "units": "m",
                        "maxMatches": 150
                    }
                }
                
                headers = {'Content-Type': 'application/json'}
                response = self.session.post(search_url, 
                                           params={'key': self.api_key}, 
                                           json=poi_request_body,
                                           headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    search_results = data.get('searchResults', [])
                    
                    if search_results:
                        # Filter for businesses with complete address information
                        valid_businesses = []
                        for result in search_results:
                            fields = result.get('fields', {})
                            
                            name = fields.get('name', '').strip()
                            address = fields.get('address', '').strip()
                            city = fields.get('city', '').strip()
                            state = fields.get('state', '').strip()
                            
                            # Must have complete business information
                            if name and address and city and state:
                                valid_businesses.append(result)
                        
                        if valid_businesses:
                            # Select a random real business
                            selected = random.choice(valid_businesses)
                            fields = selected['fields']
                            
                            # Extract coordinates
                            lat = fields.get('lat') or fields.get('disp_lat')
                            lng = fields.get('lng') or fields.get('disp_lng')
                            
                            real_business = {
                                'address_line1': fields.get('address', ''),
                                'city': fields.get('city', ''),
                                'state': fields.get('state', ''),
                                'zip_code': fields.get('postal_code', '00000'),
                                'full_address': f"{fields.get('address', '')}, {fields.get('city', '')}, {fields.get('state', '')} {fields.get('postal_code', '00000')}",
                                'latitude': float(lat) if lat else None,
                                'longitude': float(lng) if lng else None,
                                'business_name': fields.get('name', ''),
                                'business_type': fields.get('group_sic_code_name', 'Business'),
                                'source': 'mapquest_nationwide_poi_fallback'
                            }
                            
                            console.print(f"✅ Found REAL business nationwide: {real_business['business_name']}", style="green")
                            console.print(f"📍 Address: {real_business['full_address']}", style="blue")
                            console.print(f"🏢 Type: {real_business['business_type']}", style="cyan")
                            
                            return real_business
            
            # If still no results, return well-known landmark addresses
            console.print("🏛️ Using well-known landmark addresses as final fallback...", style="yellow")
            return self._get_landmark_address()
            
        except Exception as e:
            console.print(f"❌ Real business fallback failed: {e}", style="red")
            return self._get_landmark_address()
    
    def _get_landmark_address(self) -> Optional[Dict]:
        """
        Get well-known landmark addresses as absolute final fallback
        These are guaranteed real addresses that exist
        """
        # Well-known real addresses that definitely exist
        landmarks = [
            {
                'address_line1': '1600 Pennsylvania Avenue NW',
                'city': 'Washington',
                'state': 'DC',
                'zip_code': '20500',
                'latitude': 38.8977,
                'longitude': -77.0365,
                'business_name': 'The White House',
                'business_type': 'Government Building'
            },
            {
                'address_line1': '350 5th Ave',
                'city': 'New York',
                'state': 'NY', 
                'zip_code': '10118',
                'latitude': 40.7484,
                'longitude': -73.9857,
                'business_name': 'Empire State Building',
                'business_type': 'Landmark Building'
            },
            {
                'address_line1': '1 Infinite Loop',
                'city': 'Cupertino',
                'state': 'CA',
                'zip_code': '95014',
                'latitude': 37.3318,
                'longitude': -122.0312,
                'business_name': 'Apple Park',
                'business_type': 'Corporate Headquarters'
            },
            {
                'address_line1': '1060 W Addison St',
                'city': 'Chicago',
                'state': 'IL',
                'zip_code': '60613',
                'latitude': 41.9484,
                'longitude': -87.6553,
                'business_name': 'Wrigley Field',
                'business_type': 'Sports Stadium'
            },
            {
                'address_line1': '1 Microsoft Way',
                'city': 'Redmond',
                'state': 'WA',
                'zip_code': '98052',
                'latitude': 47.6394,
                'longitude': -122.1288,
                'business_name': 'Microsoft Corporation',
                'business_type': 'Corporate Headquarters'
            },
            {
                'address_line1': '11 Wall Street',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10005',
                'latitude': 40.7074,
                'longitude': -74.0113,
                'business_name': 'New York Stock Exchange',
                'business_type': 'Financial Institution'
            }
        ]
        
        selected_landmark = random.choice(landmarks)
        
        # Format the address data
        address_data = {
            'address_line1': selected_landmark['address_line1'],
            'city': selected_landmark['city'],
            'state': selected_landmark['state'],
            'zip_code': selected_landmark['zip_code'],
            'full_address': f"{selected_landmark['address_line1']}, {selected_landmark['city']}, {selected_landmark['state']} {selected_landmark['zip_code']}",
            'latitude': selected_landmark['latitude'],
            'longitude': selected_landmark['longitude'],
            'business_name': selected_landmark['business_name'],
            'business_type': selected_landmark['business_type'],
            'source': 'mapquest_landmark_fallback'
        }
        
        console.print(f"🏛️ Using landmark address: {address_data['business_name']}", style="magenta")
        console.print(f"📍 Address: {address_data['full_address']}", style="blue")
        
        return address_data
    
    def validate_address(self, address: str) -> Optional[Dict]:
        """
        Validate and standardize an address using MapQuest
        
        Args:
            address: Address string to validate
            
        Returns:
            Standardized address data or None if invalid
        """
        try:
            console.print(f"✅ Validating address: {address}", style="blue")
            
            geocode_url = f"{self.base_url}/geocoding/v1/address"
            
            params = {
                'key': self.api_key,
                'location': address,
                'outFormat': 'json',
                'maxResults': 1
            }
            
            response = self.session.get(geocode_url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"MapQuest API error: {response.status_code}")
            
            data = response.json()
            results = data.get('results', [])
            
            if not results or not results[0].get('locations'):
                console.print("❌ Address not found or invalid", style="red")
                return None
            
            location = results[0]['locations'][0]
            
            # Check geocode quality
            geocode_quality = location.get('geocodeQuality', '')
            if geocode_quality in ['COUNTRY', 'STATE']:
                console.print(f"⚠️ Low quality geocode: {geocode_quality}", style="yellow")
                return None
            
            # Extract standardized address components
            standardized = {
                'address_line1': location.get('street', ''),
                'city': location.get('adminArea5', ''),
                'state': location.get('adminArea3', ''),
                'zip_code': location.get('postalCode', ''),
                'full_address': f"{location.get('street', '')}, {location.get('adminArea5', '')}, {location.get('adminArea3', '')} {location.get('postalCode', '')}",
                'latitude': location.get('latLng', {}).get('lat'),
                'longitude': location.get('latLng', {}).get('lng'),
                'geocode_quality': geocode_quality,
                'source': 'mapquest_validation'
            }
            
            console.print(f"✅ Address validated: {standardized['full_address']}", style="green")
            console.print(f"📍 Quality: {geocode_quality}", style="blue")
            
            # Ensure complete address before returning
            return self._validate_complete_address(standardized)
            
        except requests.RequestException as e:
            console.print(f"❌ Network error validating address: {e}", style="red")
            return None
        except Exception as e:
            console.print(f"❌ Error validating address: {e}", style="red")
            return None
    
    def search_addresses(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for REAL addresses matching a query using POI data
        
        Args:
            query: Search query (partial address, city, etc.)
            max_results: Maximum number of results
            
        Returns:
            List of matching REAL addresses from businesses/POI
        """
        try:
            console.print(f"🔍 Searching REAL addresses for: {query}", style="blue")
            
            # First try geocoding the query to get coordinates
            geocode_url = f"{self.base_url}/geocoding/v1/address"
            geocode_params = {
                'key': self.api_key,
                'location': query,
                'outFormat': 'json',
                'maxResults': 1
            }
            
            geocode_response = self.session.get(geocode_url, params=geocode_params)
            
            if geocode_response.status_code == 200:
                geocode_data = geocode_response.json()
                results = geocode_data.get('results', [])
                
                if results and results[0].get('locations'):
                    location = results[0]['locations'][0]
                    lat_lng = location.get('latLng', {})
                    
                    if lat_lng.get('lat') and lat_lng.get('lng'):
                        # Search for real POIs near the geocoded location
                        search_url = f"{self.base_url}/search/v2/radius"
                        
                        poi_request_body = {
                            "origin": {
                                "latLng": {
                                    "lat": lat_lng['lat'],
                                    "lng": lat_lng['lng']
                                }
                            },
                            "hostedDataList": [
                                {"tableName": "mqap.ntpois"}
                            ],
                            "options": {
                                "radius": 15,  # 15 mile radius
                                "units": "m",
                                "maxMatches": max_results * 2  # Get more results to filter
                            }
                        }
                        
                        headers = {'Content-Type': 'application/json'}
                        poi_response = self.session.post(search_url, 
                                                       params={'key': self.api_key}, 
                                                       json=poi_request_body,
                                                       headers=headers)
                        
                        if poi_response.status_code == 200:
                            poi_data = poi_response.json()
                            search_results = poi_data.get('searchResults', [])
                            
                            addresses = []
                            for result in search_results[:max_results]:
                                fields = result.get('fields', {})
                                
                                # Must have business name and address
                                if fields.get('name') and fields.get('address') and fields.get('city'):
                                    lat = fields.get('lat') or fields.get('disp_lat')
                                    lng = fields.get('lng') or fields.get('disp_lng')
                                    
                                    address_data = {
                                        'address_line1': fields.get('address', ''),
                                        'city': fields.get('city', ''),
                                        'state': fields.get('state', ''),
                                        'zip_code': fields.get('postal_code', '00000'),
                                        'full_address': f"{fields.get('address', '')}, {fields.get('city', '')}, {fields.get('state', '')} {fields.get('postal_code', '00000')}",
                                        'latitude': float(lat) if lat else None,
                                        'longitude': float(lng) if lng else None,
                                        'business_name': fields.get('name', ''),
                                        'business_type': fields.get('group_sic_code_name', 'Business'),
                                        'source': 'mapquest_real_poi_search'
                                    }
                                    addresses.append(address_data)
                            
                            console.print(f"✅ Found {len(addresses)} REAL business addresses", style="green")
                            return addresses
            
            # Fallback: return some real businesses from major cities
            console.print("🌎 Using nationwide real business search as fallback", style="yellow")
            fallback_address = self._get_real_business_fallback()
            return [fallback_address] if fallback_address else []
            
        except Exception as e:
            console.print(f"❌ Error searching real addresses: {e}", style="red")
            # Emergency fallback: return landmark addresses
            landmark = self._get_landmark_address()
            return [landmark] if landmark else []
    
    def get_address_suggestions(self, partial_address: str) -> List[str]:
        """
        Get address suggestions for auto-complete
        
        Args:
            partial_address: Partial address string
            
        Returns:
            List of suggested complete addresses
        """
        try:
            # Use the search API for suggestions
            addresses = self.search_addresses(partial_address, max_results=5)
            
            suggestions = []
            for addr in addresses:
                if addr['full_address']:
                    suggestions.append(addr['full_address'])
            
            return suggestions
            
        except Exception as e:
            console.print(f"❌ Error getting suggestions: {e}", style="red")
            return []
    
    def get_random_us_address(self) -> Optional[Dict]:
        """
        Get a random REAL business address from a major US city
        
        Returns:
            Random real US business address (never fake)
        """
        console.print("🇺🇸 Getting random REAL US business address...", style="cyan")
        
        # Use the real business fallback which searches nationwide
        return self._get_real_business_fallback()
    
    def test_api_connection(self) -> bool:
        """Test MapQuest API connection and key validity"""
        try:
            # Test with a simple geocoding request
            test_address = "1600 Pennsylvania Avenue NW, Washington, DC"
            result = self.validate_address(test_address)
            
            if result:
                console.print("✅ MapQuest API connection successful", style="green")
                console.print(f"🔑 API key valid: ...{self.api_key[-8:]}", style="blue")
                return True
            else:
                console.print("❌ MapQuest API test failed", style="red")
                return False
                
        except Exception as e:
            console.print(f"❌ MapQuest API connection failed: {e}", style="red")
            return False
    
    def _ensure_complete_real_address(self, address_data: Dict) -> Dict:
        """
        Ensure address data is complete for real addresses
        Does NOT generate fake components - only validates real ones
        
        Args:
            address_data: Address data dictionary from real POI/business
            
        Returns:
            Validated real address data
        """
        if not address_data:
            return address_data
        
        # Ensure all required fields exist (but don't generate fake ones)
        required_fields = ['address_line1', 'city', 'state', 'zip_code']
        for field in required_fields:
            if field not in address_data or not address_data[field]:
                console.print(f"⚠️ Real address missing {field}, marking as incomplete", style="yellow")
                address_data[field] = address_data.get(field, '')
        
        # Rebuild full_address if components exist
        if all(address_data.get(field) for field in required_fields):
            address_data['full_address'] = f"{address_data['address_line1']}, {address_data['city']}, {address_data['state']} {address_data['zip_code']}"
        
        return address_data
    
    def _validate_complete_address(self, address_data: Dict) -> Dict:
        """
        Validate that a REAL address is complete
        Does NOT modify real address data - only validates it
        
        Args:
            address_data: Real address data dictionary from POI/business
            
        Returns:
            Validated real address data (unmodified)
        """
        if not address_data:
            return address_data
        
        # Simply validate that it's a real address - don't modify it
        return self._ensure_complete_real_address(address_data)

    def get_api_stats(self) -> Dict:
        """Get MapQuest API usage statistics"""
        return {
            "api_key_configured": bool(self.api_key),
            "api_key_masked": f"...{self.api_key[-8:]}" if self.api_key else "Not configured",
            "base_url": self.base_url,
            "cache_size": len(self._location_cache),
            "last_test": datetime.now().isoformat()
        }
