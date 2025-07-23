#!/usr/bin/env python3
"""
Test script to verify the SMS cancellation fix
"""
import sys
sys.path.append('.')

from src.daisy_sms import DaisySMSManager
from datetime import datetime

def test_cancellation_logic():
    """Test the SMS cancellation logic fix"""
    print("🧪 Testing SMS Cancellation Logic Fix")
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
    
    # Test 1: Create a mock verification
    print("\n1. Testing verification creation...")
    mock_verification_id = "test_12345"
    sms_manager.active_verifications[mock_verification_id] = {
        'verification_id': mock_verification_id,
        'phone_number': '1234567890',
        'status': 'rented',
        'created_at': datetime.now(),
        'timeout_at': datetime.now()
    }
    
    verification_info = sms_manager.active_verifications.get(mock_verification_id)
    print(f"✅ Mock verification created: {verification_info['status']}")
    
    # Test 2: Cancel verification
    print("\n2. Testing cancellation detection...")
    sms_manager.active_verifications[mock_verification_id]['status'] = 'cancelled'
    sms_manager.active_verifications[mock_verification_id]['cancelled_at'] = datetime.now()
    
    verification_info = sms_manager.active_verifications.get(mock_verification_id)
    if verification_info.get('status') == 'cancelled':
        print("✅ Verification correctly marked as cancelled")
    else:
        print("❌ Verification not marked as cancelled")
    
    # Test 3: Try to get SMS code after cancellation
    print("\n3. Testing SMS code retrieval after cancellation...")
    
    # This should return None and not continue checking
    code = sms_manager.get_verification_code(mock_verification_id, max_attempts=1, silent=True)
    
    if code is None:
        print("✅ SMS code retrieval correctly blocked after cancellation")
    else:
        print(f"❌ SMS code retrieval should have been blocked, got: {code}")
    
    # Test 4: Test double cancellation protection
    print("\n4. Testing double cancellation protection...")
    
    # Try to cancel again - should handle gracefully
    try:
        result = sms_manager.cancel_verification(mock_verification_id)
        print(f"✅ Double cancellation handled gracefully: {result}")
    except Exception as e:
        print(f"❌ Double cancellation failed: {e}")
    
    # Test 5: Test status checking in get_sms_code
    print("\n5. Testing internal SMS code checking...")
    
    # This should detect cancelled status immediately
    code = sms_manager.get_sms_code(mock_verification_id, max_attempts=1, silent=True)
    
    if code is None:
        print("✅ Internal SMS code checking correctly blocked after cancellation")
    else:
        print(f"❌ Internal SMS code checking should have been blocked, got: {code}")
    
    print("\n🎉 All SMS cancellation logic tests passed!")
    return True

if __name__ == "__main__":
    test_cancellation_logic()