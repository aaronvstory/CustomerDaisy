#!/usr/bin/env python3
"""Test questionary interface to demonstrate enhanced experience"""

try:
    import questionary
    from questionary import Choice
    QUESTIONARY_AVAILABLE = True
    print("✅ Questionary available!")
except ImportError:
    QUESTIONARY_AVAILABLE = False
    print("❌ Questionary not available")

def test_main_menu():
    """Test the enhanced main menu interface"""
    if not QUESTIONARY_AVAILABLE:
        print("Cannot test - questionary not installed")
        return
    
    print("\n🧪 Testing Enhanced Main Menu Interface...")
    
    try:
        choices = [
            Choice("🌸 Create New Customer (with MapQuest addresses)", value="1"),
            Choice("📱 Get SMS Code for Existing Customer", value="2"),
            Choice("🔄 Assign New Number to Customer", value="3"),
            Choice("📊 View Customer Database", value="4"),
            Choice("📡 SMS Activity Monitor", value="5"),
            Choice("📈 Performance Analytics", value="6"),
            Choice("📤 Export Customer Data", value="7"),
            Choice("💰 DaisySMS Account Status", value="8"),
            Choice("🗺️ Address Management & Testing", value="9"),
            Choice("⚙️ Configuration Settings", value="c"),
            Choice("🚪 Exit Application", value="0")
        ]
        
        selection = questionary.select(
            "Select an action:",
            choices=choices
        ).ask()
        
        print(f"\n✅ You selected: {selection}")
        return selection
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_address_selection():
    """Test address selection interface"""
    if not QUESTIONARY_AVAILABLE:
        print("Cannot test - questionary not installed")
        return
        
    print("\n🧪 Testing Enhanced Address Selection...")
    
    try:
        choices = [
            Choice("📍 Select from recent addresses", value="recent"),
            Choice("➕ Enter custom address", value="custom"),
            Choice("🗺️ Near location (search around a city)", value="near"),
            Choice("🔍 Interactive selection (with auto-complete)", value="interactive"),
            Choice("🎲 Random US address", value="random")
        ]
        
        selection = questionary.select(
            "🏠 Choose address option:",
            choices=choices
        ).ask()
        
        print(f"\n✅ You selected: {selection}")
        return selection
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_confirmation():
    """Test enhanced confirmation dialog"""
    if not QUESTIONARY_AVAILABLE:
        print("Cannot test - questionary not installed")
        return
        
    print("\n🧪 Testing Enhanced Confirmation Dialog...")
    
    try:
        result = questionary.confirm(
            "Would you like to create a new customer?",
            default=False
        ).ask()
        
        print(f"\n✅ You selected: {'Yes' if result else 'No'}")
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_text_input():
    """Test enhanced text input"""
    if not QUESTIONARY_AVAILABLE:
        print("Cannot test - questionary not installed")
        return
        
    print("\n🧪 Testing Enhanced Text Input...")
    
    try:
        result = questionary.text(
            "🗺️ Enter city or address to search near:",
            default="New York"
        ).ask()
        
        print(f"\n✅ You entered: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 CustomerDaisy Enhanced Interface Test")
    print("=" * 50)
    
    # Run tests
    test_main_menu()
    test_address_selection()  
    test_confirmation()
    test_text_input()
    
    print("\n🎉 Test completed! In a real terminal, you would see:")
    print("   • Arrow key navigation")
    print("   • Beautiful highlighting")
    print("   • No more number typing!")
    print("   • Consistent modern interface")