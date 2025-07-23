#!/usr/bin/env python3
"""
Test script to diagnose Mail.tm configuration issue
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.mail_tm import MailTmManager

def test_mailtm_configuration():
    """Test how Mail.tm configuration is loaded and passed"""
    print("🔧 Testing Mail.tm Configuration")
    print("=" * 50)
    
    # Load configuration
    config_manager = ConfigManager()
    print(f"Configuration file exists: {Path('config.ini').exists()}")
    
    # Get the MAILTM section
    mailtm_config = config_manager.get_section('MAILTM')
    print("\n📋 MAILTM Configuration Section:")
    for key, value in mailtm_config.items():
        if 'password' in key.lower():
            print(f"  {key}: {'*' * len(value)} (hidden)")
        else:
            print(f"  {key}: {value}")
    
    # Test the Mail.tm manager initialization
    print("\n📧 Testing MailTmManager initialization...")
    try:
        mail_manager = MailTmManager(mailtm_config)
        print(f"✅ MailTmManager initialized successfully")
        print(f"   Base URL: {mail_manager.base_url}")
        print(f"   Password: {'*' * len(mail_manager.password)} (hidden)")
        print(f"   Domain Cache Duration: {mail_manager.domain_cache_duration}")
        
        # Test account creation with fake data
        print("\n🧪 Testing account creation process...")
        print("   This will test the configuration but not actually create an account")
        
        # Check what password would be used
        print(f"   Configured password length: {len(mail_manager.password)} characters")
        print(f"   Password starts with: {mail_manager.password[:3]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ MailTmManager initialization failed: {e}")
        return False

def test_password_retrieval():
    """Test password retrieval from different sources"""
    print("\n🔍 Testing Password Retrieval Sources")
    print("=" * 50)
    
    # Test direct config file reading
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if config.has_section('MAILTM'):
        direct_password = config.get('MAILTM', 'default_password', fallback='NOT_FOUND')
        print(f"Direct config.ini read: {direct_password}")
    else:
        print("❌ MAILTM section not found in config.ini")
    
    # Test ConfigManager retrieval
    config_manager = ConfigManager()
    manager_password = config_manager.get_value('MAILTM', 'default_password', 'NOT_FOUND')
    print(f"ConfigManager get_value: {manager_password}")
    
    # Test section retrieval
    section = config_manager.get_section('MAILTM')
    section_password = section.get('default_password', 'NOT_FOUND')
    print(f"Section dict get: {section_password}")
    
    # Test environment variable override
    env_password = os.getenv('MAILTM_PASSWORD')
    if env_password:
        print(f"Environment override: {env_password}")
    else:
        print("No environment variable override")
    
    return True

def test_account_creation_simulation():
    """Simulate account creation to see what password is used"""
    print("\n🎭 Simulating Account Creation")
    print("=" * 50)
    
    try:
        config_manager = ConfigManager()
        mailtm_config = config_manager.get_section('MAILTM')
        mail_manager = MailTmManager(mailtm_config)
        
        # Simulate what would happen in create_account
        print("Account creation would use:")
        print(f"  Password: {mail_manager.password}")
        print(f"  Password length: {len(mail_manager.password)}")
        
        # Show what the account data would look like
        test_email = "test@example.com"
        account_data = {
            "address": test_email,
            "password": mail_manager.password
        }
        
        print(f"  Account data would be: {account_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Mail.tm Configuration Diagnosis")
    print("=" * 60)
    
    tests = [
        ("Mail.tm Configuration Test", test_mailtm_configuration),
        ("Password Retrieval Test", test_password_retrieval),
        ("Account Creation Simulation", test_account_creation_simulation),
    ]
    
    results = []
    for test_name, test_func in tests:
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
        print("🎉 All configuration tests passed!")
    else:
        print("⚠️ Some configuration issues detected.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    main()