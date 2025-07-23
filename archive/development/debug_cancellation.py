#!/usr/bin/env python3
"""
Debug script to understand why SMS verification gets cancelled immediately
"""
import sys
sys.path.append('.')

from src.daisy_sms import DaisySMSManager
from datetime import datetime, timedelta
import time

def debug_cancellation():
    """Debug the SMS cancellation issue"""
    print("🐛 Debugging SMS Cancellation Issue")
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
    
    # Debug 1: Check timeout setting
    print(f"\n1. Timeout setting: {sms_manager.verification_timeout} seconds")
    
    # Debug 2: Create properly timed verification
    print("\n2. Creating verification with proper timeout...")
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
    
    print(f"   Created at: {now}")
    print(f"   Timeout at: {timeout_at}")
    print(f"   Time until timeout: {(timeout_at - now).total_seconds()} seconds")
    
    # Debug 3: Check immediate timeout condition
    print("\n3. Testing immediate timeout condition...")
    is_timed_out = datetime.now() > verification_info['timeout_at']
    print(f"   Is timed out now? {is_timed_out}")
    
    # Debug 4: Test what happens when we call get_sms_code
    print("\n4. Testing get_sms_code behavior...")
    
    # Mock the _make_request to return STATUS_WAIT_CODE
    original_make_request = sms_manager._make_request
    
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
        return original_make_request(action, params)
    
    sms_manager._make_request = mock_make_request
    
    # This should NOT cancel immediately
    print("   Calling get_sms_code with max_attempts=1...")
    result = sms_manager.get_sms_code(mock_verification_id, max_attempts=1, silent=False)
    
    # Check status after call
    verification_info = sms_manager.active_verifications.get(mock_verification_id)
    if verification_info:
        print(f"   Status after call: {verification_info.get('status')}")
    else:
        print("   Verification info not found after call")
    
    print(f"   Result: {result}")
    
    # Debug 5: Let's test the timeout check directly
    print("\n5. Testing timeout check logic...")
    
    # Create a verification that should timeout
    expired_id = "test_expired"
    expired_verification = {
        'verification_id': expired_id,
        'phone_number': '1234567890',
        'status': 'rented',
        'created_at': datetime.now() - timedelta(seconds=200),  # 200 seconds ago
        'timeout_at': datetime.now() - timedelta(seconds=20)   # 20 seconds ago (expired)
    }
    
    sms_manager.active_verifications[expired_id] = expired_verification
    
    print(f"   Created expired verification with timeout: {expired_verification['timeout_at']}")
    print(f"   Current time: {datetime.now()}")
    print(f"   Should timeout: {datetime.now() > expired_verification['timeout_at']}")
    
    # This should timeout and cancel
    result = sms_manager.get_sms_code(expired_id, max_attempts=1, silent=False)
    
    expired_info = sms_manager.active_verifications.get(expired_id)
    if expired_info:
        print(f"   Status after timeout call: {expired_info.get('status')}")
    
    print("\n🎯 Debug complete!")

if __name__ == "__main__":
    debug_cancellation()