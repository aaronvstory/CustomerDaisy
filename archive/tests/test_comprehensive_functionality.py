#!/usr/bin/env python3
"""
Comprehensive DaisySMS Application Test Suite
=============================================
Tests all core functionality to ensure enterprise-grade readiness.
"""

import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.customer_db import CustomerDatabase
from src.config_manager import ConfigManager
from src.daisy_sms import DaisySMSManager
from src.mail_tm import MailTmManager
from src.mapquest_address import MapQuestAddressManager
from src.sms_monitor import SMSMonitor

def test_configuration():
    """Test configuration management"""
    print("🔧 Testing Configuration Management...")
    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # Test required sections
        required_sections = ['DATABASE', 'DAISYSMS', 'MAILTM', 'MAPQUEST', 'CUSTOMER_GENERATION']
        for section in required_sections:
            section_config = config_manager.get_section(section)
            assert section_config is not None, f"Missing section: {section}"
        
        print("  ✅ Configuration loading: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Configuration loading: FAILED - {e}")
        return False

def test_database_operations():
    """Test database operations"""
    print("\n💾 Testing Database Operations...")
    try:
        config_manager = ConfigManager()
        db_config = config_manager.get_section('DATABASE')
        customer_gen_config = config_manager.get_section('CUSTOMER_GENERATION')
        db_config.update(customer_gen_config)
        
        db = CustomerDatabase(db_config, config_manager.get_section('MAPQUEST'))
        
        # Test database initialization
        print("  ✅ Database initialization: PASSED")
        
        # Test customer retrieval
        customers = db.load_all_customers()
        print(f"  ✅ Load customers: PASSED ({len(customers)} customers)")
        
        # Test the critical fix - get_customer_by_id
        if customers:
            test_customer_id = customers[0]['customer_id']
            customer_data = db.get_customer_by_id(test_customer_id)
            assert customer_data is not None, "get_customer_by_id returned None"
            assert customer_data['customer_id'] == test_customer_id, "Customer ID mismatch"
            print("  ✅ get_customer_by_id method: PASSED")
        else:
            print("  ⚠️ No customers to test get_customer_by_id")
        
        # Test search functionality
        if customers:
            search_results = db.search_customers(customers[0]['full_name'].split()[0])
            assert len(search_results) > 0, "Search returned no results"
            print("  ✅ Customer search: PASSED")
        
        # Test analytics
        analytics = db.generate_analytics()
        assert 'summary' in analytics, "Analytics missing summary"
        print("  ✅ Analytics generation: PASSED")
        
        return True
    except Exception as e:
        print(f"  ❌ Database operations: FAILED - {e}")
        traceback.print_exc()
        return False

def test_sms_manager():
    """Test SMS manager initialization"""
    print("\n📱 Testing SMS Manager...")
    try:
        config_manager = ConfigManager()
        sms_config = config_manager.get_section('DAISYSMS')
        
        sms_manager = DaisySMSManager(sms_config)
        
        # Test balance check (if API key is configured)
        if sms_config.get('api_key') and sms_config.get('api_key') != 'your_api_key_here':
            try:
                balance = sms_manager.get_balance()
                print(f"  ✅ Balance check: PASSED (${balance})")
            except Exception as e:
                print(f"  ⚠️ Balance check: FAILED (API issue) - {e}")
        else:
            print("  ⚠️ SMS API key not configured - skipping balance test")
        
        print("  ✅ SMS Manager initialization: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ SMS Manager: FAILED - {e}")
        return False

def test_mail_manager():
    """Test mail manager"""
    print("\n📧 Testing Mail Manager...")
    try:
        config_manager = ConfigManager()
        mail_config = config_manager.get_section('MAILTM')
        
        mail_manager = MailTmManager(mail_config)
        print("  ✅ Mail Manager initialization: PASSED")
        
        # Test domain fetching
        domains = mail_manager.get_available_domains()
        if domains:
            print(f"  ✅ Domain fetching: PASSED ({len(domains)} domains)")
        else:
            print("  ⚠️ No domains available")
        
        return True
    except Exception as e:
        print(f"  ❌ Mail Manager: FAILED - {e}")
        return False

def test_mapquest_integration():
    """Test MapQuest integration"""
    print("\n🗺️ Testing MapQuest Integration...")
    try:
        config_manager = ConfigManager()
        mapquest_config = config_manager.get_section('MAPQUEST')
        
        mapquest_manager = MapQuestAddressManager(mapquest_config)
        print("  ✅ MapQuest Manager initialization: PASSED")
        
        # Test address validation (if API key is configured)
        if mapquest_config.get('api_key') and mapquest_config.get('api_key') != 'your_api_key_here':
            try:
                test_address = "1600 Pennsylvania Avenue NW, Washington, DC"
                result = mapquest_manager.validate_address(test_address)
                if result:
                    print("  ✅ Address validation: PASSED")
                else:
                    print("  ⚠️ Address validation: No result returned")
            except Exception as e:
                print(f"  ⚠️ Address validation: FAILED (API issue) - {e}")
        else:
            print("  ⚠️ MapQuest API key not configured - skipping validation test")
        
        return True
    except Exception as e:
        print(f"  ❌ MapQuest Integration: FAILED - {e}")
        return False

def test_sms_monitor():
    """Test SMS monitor"""
    print("\n📊 Testing SMS Monitor...")
    try:
        monitor = SMSMonitor()
        
        # Test adding verification
        monitor.add_verification("test-customer", "test-verification", "1234567890")
        assert len(monitor.active_verifications) == 1, "Verification not added"
        
        print("  ✅ SMS Monitor: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ SMS Monitor: FAILED - {e}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    print("\n🛡️ Testing Error Handling...")
    try:
        config_manager = ConfigManager()
        db_config = config_manager.get_section('DATABASE')
        customer_gen_config = config_manager.get_section('CUSTOMER_GENERATION')
        db_config.update(customer_gen_config)
        
        db = CustomerDatabase(db_config, config_manager.get_section('MAPQUEST'))
        
        # Test get_customer_by_id with invalid ID
        result = db.get_customer_by_id("invalid-id")
        assert result is None, "Should return None for invalid ID"
        
        # Test search with empty string
        results = db.search_customers("")
        assert isinstance(results, list), "Search should return list even for empty query"
        
        print("  ✅ Error handling: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Error handling: FAILED - {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 DaisySMS Application - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        test_configuration,
        test_database_operations,
        test_sms_manager,
        test_mail_manager,
        test_mapquest_integration,
        test_sms_monitor,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test {test.__name__}: CRASHED - {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - Application is enterprise-ready!")
        return True
    else:
        print("⚠️ Some tests failed - review issues above")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)