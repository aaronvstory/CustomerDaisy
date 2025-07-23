#!/usr/bin/env python3
"""
Test script to understand DaisySMS response formats
"""
import sys
sys.path.append('.')

from src.daisy_sms import DaisySMSManager

def test_response_formats():
    """Test various DaisySMS response formats"""
    print("🧪 Testing DaisySMS Response Formats")
    print("=" * 60)
    
    # Create DaisySMS manager
    config = {
        'api_key': 'test_key',
        'base_url': 'https://daisysms.com/stubs/handler_api.php',
        'service_code': 'ds',
        'max_price': '0.50',
        'verification_timeout': '180',
        'polling_interval': '3'
    }
    
    sms_manager = DaisySMSManager(config)
    
    # Test different response formats
    test_responses = [
        # Standard formats from documentation
        "STATUS_OK:123456",
        "STATUS_WAIT_CODE",
        "STATUS_CANCEL", 
        "NO_ACTIVATION",
        
        # Alternative formats that might be used
        "OK:123456",
        "READY:789012",
        "ACCESS_ACTIVATION:345678",
        "123456",  # Just the code
        
        # Error formats
        "ERROR:Invalid ID",
        "TIMEOUT",
        "EXPIRED",
        
        # Multi-part formats
        "STATUS_OK:123456:extra_info",
        "OK:789012:timestamp",
    ]
    
    print("\n🔍 Testing Response Parsing:")
    print("-" * 60)
    
    for i, raw_response in enumerate(test_responses, 1):
        print(f"\n{i:2d}. Testing: '{raw_response}'")
        
        # Simulate the parsing logic
        if ':' in raw_response:
            parts = raw_response.split(':', 1)
            status = parts[0]
            data = parts[1] if len(parts) > 1 else None
            
            # Apply SMS code detection logic
            if status in ['STATUS_OK', 'OK'] and data and data.split(':')[0].isdigit():
                actual_code = data.split(':')[0]
                print(f"    ✅ SMS Code Detected: {actual_code}")
            elif status == 'STATUS_WAIT_CODE':
                print(f"    ⏳ Waiting for SMS")
            elif status == 'STATUS_CANCEL':
                print(f"    ❌ Cancelled")
            elif status == 'NO_ACTIVATION':
                print(f"    ❌ No activation")
            else:
                print(f"    ❓ Unknown status: {status} | Data: {data}")
        else:
            # Single value response
            if raw_response.isdigit() and len(raw_response) >= 4:
                print(f"    ✅ Direct SMS Code: {raw_response}")
            else:
                print(f"    ❓ Unknown format: {raw_response}")
    
    print("\n" + "=" * 60)
    print("🎯 Key Insights:")
    print("- SMS codes can come in multiple formats")
    print("- Need to handle both 'STATUS_OK:code' and 'OK:code'")
    print("- Need to handle direct numeric codes")
    print("- Need to handle multi-part responses with extra data")
    print("- Current parsing should handle most cases")
    
    return True

if __name__ == "__main__":
    test_response_formats()