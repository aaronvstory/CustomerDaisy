#!/usr/bin/env python3
"""
Test the fix for single check not cancelling verification
"""
import sys
sys.path.append('.')

from src.daisy_sms import DaisySMSManager
from datetime import datetime, timedelta

def test_single_check_fix():
    """Test that single checks don't cancel verification"""
    print("🧪 Testing Single Check Fix")
    print("=" * 50)
    
    # Create mock DaisySMS manager
    config = {
        'api_key': 'test_key',
        'base_url': 'https://daisysms.com/stubs/handler_api.php',
        'service_code': 'ds',
        'max_price': '0.50',
        'verification_timeout': '180',
        'polling_interval': '3'
    }
    
    sms_manager = DaisySMSManager(config)
    
    # Create a verification
    mock_verification_id = "test_12345"
    now = datetime.now()
    timeout_at = now + timedelta(seconds=sms_manager.verification_timeout)
    
    verification_info = {
        'verification_id': mock_verification_id,
        'phone_number': '1234567890',
        'status': 'rented',
        'created_at': now,
        'timeout_at': timeout_at
    }
    
    sms_manager.active_verifications[mock_verification_id] = verification_info
    
    # Mock the _make_request to return STATUS_WAIT_CODE
    def mock_make_request(action, params=None):
        if action == 'getStatus':
            return {
                'status': 'STATUS_WAIT_CODE',
                'data': None,
                'raw_response': 'STATUS_WAIT_CODE'
            }
        elif action == 'setStatus' and params and params.get('status') == '8':
            return {
                'status': 'ACCESS_CANCEL',
                'data': None,
                'raw_response': 'ACCESS_CANCEL'
            }
        return {'status': 'error', 'message': 'Unknown action'}
    
    sms_manager._make_request = mock_make_request
    
    print("\n1. Testing single check (should NOT cancel)...")
    result = sms_manager.get_sms_code(mock_verification_id, max_attempts=1, silent=False)
    
    verification_info = sms_manager.active_verifications.get(mock_verification_id)
    if verification_info:
        status = verification_info.get('status')
        print(f"   Status after single check: {status}")
        if status == 'rented':
            print("   ✅ Single check did NOT cancel verification")
        else:
            print("   ❌ Single check incorrectly cancelled verification")
    else:
        print("   ❌ Verification info missing after single check")
    
    print("\n2. Testing multiple attempts (should cancel after timeout)...")
    result = sms_manager.get_sms_code(mock_verification_id, max_attempts=3, silent=False)
    
    verification_info = sms_manager.active_verifications.get(mock_verification_id)
    if verification_info:
        status = verification_info.get('status')
        print(f"   Status after multiple attempts: {status}")
        if status == 'cancelled':
            print("   ✅ Multiple attempts correctly cancelled verification")
        else:
            print("   ❌ Multiple attempts did not cancel verification")
    else:
        print("   ❌ Verification info missing after multiple attempts")
    
    print("\n🎉 Single check fix test complete!")

if __name__ == "__main__":
    test_single_check_fix()