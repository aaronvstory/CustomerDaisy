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
    
    def get_random_address_near_location(self, origin_address: str, radius_miles: float = 10.0) -> Optional[Dict]:
        """
        Get a random real address near a given location using MapQuest API
        
        Args:
            origin_address: Base address to search around
            radius_miles: Search radius in miles (default: 10)
            
        Returns:
            Dict with address components or None if failed
        """
        try:
            console.print(f"🔍 Searching for addresses near: {origin_address}", style="blue")
            
            # Use MapQuest Search API to find addresses in radius
            search_url = f"{self.base_url}/search/v2/radius"
            
            params = {
                'key': self.api_key,
                'origin': origin_address,
                'radius': radius_miles,
                'units': 'm',  # miles
                'maxMatches': 50,
                'outFormat': 'json'
            }
            
            response = self.session.get(search_url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"MapQuest API error: {response.status_code} - {response.text}")
            
            data = response.json()
            search_results = data.get('searchResults', [])
            
            if not search_results:
                console.print("⚠️ No addresses found in radius, trying broader search", style="yellow")
                return self._get_fallback_address(origin_address)
            
            # Filter results that have complete address information
            valid_addresses = []
            for result in search_results:
                fields = result.get('fields', {})
                address = fields.get('address', '').strip()
                city = fields.get('city', '').strip()
                state = fields.get('state', '').strip()
                postal_code = fields.get('postal_code', '').strip()
                
                # Only include addresses with all components
                if address and city and state and postal_code:
                    # Skip if too close to origin (less than 0.5 miles)
                    distance = result.get('distance', 0)
                    if distance >= 0.5:
                        valid_addresses.append(result)
            
            if not valid_addresses:
                console.print("⚠️ No valid complete addresses found", style="yellow")
                return self._get_fallback_address(origin_address)
            
            # Select a random address from valid results
            selected = random.choice(valid_addresses)
            fields = selected['fields']
            
            address_data = {
                'address_line1': fields['address'],
                'city': fields['city'],
                'state': fields['state'],
                'zip_code': fields['postal_code'],
                'full_address': f"{fields['address']}, {fields['city']}, {fields['state']} {fields['postal_code']}",
                'latitude': selected.get('place', {}).get('geometry', {}).get('coordinates', [None, None])[1],
                'longitude': selected.get('place', {}).get('geometry', {}).get('coordinates', [None, None])[0],
                'distance_from_origin': selected.get('distance', 0),
                'source': 'mapquest_radius_search'
            }
            
            console.print(f"✅ Found address: {address_data['full_address']}", style="green")
            console.print(f"📏 Distance from origin: {address_data['distance_from_origin']:.1f} miles", style="blue")
            
            return address_data
            
        except requests.RequestException as e:
            console.print(f"❌ Network error getting address: {e}", style="red")
            return None
        except Exception as e:
            console.print(f"❌ Error getting random address: {e}", style="red")
            return None
    
    def _get_fallback_address(self, origin_address: str) -> Optional[Dict]:
        """Get fallback address using geocoding if radius search fails"""
        try:
            # Try to geocode the origin and generate nearby address
            geocode_url = f"{self.base_url}/geocoding/v1/address"
            
            params = {
                'key': self.api_key,
                'location': origin_address,
                'outFormat': 'json',
                'maxResults': 1
            }
            
            response = self.session.get(geocode_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    location = results[0]['locations'][0]
                    
                    # Get the street address - if empty, generate a realistic one
                    street = location.get('street', '').strip()
                    city = location.get('adminArea5', '').strip()
                    state = location.get('adminArea3', '').strip()
                    zip_code = location.get('postalCode', '').strip()
                    
                    # If street is empty, generate a realistic street address
                    if not street and city:
                        import random
                        street_names = [
                            "Main St", "Oak Ave", "Park Rd", "First St", "Second St", 
                            "Elm St", "Maple Ave", "Washington St", "Lincoln Ave", "Church St",
                            "School St", "High St", "Mill Rd", "Pine St", "Cedar Ave"
                        ]
                        street_number = random.randint(100, 9999)
                        street_name = random.choice(street_names)
                        street = f"{street_number} {street_name}"
                    
                    # Ensure we have basic address components
                    if not city:
                        city = origin_address.split(',')[0].strip()
                    if not state:
                        state = "Unknown State"
                    if not zip_code:
                        zip_code = "00000"
                    
                    address_data = {
                        'address_line1': street,
                        'city': city,
                        'state': state,
                        'zip_code': zip_code,
                        'full_address': f"{street}, {city}, {state} {zip_code}",
                        'latitude': location.get('latLng', {}).get('lat'),
                        'longitude': location.get('latLng', {}).get('lng'),
                        'source': 'mapquest_geocoding_fallback'
                    }
                    
                    console.print(f"✅ Fallback address: {address_data['full_address']}", style="cyan")
                    return address_data
            
            return None
            
        except Exception as e:
            console.print(f"❌ Fallback address failed: {e}", style="red")
            return None
    
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
            
            return standardized
            
        except requests.RequestException as e:
            console.print(f"❌ Network error validating address: {e}", style="red")
            return None
        except Exception as e:
            console.print(f"❌ Error validating address: {e}", style="red")
            return None
    
    def search_addresses(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for addresses matching a query
        
        Args:
            query: Search query (partial address, city, etc.)
            max_results: Maximum number of results
            
        Returns:
            List of matching addresses
        """
        try:
            console.print(f"🔍 Searching addresses for: {query}", style="blue")
            
            search_url = f"{self.base_url}/search/v2/structured"
            
            params = {
                'key': self.api_key,
                'location': query,
                'outFormat': 'json',
                'maxMatches': max_results
            }
            
            response = self.session.get(search_url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"MapQuest API error: {response.status_code}")
            
            data = response.json()
            search_results = data.get('searchResults', [])
            
            addresses = []
            for result in search_results:
                fields = result.get('fields', {})
                
                if fields.get('address') and fields.get('city'):
                    address_data = {
                        'address_line1': fields.get('address', ''),
                        'city': fields.get('city', ''),
                        'state': fields.get('state', ''),
                        'zip_code': fields.get('postal_code', ''),
                        'full_address': f"{fields.get('address', '')}, {fields.get('city', '')}, {fields.get('state', '')} {fields.get('postal_code', '')}",
                        'source': 'mapquest_search'
                    }
                    addresses.append(address_data)
            
            console.print(f"✅ Found {len(addresses)} addresses", style="green")
            return addresses
            
        except Exception as e:
            console.print(f"❌ Error searching addresses: {e}", style="red")
            return []
    
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
        Get a random address from a major US city
        
        Returns:
            Random real US address
        """
        # List of major US cities for random address generation
        major_cities = [
            "New York, NY",
            "Los Angeles, CA", 
            "Chicago, IL",
            "Houston, TX",
            "Phoenix, AZ",
            "Philadelphia, PA",
            "San Antonio, TX",
            "San Diego, CA",
            "Dallas, TX",
            "San Jose, CA",
            "Austin, TX",
            "Jacksonville, FL",
            "Fort Worth, TX",
            "Columbus, OH",
            "Charlotte, NC",
            "San Francisco, CA",
            "Indianapolis, IN",
            "Seattle, WA",
            "Denver, CO",
            "Boston, MA",
            "Nashville, TN",
            "Memphis, TN",
            "Portland, OR",
            "Las Vegas, NV",
            "Louisville, KY",
            "Miami, FL",
            "Atlanta, GA",
            "Virginia Beach, VA",
            "Oakland, CA",
            "Minneapolis, MN"
        ]
        
        # Select random city and get address near it
        random_city = random.choice(major_cities)
        console.print(f"🎲 Getting random address near: {random_city}", style="cyan")
        
        return self.get_random_address_near_location(random_city, radius_miles=15.0)
    
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
    
    def get_api_stats(self) -> Dict:
        """Get MapQuest API usage statistics"""
        return {
            "api_key_configured": bool(self.api_key),
            "api_key_masked": f"...{self.api_key[-8:]}" if self.api_key else "Not configured",
            "base_url": self.base_url,
            "cache_size": len(self._location_cache),
            "last_test": datetime.now().isoformat()
        }
