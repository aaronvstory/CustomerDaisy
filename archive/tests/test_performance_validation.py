#!/usr/bin/env python3
"""
Performance Validation Test
Test application startup time, memory usage, and operation performance.
"""

import sys
import time
import psutil
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_startup_performance():
    """Test application startup time"""
    print('⚡ Testing Application Startup Performance...')
    try:
        # Test module import times
        start_time = time.time()
        
        from src.config_manager import ConfigManager
        config_import_time = time.time() - start_time
        
        from src.customer_db import CustomerDatabase
        db_import_time = time.time() - start_time - config_import_time
        
        from src.daisy_sms import DaisySMSManager
        sms_import_time = time.time() - start_time - config_import_time - db_import_time
        
        from src.mail_tm import MailTmManager
        mail_import_time = time.time() - start_time - config_import_time - db_import_time - sms_import_time
        
        from src.mapquest_address import MapQuestAddressManager
        mapquest_import_time = time.time() - start_time - config_import_time - db_import_time - sms_import_time - mail_import_time
        
        total_import_time = time.time() - start_time
        
        print(f'✅ Module imports: {total_import_time:.3f}s')
        print(f'   - Config: {config_import_time:.3f}s')
        print(f'   - Database: {db_import_time:.3f}s')
        print(f'   - SMS: {sms_import_time:.3f}s')
        print(f'   - Mail: {mail_import_time:.3f}s')
        print(f'   - MapQuest: {mapquest_import_time:.3f}s')
        
        # Test component initialization
        init_start = time.time()
        
        config_manager = ConfigManager()
        config_init_time = time.time() - init_start
        
        db_config = config_manager.get_section('DATABASE')
        customer_gen_config = config_manager.get_section('CUSTOMER_GENERATION')
        db_config.update(customer_gen_config)
        
        db = CustomerDatabase(db_config, config_manager.get_section('MAPQUEST'))
        db_init_time = time.time() - init_start - config_init_time
        
        sms_manager = DaisySMSManager(config_manager.get_section('DAISYSMS'))
        sms_init_time = time.time() - init_start - config_init_time - db_init_time
        
        total_init_time = time.time() - init_start
        
        print(f'✅ Component initialization: {total_init_time:.3f}s')
        print(f'   - Config: {config_init_time:.3f}s')
        print(f'   - Database: {db_init_time:.3f}s')
        print(f'   - SMS Manager: {sms_init_time:.3f}s')
        
        total_startup = total_import_time + total_init_time
        print(f'📊 Total startup time: {total_startup:.3f}s')
        
        # Performance thresholds
        if total_startup < 2.0:
            print('🟢 Startup performance: EXCELLENT')
        elif total_startup < 5.0:
            print('🟡 Startup performance: GOOD')
        else:
            print('🔴 Startup performance: NEEDS IMPROVEMENT')
        
        return True
        
    except Exception as e:
        print(f'❌ Startup performance test failed: {e}')
        return False

def test_memory_usage():
    """Test memory usage during operations"""
    print('\n💾 Testing Memory Usage...')
    try:
        process = psutil.Process(os.getpid())
        
        # Initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f'📊 Initial memory: {initial_memory:.1f} MB')
        
        # Import modules and measure memory
        from src.config_manager import ConfigManager
        from src.customer_db import CustomerDatabase
        from src.daisy_sms import DaisySMSManager
        
        import_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f'📊 After imports: {import_memory:.1f} MB (+{import_memory - initial_memory:.1f} MB)')
        
        # Initialize components
        config_manager = ConfigManager()
        db_config = config_manager.get_section('DATABASE')
        customer_gen_config = config_manager.get_section('CUSTOMER_GENERATION')
        db_config.update(customer_gen_config)
        
        db = CustomerDatabase(db_config, config_manager.get_section('MAPQUEST'))
        
        init_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f'📊 After initialization: {init_memory:.1f} MB (+{init_memory - import_memory:.1f} MB)')
        
        # Load data
        customers = db.load_all_customers()
        
        load_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f'📊 After loading {len(customers)} customers: {load_memory:.1f} MB (+{load_memory - init_memory:.1f} MB)')
        
        total_memory_increase = load_memory - initial_memory
        print(f'📊 Total memory increase: {total_memory_increase:.1f} MB')
        
        # Memory efficiency assessment
        if total_memory_increase < 50:
            print('🟢 Memory usage: EXCELLENT')
        elif total_memory_increase < 100:
            print('🟡 Memory usage: GOOD')
        else:
            print('🔴 Memory usage: NEEDS OPTIMIZATION')
        
        return True
        
    except Exception as e:
        print(f'❌ Memory usage test failed: {e}')
        return False

