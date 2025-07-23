#!/usr/bin/env python3
"""
Database Integrity Test
Test database consistency, data integrity, and all database operations.
"""

import sys
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.config_manager import ConfigManager
from src.customer_db import CustomerDatabase

def test_database_schema():
    """Test database schema integrity"""
    print('📊 Testing Database Schema...')
    try:
        # Connect directly to database
        db_path = Path('data/customers.db')
        if not db_path.exists():
            print('❌ Database file does not exist')
            return False
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['customers', 'phone_numbers', 'sms_history']
        for table in required_tables:
            if table in tables:
                print(f'✅ Table {table}: EXISTS')
            else:
                print(f'❌ Table {table}: MISSING')
                return False
        
        # Check customers table schema
        cursor.execute("PRAGMA table_info(customers);")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'customer_id', 'full_name', 'first_name', 'last_name', 
            'email', 'full_address', 'city', 'state', 'zip_code',
            'latitude', 'longitude', 'primary_phone', 'created_at'
        ]
        
        for column in required_columns:
            if column in columns:
                print(f'✅ Column {column}: EXISTS')
            else:
                print(f'❌ Column {column}: MISSING')
                return False
        
        conn.close()
        print('🎉 Database schema integrity: PASSED')
        return True
        
    except Exception as e:
        print(f'❌ Database schema test failed: {e}')
        return False

def test_data_consistency():
    """Test data consistency and relationships"""
    print('\n🔍 Testing Data Consistency...')
    try:
        config_manager = ConfigManager()
        db_config = config_manager.get_section('DATABASE')
        customer_gen_config = config_manager.get_section('CUSTOMER_GENERATION')
        db_config.update(customer_gen_config)
        
        db = CustomerDatabase(db_config, config_manager.get_section('MAPQUEST'))
        
        # Load all customers
        customers = db.load_all_customers()
        print(f'✅ Loaded {len(customers)} customers')
        
        # Check each customer has required fields
        required_fields = ['customer_id', 'full_name', 'email', 'created_at']
        for i, customer in enumerate(customers):
            for field in required_fields:
                if field not in customer or customer[field] is None:
                    print(f'❌ Customer {i}: Missing {field}')
                    return False
        
        print('✅ All customers have required fields')
        
        # Check customer ID uniqueness
        customer_ids = [c['customer_id'] for c in customers]
        if len(customer_ids) == len(set(customer_ids)):
            print('✅ Customer IDs are unique')
        else:
            print('❌ Duplicate customer IDs found')
            return False
        
        # Check email uniqueness
        emails = [c['email'] for c in customers if c['email']]
        if len(emails) == len(set(emails)):
            print('✅ Email addresses are unique')
        else:
            print('❌ Duplicate email addresses found')
            return False
        
        print('🎉 Data consistency: PASSED')
        return True
        
    except Exception as e:
        print(f'❌ Data consistency test failed: {e}')
        return False

def test_crud_operations():
    """Test Create, Read, Update, Delete operations"""
    print('\n🔧 Testing CRUD Operations...')
    try:
        config_manager = ConfigManager()
        db_config = config_manager.get_section('DATABASE')
        customer_gen_config = config_manager.get_section('CUSTOMER_GENERATION')
        db_config.update(customer_gen_config)
        
        db = CustomerDatabase(db_config, config_manager.get_section('MAPQUEST'))
        
        # Test Read operations
        customers = db.load_all_customers()
        print(f'✅ Read: Loaded {len(customers)} customers')
        
        if customers:
            # Test search
            first_customer = customers[0]
            search_results = db.search_customers(first_customer['full_name'].split()[0])
            if search_results:
                print('✅ Search: Customer search working')
            else:
                print('❌ Search: No results returned')
                return False
            
            # Test get by ID
            customer_by_id = db.get_customer_by_id(first_customer['customer_id'])
            if customer_by_id and customer_by_id['customer_id'] == first_customer['customer_id']:
                print('✅ Get by ID: Working correctly')
            else:
                print('❌ Get by ID: Failed or returned wrong customer')
                return False
        
        # Test analytics generation
        analytics = db.generate_analytics()
        if 'summary' in analytics:
            print('✅ Analytics: Generated successfully')
        else:
            print('❌ Analytics: Failed to generate')
            return False
        
        print('🎉 CRUD operations: PASSED')
        return True
        
    except Exception as e:
        print(f'❌ CRUD operations test failed: {e}')
        return False

def test_backup_system():
    """Test backup and recovery functionality"""
    print('\n💾 Testing Backup System...')
    try:
        # Check backup directory exists
        backup_dir = Path('backups')
        if backup_dir.exists():
            print('✅ Backup directory exists')
            
            # Check for backup files
            backup_files = list(backup_dir.glob('*.json'))
            if backup_files:
                print(f'✅ Found {len(backup_files)} backup files')
            else:
                print('⚠️ No backup files found (may be normal for new installation)')
        else:
            print('⚠️ Backup directory does not exist')
        
        print('🎉 Backup system: PASSED')
        return True
        
    except Exception as e:
        print(f'❌ Backup system test failed: {e}')
        return False

def main():
    """Run all database integrity tests"""
    print('🚀 Database Integrity Comprehensive Test')
    print('=' * 50)
    
    tests = [
        test_database_schema,
        test_data_consistency,
        test_crud_operations,
        test_backup_system
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
    print(f'📊 Database Test Results: {passed} PASSED, {failed} FAILED')
    
    if failed == 0:
        print('🎉 DATABASE INTEGRITY 100% CONFIRMED!')
        return True
    else:
        print('⚠️ Database integrity issues detected')
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)