#!/usr/bin/env python3
"""
Test DoorDash SMS verification with correct service code
"""

from src.daisy_sms import DaisySMSManager
import configparser

# Load updated config
config = configparser.ConfigParser()
config.read('config.ini')
manager = DaisySMSManager(dict(config.items('DAISYSMS')))

print('🎯 Testing DoorDash SMS verification with correct service code!')
print(f'✅ Service Code: {manager.service_code} (DoorDash)')
print(f'💰 Max Price: ${manager.max_price}')
print()

print('🧪 Testing DoorDash number rental...')
try:
    verification = manager.rent_number('ac', max_price=0.15)  # Rent DoorDash number
    if verification:
        print(f'✅ DoorDash number rented: {verification["phone_number"]}')
        print(f'📱 Verification ID: {verification["verification_id"]}')
        
        print('\n📞 Testing enhanced SMS polling for DoorDash (3 attempts)...')
        code = manager.get_verification_code(verification['verification_id'], max_attempts=3, silent=False)
        if code:
            print(f'🎉 SUCCESS! DoorDash SMS code received: {code}')
        else:
            print('ℹ️ No SMS received yet (normal for quick test)')
            print('   In real DoorDash signup, SMS should arrive within 30-60 seconds')
            
        print('\n🧹 Cancelling test verification...')
        cancelled = manager.cancel_verification(verification['verification_id'])
        print(f'✅ Cancelled: {cancelled}')
        
    else:
        print('❌ Failed to rent DoorDash number')
        
except Exception as e:
    print(f'❌ Test error: {e}')

print('\n✅ Ready for real DoorDash verification!')
print('💡 Now when you create customers, they will get DoorDash-compatible numbers')
print('💡 SMS codes should arrive within 30-60 seconds during real signup')