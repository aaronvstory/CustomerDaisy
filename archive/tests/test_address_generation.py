#!/usr/bin/env python3
"""
Test Address Generation
=======================
Debug the address generation issue
"""

from src.mapquest_address import MapQuestAddressManager
from src.config_manager import ConfigManager
from rich.console import Console

console = Console()

def test_address_generation():
    """Test address generation to debug empty street issue"""
    console.print("🧪 Testing Address Generation", style="bold cyan")
    
    # Initialize MapQuest manager
    config_manager = ConfigManager()
    mapquest_config = config_manager.get_section('MAPQUEST')
    
    if not mapquest_config.get('api_key'):
        console.print("❌ No MapQuest API key found", style="red")
        return
    
    mapquest_manager = MapQuestAddressManager(mapquest_config)
    
    # Test 1: Test API connection
    console.print("\n🔗 Testing API Connection...", style="blue")
    if mapquest_manager.test_api_connection():
        console.print("✅ API connection successful", style="green")
    else:
        console.print("❌ API connection failed", style="red")
        return
    
    # Test 2: Test random US address
    console.print("\n🎲 Testing Random US Address...", style="blue")
    for i in range(3):
        console.print(f"\n--- Test {i+1} ---", style="dim")
        result = mapquest_manager.get_random_us_address()
        
        if result:
            console.print(f"✅ Success!", style="green")
            console.print(f"   Full Address: {result['full_address']}", style="white")
            console.print(f"   Street: '{result['address_line1']}'", style="cyan")
            console.print(f"   City: '{result['city']}'", style="cyan")
            console.print(f"   State: '{result['state']}'", style="cyan")
            console.print(f"   Source: {result.get('source', 'unknown')}", style="dim")
        else:
            console.print(f"❌ Failed to get address", style="red")
    
    # Test 3: Test address near specific location
    console.print("\n🎯 Testing Address Near Location...", style="blue")
    test_locations = ["Philadelphia, PA", "Memphis, TN", "Louisville, KY"]
    
    for location in test_locations:
        console.print(f"\n--- Testing near {location} ---", style="dim")
        result = mapquest_manager.get_random_address_near_location(location)
        
        if result:
            console.print(f"✅ Success!", style="green")
            console.print(f"   Full Address: {result['full_address']}", style="white")
            console.print(f"   Street: '{result['address_line1']}'", style="cyan")
            console.print(f"   City: '{result['city']}'", style="cyan")
            console.print(f"   State: '{result['state']}'", style="cyan")
            console.print(f"   Source: {result.get('source', 'unknown')}", style="dim")
        else:
            console.print(f"❌ Failed to get address near {location}", style="red")

if __name__ == "__main__":
    test_address_generation() 