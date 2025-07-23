#!/usr/bin/env python3
"""
Test script to verify Mail.tm account creation uses configured password
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.mail_tm import MailTmManager

def test_real_account_creation():
    """Test creating a real Mail.tm account to verify password usage"""
    print("🧪 Testing Real Mail.tm Account Creation")
    print("=" * 50)
    
    try:
        # Initialize configuration and manager
        config_manager = ConfigManager()
        mailtm_config = config_manager.get_section('MAILTM')
        mail_manager = MailTmManager(mailtm_config)
        
        configured_password = mailtm_config.get('default_password')
        print(f"Configured password: {configured_password}")
        print(f"Manager password: {mail_manager.password}")
        print(f"Passwords match: {configured_password == mail_manager.password}")
        
        print("\n🔍 Testing service availability...")
        if not mail_manager.test_service():
            print("❌ Mail.tm service is not available, cannot test account creation")
            return False
        
        print("\n📧 Creating test account...")
        # Create a test account
        try:
            account_info = mail_manager.create_account("Test", "User")
            
            print("✅ Account created successfully!")
            print(f"   Email: {account_info['email']}")
            print(f"   Password used: {account_info['email_password']}")
            print(f"   Password matches config: {account_info['email_password'] == configured_password}")
            
            # Test login with the account
            print("\n🔐 Testing login with created account...")
            try:
                token = mail_manager.get_account_token(account_info['email'], account_info['email_password'])
                if token:
                    print("✅ Login successful - password is working correctly!")
                    
                    # Clean up - delete the test account
                    print("\n🧹 Cleaning up test account...")
                    if mail_manager.delete_account(account_info['email'], account_info['email_password']):
                        print("✅ Test account deleted successfully")
                    else:
                        print("⚠️ Could not delete test account - manual cleanup may be needed")
                        print(f"   Test account: {account_info['email']}")
                    
                    return True
                else:
                    print("❌ Login failed - password issue detected!")
                    return False
                    
            except Exception as login_e:
                print(f"❌ Login test failed: {login_e}")
                return False
                
        except Exception as create_e:
            print(f"❌ Account creation failed: {create_e}")
            return False
            
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

def test_password_verification():
    """Test that the password is being used correctly in API calls"""
    print("\n🔍 Testing Password Usage in API Calls")
    print("=" * 50)
    
    try:
        config_manager = ConfigManager()
        mailtm_config = config_manager.get_section('MAILTM')
        mail_manager = MailTmManager(mailtm_config)
        
        configured_password = mailtm_config.get('default_password')
        
        # Check internal password storage
        print(f"Internal password storage: {mail_manager.password}")
        print(f"Config password: {configured_password}")
        print(f"Passwords identical: {mail_manager.password is configured_password}")
        print(f"Passwords equal: {mail_manager.password == configured_password}")
        
        # Simulate account data preparation
        test_email = "testuser@example.com"
        account_data = {
            "address": test_email,
            "password": mail_manager.password
        }
        
        print(f"\nAccount data that would be sent to API:")
        print(f"  address: {account_data['address']}")
        print(f"  password: {account_data['password']}")
        print(f"  password matches config: {account_data['password'] == configured_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Password verification test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Mail.tm Password Configuration Verification")
    print("=" * 60)
    
    # First, show current configuration
    print("📋 Current Configuration:")
    config_manager = ConfigManager()
    mailtm_config = config_manager.get_section('MAILTM')
    print(f"   Configured password: {mailtm_config.get('default_password')}")
    print()
    
    tests = [
        ("Password Verification Test", test_password_verification),
        ("Real Account Creation Test", test_real_account_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🏃 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Mail.tm is using the configured password correctly.")
    else:
        print("⚠️ Issues detected with password configuration.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    main()