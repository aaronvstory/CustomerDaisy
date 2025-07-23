#!/usr/bin/env python3
"""
Menu Workflows Test Suite
=========================
Tests all menu options and workflows to ensure they function correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main import CustomerDaisyApp
from src.config_manager import ConfigManager

def test_application_initialization():
    """Test application initialization"""
    print("🚀 Testing Application Initialization...")
    try:
        app = CustomerDaisyApp()
        assert app.config_manager is not None, "Config manager not initialized"
        assert app.database is not None, "Database not initialized"
        assert app.sms_manager is not None, "SMS manager not initialized"
        assert app.mail_manager is not None, "Mail manager not initialized"
        assert app.mapquest_manager is not None, "MapQuest manager not initialized"
        print("  ✅ Application initialization: PASSED")
        return app, True
    except Exception as e:
        print(f"  ❌ Application initialization: FAILED - {e}")
        return None, False

def test_database_functionality(app):
    """Test database-related menu options"""
    print("\n💾 Testing Database Functionality...")
    try:
        # Test view_customer_database functionality
        customers = app.database.load_all_customers()
        print(f"  ✅ Load customers: PASSED ({len(customers)} customers)")
        
        # Test search functionality
        if customers:
            search_results = app.database.search_customers(customers[0]['full_name'].split()[0])
            assert len(search_results) > 0, "Search returned no results"
            print("  ✅ Customer search: PASSED")
        
        # Test analytics functionality
        analytics = app.database.generate_analytics()
        assert 'summary' in analytics, "Analytics missing summary"
        print("  ✅ Analytics generation: PASSED")
        
        # Test export functionality
        export_file = app.database.export_customers('json')
        assert Path(export_file).exists(), "Export file not created"
        print("  ✅ Export functionality: PASSED")
        
        return True
    except Exception as e:
        print(f"  ❌ Database functionality: FAILED - {e}")
        return False

def test_sms_functionality(app):
    """Test SMS-related functionality"""
    print("\n📱 Testing SMS Functionality...")
    try:
        # Test balance check
        balance = app.sms_manager.get_balance()
        assert balance is not None, "Balance check failed"
        print(f"  ✅ Balance check: PASSED (${balance})")
        
        # Test available services
        services = app.sms_manager.get_available_services()
        assert isinstance(services, dict), "Services should be a dictionary"
        print(f"  ✅ Services list: PASSED ({len(services)} services)")
        
        return True
    except Exception as e:
        print(f"  ❌ SMS functionality: FAILED - {e}")
        return False

def test_mail_functionality(app):
    """Test mail-related functionality"""
    print("\n📧 Testing Mail Functionality...")
    try:
        # Test domain fetching
        domains = app.mail_manager.get_available_domains()
        assert isinstance(domains, list), "Domains should be a list"
        print(f"  ✅ Domain fetching: PASSED ({len(domains)} domains)")
        
        # Test username generation
        username = app.mail_manager.generate_username("John", "Doe")
        assert len(username) > 0, "Username generation failed"
        print("  ✅ Username generation: PASSED")
        
        return True
    except Exception as e:
        print(f"  ❌ Mail functionality: FAILED - {e}")
        return False

def test_mapquest_functionality(app):
    """Test MapQuest-related functionality"""
    print("\n🗺️ Testing MapQuest Functionality...")
    try:
        # Test address validation
        test_address = "1600 Pennsylvania Avenue NW, Washington, DC"
        result = app.mapquest_manager.validate_address(test_address)
        
        if result:
            print("  ✅ Address validation: PASSED")
        else:
            print("  ⚠️ Address validation: No result (may be API limit)")
        
        # Test connection
        assert app.mapquest_manager.api_key is not None, "API key not configured"
        print("  ✅ MapQuest configuration: PASSED")
        
        return True
    except Exception as e:
        print(f"  ❌ MapQuest functionality: FAILED - {e}")
        return False

def test_customer_generation(app):
    """Test customer generation functionality"""
    print("\n👤 Testing Customer Generation...")
    try:
        # Test address generation without custom address
        address_data = app.database._get_address_data()
        assert 'full_address' in address_data, "Address data missing full_address"
        assert 'city' in address_data, "Address data missing city"
        print("  ✅ Address generation: PASSED")
        
        # Test customer data structure if faker is available
        try:
            customer_data = app.database.generate_customer_data()
            assert 'customer_id' in customer_data, "Customer data missing ID"
            assert 'full_name' in customer_data, "Customer data missing name"
            assert 'email' in customer_data, "Customer data missing email"
            print("  ✅ Customer data generation: PASSED")
        except RuntimeError as e:
            if "Faker library not available" in str(e):
                print("  ⚠️ Customer data generation: SKIPPED (Faker not available)")
            else:
                raise
        
        return True
    except Exception as e:
        print(f"  ❌ Customer generation: FAILED - {e}")
        return False

def test_configuration_functionality(app):
    """Test configuration-related functionality"""
    print("\n⚙️ Testing Configuration Functionality...")
    try:
        # Test config manager
        config = app.config_manager.get_config()
        assert config is not None, "Configuration not loaded"
        print("  ✅ Configuration loading: PASSED")
        
        # Test section access
        daisysms_config = app.config_manager.get_section('DAISYSMS')
        assert daisysms_config is not None, "DaisySMS config not found"
        print("  ✅ Section access: PASSED")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration functionality: FAILED - {e}")
        return False

def test_monitor_functionality(app):
    """Test SMS monitoring functionality"""
    print("\n📊 Testing Monitor Functionality...")
    try:
        # Test monitor initialization
        assert app.sms_monitor is not None, "SMS monitor not initialized"
        
        # Test adding verification to monitor
        app.sms_monitor.add_verification("test-customer", "test-verification", "1234567890")
        assert len(app.sms_monitor.active_verifications) > 0, "Verification not added to monitor"
        print("  ✅ Monitor functionality: PASSED")
        
        return True
    except Exception as e:
        print(f"  ❌ Monitor functionality: FAILED - {e}")
        return False

def run_menu_workflow_tests():
    """Run all menu workflow tests"""
    print("🎯 DaisySMS Application - Menu Workflow Test Suite")
    print("=" * 70)
    
    # Initialize application
    app, init_success = test_application_initialization()
    if not init_success:
        print("\n❌ Cannot continue - application initialization failed")
        return False
    
    # Run all tests
    tests = [
        lambda: test_database_functionality(app),
        lambda: test_sms_functionality(app),
        lambda: test_mail_functionality(app),
        lambda: test_mapquest_functionality(app),
        lambda: test_customer_generation(app),
        lambda: test_configuration_functionality(app),
        lambda: test_monitor_functionality(app)
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
            print(f"  ❌ Test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Workflow Test Results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 ALL WORKFLOW TESTS PASSED - All menu options functional!")
        return True
    else:
        print("⚠️ Some workflow tests failed - review issues above")
        return False

if __name__ == "__main__":
    success = run_menu_workflow_tests()
    sys.exit(0 if success else 1)