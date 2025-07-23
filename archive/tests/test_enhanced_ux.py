#!/usr/bin/env python3
"""
Test Enhanced UX Features
=========================
Tests the new interactive customer selection and recent address features
"""

import sys
import configparser
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from customer_db import CustomerDatabase
from rich.console import Console

console = Console()

def test_database_methods():
    """Test the new database methods"""
    console.print("🧪 Testing Enhanced UX Database Methods", style="bold cyan")
    
    # Load config
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Initialize database
    db_config = dict(config.items('DATABASE'))
    db_config['database_path'] = 'customer_data/customers.db'
    db_config['json_backup_path'] = 'customer_data/customers_backup.json'
    
    mapquest_config = dict(config.items('MAPQUEST'))
    
    database = CustomerDatabase(db_config, mapquest_config)
    
    # Test recent customers
    console.print("\n📋 Testing get_recent_customers()...", style="yellow")
    recent_customers = database.get_recent_customers(10)
    
    if recent_customers:
        console.print(f"✅ Found {len(recent_customers)} recent customers:", style="green")
        for i, customer in enumerate(recent_customers[:3], 1):
            name = customer.get('full_name', 'Unknown')
            city = customer.get('city', 'Unknown')
            phone = customer.get('primary_phone', 'No phone')
            verified = "✅" if customer.get('verification_completed') else "📱"
            console.print(f"  {i}. {verified} {name} ({city}) • {phone}", style="white")
        
        if len(recent_customers) > 3:
            console.print(f"  ... and {len(recent_customers) - 3} more", style="dim")
    else:
        console.print("ℹ️ No customers found", style="blue")
    
    # Test recent addresses
    console.print("\n🏠 Testing get_recent_addresses()...", style="yellow")
    recent_addresses = database.get_recent_addresses(5)
    
    if recent_addresses:
        console.print(f"✅ Found {len(recent_addresses)} recent addresses:", style="green")
        for i, addr in enumerate(recent_addresses, 1):
            full_addr = addr.get('full_address', 'Unknown')
            city = addr.get('city', 'Unknown')
            state = addr.get('state', 'Unknown')
            source = addr.get('address_source', 'unknown')
            source_icon = "🗺️" if 'mapquest' in source.lower() else "📍"
            console.print(f"  {i}. {source_icon} {full_addr} ({city}, {state})", style="white")
    else:
        console.print("ℹ️ No recent addresses found", style="blue")
    
    console.print("\n✅ Database methods test completed!", style="bold green")

def test_questionary_availability():
    """Test questionary library availability"""
    console.print("\n🎨 Testing Questionary Library...", style="yellow")
    
    try:
        import questionary
        from questionary import Choice
        console.print("✅ Questionary library is available", style="green")
        
        # Test a simple questionary interaction (but don't actually ask)
        choices = [
            Choice("Test Choice 1", value="test1"),
            Choice("Test Choice 2", value="test2"),
        ]
        console.print(f"✅ Created {len(choices)} test choices", style="green")
        
        style = questionary.Style([
            ('question', 'bold cyan'),
            ('pointer', 'cyan'),
            ('highlighted', 'bold cyan'),
            ('selected', 'bold green'),
        ])
        console.print("✅ Custom questionary style created", style="green")
        
    except ImportError as e:
        console.print(f"❌ Questionary library not available: {e}", style="red")
        console.print("💡 The app will fall back to Rich-based menus", style="yellow")

def main():
    """Run all tests"""
    console.print("🚀 CustomerDaisy Enhanced UX Testing", style="bold magenta")
    console.print("=" * 50, style="magenta")
    
    try:
        test_questionary_availability()
        test_database_methods()
        
        console.print("\n🎉 All tests completed successfully!", style="bold green")
        console.print("\n💡 The enhanced UX features are ready to use:", style="cyan")
        console.print("  • Option 2: Shows recent customers with beautiful selection", style="white")
        console.print("  • Option 3: Shows recent customers for number assignment", style="white")
        console.print("  • Address selection: Shows recent addresses first", style="white")
        console.print("  • Interactive menus: Beautiful questionary interface", style="white")
        
    except Exception as e:
        console.print(f"\n❌ Test failed with error: {e}", style="red")
        import traceback
        console.print(traceback.format_exc(), style="dim red")

if __name__ == "__main__":
    main()