def test_operation_performance():
    """Test performance of key operations"""
    print('\n🔍 Testing Operation Performance...')
    try:
        from src.config_manager import ConfigManager
        from src.customer_db import CustomerDatabase
        
        config_manager = ConfigManager()
        db_config = config_manager.get_section('DATABASE')
        customer_gen_config = config_manager.get_section('CUSTOMER_GENERATION')
        db_config.update(customer_gen_config)
        
        db = CustomerDatabase(db_config, config_manager.get_section('MAPQUEST'))
        
        # Test database load performance
        start_time = time.time()
        customers = db.load_all_customers()
        load_time = time.time() - start_time
        print(f'✅ Load {len(customers)} customers: {load_time:.3f}s')
        
        if customers:
            # Test search performance
            start_time = time.time()
            search_results = db.search_customers(customers[0]['full_name'].split()[0])
            search_time = time.time() - start_time
            print(f'✅ Customer search: {search_time:.3f}s ({len(search_results)} results)')
            
            # Test get by ID performance
            start_time = time.time()
            customer = db.get_customer_by_id(customers[0]['customer_id'])
            get_time = time.time() - start_time
            print(f'✅ Get customer by ID: {get_time:.3f}s')
        
        # Test analytics performance
        start_time = time.time()
        analytics = db.generate_analytics()
        analytics_time = time.time() - start_time
        print(f'✅ Generate analytics: {analytics_time:.3f}s')
        
        # Performance assessment
        total_op_time = load_time + search_time + get_time + analytics_time
        if total_op_time < 1.0:
            print('🟢 Operation performance: EXCELLENT')
        elif total_op_time < 3.0:
            print('🟡 Operation performance: GOOD')
        else:
            print('🔴 Operation performance: NEEDS OPTIMIZATION')
        
        return True
        
    except Exception as e:
        print(f'❌ Operation performance test failed: {e}')
        return False

def test_api_response_times():
    """Test API response times"""
    print('\n🌐 Testing API Response Times...')
    try:
        from src.config_manager import ConfigManager
        from src.daisy_sms import DaisySMSManager
        from src.mapquest_address import MapQuestAddressManager
        
        config_manager = ConfigManager()
        
        # Test DaisySMS API
        start_time = time.time()
        sms_manager = DaisySMSManager(config_manager.get_section('DAISYSMS'))
        balance = sms_manager.get_balance()
        sms_time = time.time() - start_time
        print(f'✅ DaisySMS balance check: {sms_time:.3f}s')
        
        # Test MapQuest API
        start_time = time.time()
        mapquest_manager = MapQuestAddressManager(config_manager.get_section('MAPQUEST'))
        test_result = mapquest_manager.test_api_connection()
        mapquest_time = time.time() - start_time
        print(f'✅ MapQuest API test: {mapquest_time:.3f}s')
        
        total_api_time = sms_time + mapquest_time
        print(f'📊 Total API response time: {total_api_time:.3f}s')
        
        # API performance assessment
        if total_api_time < 2.0:
            print('🟢 API performance: EXCELLENT')
        elif total_api_time < 5.0:
            print('🟡 API performance: GOOD')
        else:
            print('🔴 API performance: SLOW (may be network related)')
        
        return True
        
    except Exception as e:
        print(f'❌ API response time test failed: {e}')
        return False

def main():
    """Run all performance validation tests"""
    print('🚀 Performance Validation Comprehensive Test')
    print('=' * 50)
    
    tests = [
        test_startup_performance,
        test_memory_usage,
        test_operation_performance,
        test_api_response_times
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
    print(f'📊 Performance Test Results: {passed} PASSED, {failed} FAILED')
    
    if failed == 0:
        print('🎉 PERFORMANCE VALIDATION 100% PASSED!')
        return True
    else:
        print('⚠️ Performance issues detected')
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)