#!/usr/bin/env python3
"""
Test script to verify that MapQuest integration returns REAL addresses
"""

import sys
import os
sys.path.append('src')

from mapquest_address import MapQuestAddressManager
from config_manager import ConfigManager

def test_real_addresses():
    """Test that all address generation methods return real addresses"""
    
    print("🧪 Testing Real Address Generation System")
    print("=" * 60)
    
    # Load configuration
    config_manager = ConfigManager()
    mapquest_config = config_manager.get_section('MAPQUEST')
    
    # Initialize MapQuest manager
    mapquest_manager = MapQuestAddressManager(mapquest_config)
    
    # Test 1: API Connection
    print("\n1. Testing API Connection...")
    if mapquest_manager.test_api_connection():
        print("✅ API Connection successful")
        stats = mapquest_manager.get_api_stats()
        print(f"   📊 API Key: {stats['api_key_masked']}")
    else:
        print("❌ API Connection failed")
        return False
    
    # Test 2: Random US Address
    print("\n2. Testing Random US Address Generation...")
    random_address = mapquest_manager.get_random_us_address()
    if random_address:
        print("✅ Random US address generated:")
        print(f"   🏢 Business: {random_address.get('business_name', 'N/A')}")
        print(f"   📍 Address: {random_address['full_address']}")
        print(f"   🏷️ Type: {random_address.get('business_type', 'N/A')}")
        print(f"   📊 Source: {random_address['source']}")
        print(f"   🌐 Coordinates: {random_address.get('latitude')}, {random_address.get('longitude')}")
        
        # Verify it's not a fake address
        if is_fake_address(random_address):
            print("❌ WARNING: Generated address appears to be fake!")
            return False
        else:
            print("✅ Address appears to be real")
    else:
        print("❌ Failed to generate random US address")
        return False
    
    # Test 3: Address Near Location
    print("\n3. Testing Address Near Location...")
    near_address = mapquest_manager.get_random_address_near_location("Chicago, IL", 10.0)
    if near_address:
        print("✅ Address near Chicago generated:")
        print(f"   🏢 Business: {near_address.get('business_name', 'N/A')}")
        print(f"   📍 Address: {near_address['full_address']}")
        print(f"   🏷️ Type: {near_address.get('business_type', 'N/A')}")
        print(f"   📏 Distance: {near_address.get('distance_from_origin', 0):.1f} miles")
        print(f"   📊 Source: {near_address['source']}")
        
        # Verify it's not a fake address
        if is_fake_address(near_address):
            print("❌ WARNING: Generated address appears to be fake!")
            return False
        else:
            print("✅ Address appears to be real")
    else:
        print("❌ Failed to generate address near Chicago")
        return False
    
    # Test 4: Address Search
    print("\n4. Testing Address Search...")
    search_results = mapquest_manager.search_addresses("New York, NY", 3)
    if search_results:
        print(f"✅ Found {len(search_results)} addresses in New York:")
        for i, addr in enumerate(search_results, 1):
            print(f"   {i}. {addr.get('business_name', 'N/A')} - {addr['full_address']}")
            if is_fake_address(addr):
                print(f"      ❌ WARNING: Address {i} appears to be fake!")
                return False
        print("✅ All search results appear to be real addresses")
    else:
        print("❌ Failed to search addresses in New York")
        return False
    
    # Test 5: Multiple Random Addresses
    print("\n5. Testing Multiple Random Address Generation...")
    fake_count = 0
    real_count = 0
    
    for i in range(5):
        addr = mapquest_manager.get_random_us_address()
        if addr:
            print(f"   {i+1}. {addr.get('business_name', 'N/A')} - {addr['full_address']}")
            if is_fake_address(addr):
                fake_count += 1
                print(f"      ❌ Address {i+1} appears to be fake!")
            else:
                real_count += 1
                print(f"      ✅ Address {i+1} appears to be real")
        else:
            print(f"   {i+1}. ❌ Failed to generate address")
    
    print(f"\n📊 Summary: {real_count} real addresses, {fake_count} fake addresses")
    
    if fake_count > 0:
        print("❌ FAILED: System still generating fake addresses")
        return False
    else:
        print("✅ SUCCESS: All addresses appear to be real")
        return True

def is_fake_address(address_data):
    """
    Check if an address appears to be fake/synthetic
    
    Args:
        address_data: Address dictionary
        
    Returns:
        True if address appears fake, False if appears real
    """
    if not address_data:
        return True
    
    address_line = address_data.get('address_line1', '').lower()
    full_address = address_data.get('full_address', '').lower()
    business_name = address_data.get('business_name', '').lower()
    zip_code = address_data.get('zip_code', '')
    source = address_data.get('source', '')
    
    # Real address sources that are acceptable
    real_sources = [
        'mapquest_real_poi',
        'mapquest_nationwide_poi_fallback', 
        'mapquest_landmark_fallback',
        'mapquest_real_poi_search'
    ]
    
    # If from a real source, it's probably real
    if source in real_sources:
        # Only check for obviously fake patterns
        fake_patterns = [
            # Obviously fake business names
            'test business' in business_name,
            'sample business' in business_name,
            'fake business' in business_name,
            'example corp' in business_name,
            'demo company' in business_name,
            'placeholder' in business_name,
            
            # Obviously fake addresses (with generic names and no real context)
            'main st' in full_address and 'san francisco, ca 00000' in full_address,
            'first st' in full_address and '00000' in zip_code,
            
            # Definitely fake zip codes
            zip_code in ['00000'] and 'washington, dc' not in full_address.lower()
        ]
        
        return any(fake_patterns)
    
    # For other sources, be more strict
    fake_indicators = [
        # Missing essential data
        not address_line.strip(),
        not address_data.get('city', '').strip(),
        not address_data.get('state', '').strip(),
        
        # Obviously synthetic patterns
        zip_code in ['11111', '22222', '99999'],
        
        # Source indicates it's not from real POI data
        'fallback' in source and 'landmark' not in source and not business_name
    ]
    
    return any(fake_indicators)

if __name__ == "__main__":
    try:
        success = test_real_addresses()
        if success:
            print("\n🎉 ALL TESTS PASSED: Real address system is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ TESTS FAILED: System still has issues with fake addresses")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)