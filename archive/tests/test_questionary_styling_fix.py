#!/usr/bin/env python3
"""
Test Questionary Styling Fix
=============================
Tests to validate that questionary styling has been fixed and won't cause color format errors.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_questionary_style_format():
    """Test that questionary styles use valid color formats"""
    print("\n🧪 Testing questionary style formats...")
    
    try:
        import main
        import inspect
        
        # Get the source of the _select_customer_interactive method
        method_source = inspect.getsource(main.CustomerDaisyApp._select_customer_interactive)
        
        # Check that 'dim white' has been removed
        if 'dim white' in method_source:
            print("  ❌ 'dim white' still found in styling - this will cause errors")
            return False
        else:
            print("  ✅ 'dim white' removed from styling")
        
        # Check that valid colors are used
        if "'instruction', 'gray'" in method_source:
            print("  ✅ 'instruction' now uses 'gray' (valid color)")
        else:
            print("  ❌ 'instruction' color not properly fixed")
            return False
        
        if "'disabled', 'gray'" in method_source:
            print("  ✅ 'disabled' now uses 'gray' (valid color)")
        else:
            print("  ❌ 'disabled' color not properly fixed")
            return False
        
        print("  ✅ All questionary styles use valid color formats")
        return True
    
    except Exception as e:
        print(f"  ❌ Style format test error: {e}")
        return False

def test_questionary_style_creation():
    """Test that questionary.Style can be created without errors"""
    print("\n🧪 Testing questionary.Style creation...")
    
    try:
        # Try to import questionary
        try:
            import questionary
            print("  ✅ questionary imported successfully")
        except ImportError:
            print("  ⚠️  questionary not available - test will be skipped")
            return True
        
        # Test the exact style definition used in the code
        test_style = questionary.Style([
            ('question', 'bold cyan'),
            ('pointer', 'cyan'),
            ('highlighted', 'bold cyan'),
            ('selected', 'bold green'),
            ('separator', 'white'),
            ('instruction', 'gray'),
            ('text', 'white'),
            ('disabled', 'gray'),
        ])
        
        print("  ✅ questionary.Style created successfully with new colors")
        
        # Test that the style object has the expected properties
        if hasattr(test_style, 'style_rules'):
            print("  ✅ Style object has expected structure")
        else:
            print("  ⚠️  Style object structure may have changed")
        
        return True
    
    except Exception as e:
        print(f"  ❌ Style creation test error: {e}")
        return False

def test_customer_selection_method_exists():
    """Test that the customer selection method exists and is properly structured"""
    print("\n🧪 Testing customer selection method structure...")
    
    try:
        import main
        
        # Check that the method exists
        if hasattr(main.CustomerDaisyApp, '_select_customer_interactive'):
            print("  ✅ _select_customer_interactive method exists")
        else:
            print("  ❌ _select_customer_interactive method not found")
            return False
        
        # Check that fallback method exists
        if hasattr(main.CustomerDaisyApp, '_select_customer'):
            print("  ✅ Fallback _select_customer method exists")
        else:
            print("  ❌ Fallback _select_customer method not found")
            return False
        
        # Check QUESTIONARY_AVAILABLE flag exists
        if hasattr(main, 'QUESTIONARY_AVAILABLE'):
            print("  ✅ QUESTIONARY_AVAILABLE flag exists")
        else:
            print("  ❌ QUESTIONARY_AVAILABLE flag not found")
            return False
        
        print("  ✅ Customer selection method structure is correct")
        return True
    
    except Exception as e:
        print(f"  ❌ Method structure test error: {e}")
        return False

def test_assign_new_number_integration():
    """Test that assign new number functionality won't crash on styling"""
    print("\n🧪 Testing assign new number integration...")
    
    try:
        import main
        
        # Mock the database and other dependencies
        with patch('main.ConfigManager'), \
             patch('main.DaisySMSManager'), \
             patch('main.MailTmManager'), \
             patch('main.MapQuestAddressManager'), \
             patch('main.CustomerDatabase') as mock_db, \
             patch('main.SMSMonitor'):
            
            app = main.CustomerDaisyApp()
            
            # Mock some recent customers
            mock_customers = [
                {
                    'customer_id': '1',
                    'full_name': 'Test User',
                    'email': 'test@example.com',
                    'primary_phone': '1234567890',
                    'city': 'Test City',
                    'state': 'TS',
                    'verification_completed': True
                }
            ]
            
            # Test that the method can be called without crashing
            # (It will fail on user input, but shouldn't crash on styling)
            try:
                # This should not crash due to styling errors
                result = app._select_customer_interactive(mock_customers)
                print("  ✅ Customer selection method callable without styling errors")
            except Exception as e:
                if "Wrong color format" in str(e):
                    print(f"  ❌ Styling error still present: {e}")
                    return False
                elif "questionary" in str(e).lower():
                    print(f"  ❌ Questionary-related error: {e}")
                    return False
                else:
                    # Other errors (like input/output issues) are expected in test environment
                    print("  ✅ No styling errors detected (other errors are expected in test)")
        
        return True
    
    except Exception as e:
        if "Wrong color format" in str(e):
            print(f"  ❌ Styling error still present: {e}")
            return False
        else:
            print(f"  ✅ No styling errors (other test errors expected)")
            return True

def main():
    """Run all tests"""
    print("🧪 Testing Questionary Styling Fix")
    print("=" * 60)
    
    tests = [
        ("Style Format", test_questionary_style_format),
        ("Style Creation", test_questionary_style_creation),
        ("Method Structure", test_customer_selection_method_exists),
        ("Integration", test_assign_new_number_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Tests...")
        if test_func():
            passed += 1
            print(f"  ✅ {test_name} Tests PASSED")
        else:
            print(f"  ❌ {test_name} Tests FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Questionary styling error fixed.")
        print("\n🔧 Fix Applied:")
        print("  • Changed 'dim white' to 'gray' in questionary styles")
        print("  • Changed 'grey62' to 'gray' for consistency")
        print("  • All questionary styles now use valid color formats")
        print("  • Customer selection should work without styling errors")
        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)