#!/usr/bin/env python3
"""
API Endpoints Test
Test all external API endpoints to ensure connectivity and functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config_manager import ConfigManager
from src.daisy_sms import DaisySMSManager
from src.mail_tm import MailTmManager
from src.mapquest_address import MapQuestAddressManager

def test_daisysms_api():
    """Test DaisySMS API endpoints"""
    print('🧪 Testing DaisySMS API endpoints...')
    try:
        config_manager = ConfigManager()
        sms_config = config_manager.get_section('DAISYSMS')
        sms_manager = DaisySMSManager(sms_config)
        
        # Test balance endpoint
        balance = sms_manager.get_balance()
        print(f'✅ Balance API: ${balance:.2f}')
        
        # Test services endpoint
        services = sms_manager.get_available_services()
        print(f'✅ Services API: {len(services)} services available')
        
        # Test pricing endpoint
        pricing = sms_manager.get_pricing_info()
        print(f'✅ Pricing API: Service {pricing.get("service", "unknown")} - ${pricing.get("price", 0):.2f}')
        
        print('🎉 All DaisySMS API endpoints working!')
        return True
    except Exception as e:
        print(f'❌ DaisySMS API error: {e}')
        return False

def test_mailtm_api():
    """Test Mail.tm API endpoints"""
    print('\n📧 Testing Mail.tm API endpoints...')
    try:
        config_manager = ConfigManager()
        mail_config = config_manager.get_section('MAILTM')
        mail_manager = MailTmManager(mail_config)
        
        # Test domains endpoint
        domains = mail_manager.get_available_domains()
        print(f'✅ Domains API: {len(domains)} domains available')
        
        print('🎉 All Mail.tm API endpoints working!')
        return True
    except Exception as e:
        print(f'❌ Mail.tm API error: {e}')
        return False

def test_mapquest_api():
    """Test MapQuest API endpoints"""
    print('\n🗺️ Testing MapQuest API endpoints...')
    try:
        config_manager = ConfigManager()
        mapquest_config = config_manager.get_section('MAPQUEST')
        mapquest_manager = MapQuestAddressManager(mapquest_config)
        
        # Test API connection
        if mapquest_manager.test_api_connection():
            print('✅ MapQuest API connection successful')
            
            # Test address validation
            test_address = "1600 Pennsylvania Avenue NW, Washington, DC"
            result = mapquest_manager.validate_address(test_address)
            if result:
                print(f'✅ Address validation API: {result["city"]}, {result["state"]}')
            else:
                print('⚠️ Address validation returned no result')
            
            print('🎉 All MapQuest API endpoints working!')
            return True
        else:
            print('❌ MapQuest API connection failed')
            return False
    except Exception as e:
        print(f'❌ MapQuest API error: {e}')
        return False

def main():
    """Run all API endpoint tests"""
    print('🚀 API Endpoints Comprehensive Test')
    print('=' * 50)
    
    tests = [
        test_daisysms_api,
        test_mailtm_api,
        test_mapquest_api
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
            print(f'❌ Test {test.__name__} crashed: {e}')
            failed += 1
    
    print('\n' + '=' * 50)
    print(f'📊 API Test Results: {passed} PASSED, {failed} FAILED')
    
    if failed == 0:
        print('🎉 ALL API ENDPOINTS WORKING!')
        return True
    else:
        print('⚠️ Some API endpoints failed')
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)