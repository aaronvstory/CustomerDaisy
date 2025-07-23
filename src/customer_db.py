#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CustomerDaisy - Customer Database Management with MapQuest Integration
=====================================================================
Manages customer data storage, retrieval, and analytics with real address validation.
"""

import json
import uuid
import hashlib
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import random
from dataclasses import dataclass, field

# Rich imports for interactive features
try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    class Console:
        def print(self, *args, **kwargs): 
            print(*args)

console = Console() if RICH_AVAILABLE else Console()

# Faker for generating realistic customer data
try:
    from faker import Faker
    fake = Faker('en_US')
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    fake = None


@dataclass
class CustomerRecord:
    """Represents a customer record with all associated data"""
    customer_id: str
    full_name: str
    first_name: str
    last_name: str
    email: str
    password: str
    full_address: str
    address_line1: str
    city: str
    state: str
    zip_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address_source: str = 'unknown'
    address_validated: bool = False
    primary_phone: Optional[str] = None
    primary_verification_id: Optional[str] = None
    verification_completed: bool = False
    verification_code: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    phone_numbers: List[Dict] = field(default_factory=list)
    sms_history: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class CustomerDatabase:
    """
    Advanced customer database with MapQuest integration for real addresses
    """
    
    def __init__(self, db_config: Dict, mapquest_config: Dict = None, mapquest_manager=None):
        self.db_path = Path(db_config.get('database_path', 'data/customers.db'))
        self.json_backup_path = Path(db_config.get('json_backup_path', 'data/customers_backup.json'))
        self.mapquest_config = mapquest_config or {}
        self.config = db_config  # Store full config for access to settings
        
        # Use provided MapQuest manager or create new one
        self.mapquest_manager = mapquest_manager
        if self.mapquest_manager is None and self.mapquest_config.get('api_key'):
            try:
                from .mapquest_address import MapQuestAddressManager
                self.mapquest_manager = MapQuestAddressManager(self.mapquest_config)
            except ImportError:
                console.print("⚠️ MapQuest integration not available", style="yellow")
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._setup_database()
        
        # Load existing data
        self.customers = self._load_customers()
        
        console.print(f"💾 Database initialized: {len(self.customers)} customers loaded", style="green")
    
    def _configure_faker_gender(self, gender_preference: str):
        """Configure faker gender preference"""
        if hasattr(self, 'config'):
            self.config['gender_preference'] = gender_preference
    
    def _setup_database(self):
        """Setup SQLite database with proper schema and performance indexes"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT UNIQUE,
                    password TEXT,
                    full_address TEXT,
                    address_line1 TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    latitude REAL,
                    longitude REAL,
                    address_source TEXT,
                    address_validated BOOLEAN,
                    primary_phone TEXT,
                    primary_verification_id TEXT,
                    verification_completed BOOLEAN,
                    verification_code TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT
                )
            ''')
            
            # Phone numbers table for multiple numbers per customer
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS phone_numbers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT,
                    phone_number TEXT,
                    verification_id TEXT,
                    is_primary BOOLEAN,
                    status TEXT,
                    created_at TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            ''')
            
            # SMS history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sms_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT,
                    phone_number TEXT,
                    sms_code TEXT,
                    received_at TEXT,
                    service_used TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            ''')
            
            # Performance indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(primary_phone)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(full_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_phone_numbers_customer ON phone_numbers(customer_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sms_history_customer ON sms_history(customer_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_verification ON customers(primary_verification_id)')
            
            conn.commit()
    
    def _load_customers(self) -> Dict[str, CustomerRecord]:
        """Load customers from database with fallback to JSON"""
        customers = {}
        
        try:
            # Try loading from SQLite first
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM customers')
                rows = cursor.fetchall()
                
                for row in rows:
                    customer_data = dict(row)
                    
                    # Parse metadata JSON
                    if customer_data.get('metadata'):
                        try:
                            customer_data['metadata'] = json.loads(customer_data['metadata'])
                        except json.JSONDecodeError:
                            customer_data['metadata'] = {}
                    else:
                        customer_data['metadata'] = {}
                    
                    # Load phone numbers
                    cursor.execute(
                        'SELECT * FROM phone_numbers WHERE customer_id = ?',
                        (customer_data['customer_id'],)
                    )
                    phone_rows = cursor.fetchall()
                    customer_data['phone_numbers'] = [dict(row) for row in phone_rows]
                    
                    # Load SMS history
                    cursor.execute(
                        'SELECT * FROM sms_history WHERE customer_id = ?',
                        (customer_data['customer_id'],)
                    )
                    sms_rows = cursor.fetchall()
                    customer_data['sms_history'] = [dict(row) for row in sms_rows]
                    
                    customers[customer_data['customer_id']] = CustomerRecord(**customer_data)
        
        except Exception as e:
            self.logger.warning(f"Failed to load from SQLite: {e}")
            
            # Fallback to JSON backup
            if self.json_backup_path.exists():
                try:
                    with open(self.json_backup_path, 'r') as f:
                        json_data = json.load(f)
                        for customer_id, customer_data in json_data.items():
                            customers[customer_id] = CustomerRecord(**customer_data)
                    console.print(f"📄 Loaded {len(customers)} customers from JSON backup", style="yellow")
                except Exception as json_error:
                    self.logger.error(f"Failed to load JSON backup: {json_error}")
        
        return customers
    
    def _save_customers(self):
        """Save customers to both SQLite and JSON backup"""
        try:
            # Save to SQLite
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for customer_id, customer in self.customers.items():
                    # Prepare customer data
                    customer_data = {
                        'customer_id': customer.customer_id,
                        'full_name': customer.full_name,
                        'first_name': customer.first_name,
                        'last_name': customer.last_name,
                        'email': customer.email,
                        'password': customer.password,
                        'full_address': customer.full_address,
                        'address_line1': customer.address_line1,
                        'city': customer.city,
                        'state': customer.state,
                        'zip_code': customer.zip_code,
                        'latitude': customer.latitude,
                        'longitude': customer.longitude,
                        'address_source': customer.address_source,
                        'address_validated': customer.address_validated,
                        'primary_phone': customer.primary_phone,
                        'primary_verification_id': customer.primary_verification_id,
                        'verification_completed': customer.verification_completed,
                        'verification_code': customer.verification_code,
                        'created_at': customer.created_at,
                        'updated_at': datetime.now(timezone.utc).isoformat(),
                        'metadata': json.dumps(customer.metadata)
                    }
                    
                    # Insert or update customer
                    cursor.execute('''
                        INSERT OR REPLACE INTO customers 
                        (customer_id, full_name, first_name, last_name, email, password,
                         full_address, address_line1, city, state, zip_code, latitude, longitude,
                         address_source, address_validated, primary_phone, primary_verification_id,
                         verification_completed, verification_code, created_at, updated_at, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', tuple(customer_data.values()))
                    
                    # Clear and insert phone numbers
                    cursor.execute('DELETE FROM phone_numbers WHERE customer_id = ?', (customer_id,))
                    for phone in customer.phone_numbers:
                        cursor.execute('''
                            INSERT INTO phone_numbers 
                            (customer_id, phone_number, verification_id, is_primary, status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            customer_id,
                            phone.get('phone_number'),
                            phone.get('verification_id'),
                            phone.get('is_primary', False),
                            phone.get('status', 'active'),
                            phone.get('created_at', datetime.now(timezone.utc).isoformat())
                        ))
                    
                    # Clear and insert SMS history
                    cursor.execute('DELETE FROM sms_history WHERE customer_id = ?', (customer_id,))
                    for sms in customer.sms_history:
                        cursor.execute('''
                            INSERT INTO sms_history 
                            (customer_id, phone_number, sms_code, received_at, service_used)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            customer_id,
                            sms.get('phone_number'),
                            sms.get('sms_code'),
                            sms.get('received_at'),
                            sms.get('service_used', 'daisysms')
                        ))
                
                conn.commit()
            
            # Save JSON backup
            self.json_backup_path.parent.mkdir(parents=True, exist_ok=True)
            json_data = {}
            for customer_id, customer in self.customers.items():
                json_data[customer_id] = {
                    'customer_id': customer.customer_id,
                    'full_name': customer.full_name,
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'email': customer.email,
                    'password': customer.password,
                    'full_address': customer.full_address,
                    'address_line1': customer.address_line1,
                    'city': customer.city,
                    'state': customer.state,
                    'zip_code': customer.zip_code,
                    'latitude': customer.latitude,
                    'longitude': customer.longitude,
                    'address_source': customer.address_source,
                    'address_validated': customer.address_validated,
                    'primary_phone': customer.primary_phone,
                    'primary_verification_id': customer.primary_verification_id,
                    'verification_completed': customer.verification_completed,
                    'verification_code': customer.verification_code,
                    'created_at': customer.created_at,
                    'updated_at': customer.updated_at,
                    'phone_numbers': customer.phone_numbers,
                    'sms_history': customer.sms_history,
                    'metadata': customer.metadata
                }
            
            with open(self.json_backup_path, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
        
        except Exception as e:
            self.logger.error(f"Failed to save customers: {e}")
            raise
    
    def generate_customer_data(self, custom_address: str = None, origin_address: str = None) -> Dict:
        """
        Generate realistic customer data with MapQuest real addresses
        """
        if not FAKER_AVAILABLE:
            raise RuntimeError("Faker library not available for generating customer data")
        
        # Get gender preference from config
        gender_preference = 'both'
        if hasattr(self, 'config') and self.config:
            gender_preference = self.config.get('gender_preference', 'both')
        
        # Generate basic customer info based on gender preference
        if gender_preference == 'male':
            first_name = fake.first_name_male()
            last_name = fake.last_name()
        elif gender_preference == 'female':
            first_name = fake.first_name_female()
            last_name = fake.last_name()
        else:  # both
            first_name = fake.first_name()
            last_name = fake.last_name()
        
        full_name = f"{first_name} {last_name}"
        
        # Generate secure password
        password = self._generate_secure_password()
        
        # Generate email address based on name
        email_name = f"{first_name.lower()}{last_name.lower()}{fake.random_int(min=100, max=9999)}"
        email = f"{email_name}@{fake.free_email_domain()}"
        
        customer_data = {
            'customer_id': str(uuid.uuid4()),
            'full_name': full_name,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password,
            'phone_numbers': [],
            'sms_history': [],
            'metadata': {
                'generation_method': 'faker',
                'gender_preference': gender_preference,
                'generation_timestamp': datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Get address data (real or fallback)
        address_data = self._get_address_data(custom_address, origin_address)
        customer_data.update(address_data)
        
        return customer_data
    
    def _get_address_data(self, custom_address: str = None, origin_address: str = None) -> Dict:
        """Get address data from MapQuest or fallback to fake data"""
        address_data = {}
        
        # Try MapQuest first if available
        if self.mapquest_manager:
            try:
                if custom_address:
                    # Validate specific address
                    console.print(f"🔍 Validating address: {custom_address}", style="blue")
                    result = self.mapquest_manager.validate_address(custom_address)
                    if result:
                        address_data = {
                            'full_address': result['full_address'],
                            'address_line1': result['address_line1'],
                            'city': result['city'],
                            'state': result['state'],
                            'zip_code': result['zip_code'],
                            'latitude': result.get('latitude'),
                            'longitude': result.get('longitude'),
                            'address_source': 'mapquest_validated',
                            'address_validated': True
                        }
                        console.print("✅ Address validated with MapQuest", style="green")
                    else:
                        console.print("❌ Address validation failed", style="red")
                
                elif origin_address:
                    # Random address near origin
                    console.print(f"🎲 Finding address near: {origin_address}", style="blue")
                    result = self.mapquest_manager.get_random_address_near_location(origin_address)
                    if result:
                        address_data = {
                            'full_address': result['full_address'],
                            'address_line1': result['address_line1'],
                            'city': result['city'],
                            'state': result['state'],
                            'zip_code': result['zip_code'],
                            'latitude': result.get('latitude'),
                            'longitude': result.get('longitude'),
                            'address_source': 'mapquest_near_location',
                            'address_validated': True
                        }
                        console.print("✅ Real address found near location", style="green")
                
                else:
                    # Random US address
                    console.print("🎲 Getting random real address", style="blue")
                    result = self.mapquest_manager.get_random_us_address()
                    if result:
                        address_data = {
                            'full_address': result['full_address'],
                            'address_line1': result['address_line1'],
                            'city': result['city'],
                            'state': result['state'],
                            'zip_code': result['zip_code'],
                            'latitude': result.get('latitude'),
                            'longitude': result.get('longitude'),
                            'address_source': 'mapquest_random',
                            'address_validated': True
                        }
                        console.print("✅ Real random address generated", style="green")
            
            except Exception as e:
                console.print(f"⚠️ MapQuest error: {e}", style="yellow")
                self.logger.warning(f"MapQuest address generation failed: {e}")
        
        # Fallback to fake address if MapQuest fails
        if not address_data:
            console.print("🎭 Using fake address as fallback", style="yellow")
            address_data = {
                'full_address': fake.address().replace('\n', ', '),
                'address_line1': fake.street_address(),
                'city': fake.city(),
                'state': fake.state_abbr(),
                'zip_code': fake.zipcode(),
                'latitude': float(fake.latitude()),
                'longitude': float(fake.longitude()),
                'address_source': 'faker_fallback',
                'address_validated': False
            }
        
        return address_data
    
    def interactive_address_selection(self) -> Dict:
        """Interactive address selection with auto-complete suggestions"""
        if not self.mapquest_manager:
            console.print("❌ MapQuest not available for interactive selection", style="red")
            return self._get_address_data()
        
        console.print("\n🏠 Interactive Address Selection", style="bold blue")
        console.print("Type partial addresses to see suggestions", style="dim")
        
        while True:
            query = Prompt.ask("Enter city, state, or partial address")
            
            if not query.strip():
                console.print("❌ Please enter a search term", style="red")
                continue
            
            console.print(f"🔍 Searching for: {query}", style="yellow")
            
            try:
                suggestions = self.mapquest_manager.search_addresses(query, max_results=10)
                
                if not suggestions:
                    console.print("❌ No suggestions found", style="red")
                    if not Confirm.ask("Try a different search?"):
                        break
                    continue
                
                # Display suggestions table
                suggestions_table = Table(title="Address Suggestions")
                suggestions_table.add_column("Index", style="cyan")
                suggestions_table.add_column("Address", style="white")
                suggestions_table.add_column("City", style="green")
                suggestions_table.add_column("State", style="blue")
                
                for i, suggestion in enumerate(suggestions):
                    suggestions_table.add_row(
                        str(i + 1),
                        suggestion['address_line1'],
                        suggestion['city'],
                        suggestion['state']
                    )
                
                console.print(suggestions_table)
                
                # Get user selection
                try:
                    choice = IntPrompt.ask(
                        "Select address (0 to search again)",
                        choices=[str(i) for i in range(len(suggestions) + 1)]
                    )
                    
                    if choice == 0:
                        continue
                    
                    selected_address = suggestions[choice - 1]
                    
                    # Validate the selected address
                    console.print("✅ Validating selected address...", style="blue")
                    validated = self.mapquest_manager.validate_address(selected_address['full_address'])
                    if validated:
                        return {
                            'full_address': validated['full_address'],
                            'address_line1': validated['address_line1'],
                            'city': validated['city'],
                            'state': validated['state'],
                            'zip_code': validated['zip_code'],
                            'latitude': validated.get('latitude'),
                            'longitude': validated.get('longitude'),
                            'address_source': 'mapquest_suggestion_validated',
                            'address_validated': True
                        }
                
                except (ValueError, IndexError):
                    console.print("❌ Invalid selection", style="red")
                
                if not Confirm.ask("Try entering address again?"):
                    break
                    
            except Exception as e:
                console.print(f"❌ Search error: {e}", style="red")
                if not Confirm.ask("Try again?"):
                    break
        
        # Fallback to random address if user gives up
        console.print("🎲 Using random address instead", style="cyan")
        return self._get_address_data()
    
    def _generate_secure_password(self) -> str:
        """Generate a secure password"""
        if FAKER_AVAILABLE:
            return fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
        else:
            # Fallback password generation
            import string
            import secrets
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(alphabet) for _ in range(12))
    
    def save_customer(self, customer_data: Dict) -> str:
        """Save customer to database"""
        try:
            # Fix field mapping - mail manager returns email_password, but CustomerRecord expects password
            if 'email_password' in customer_data and 'password' not in customer_data:
                customer_data['password'] = customer_data.pop('email_password')
            
            # Generate customer ID if not provided
            if 'customer_id' not in customer_data:
                customer_data['customer_id'] = str(uuid.uuid4())
            
            # Filter out any unexpected fields that aren't in CustomerRecord
            valid_fields = {
                'customer_id', 'full_name', 'first_name', 'last_name', 'email', 'password',
                'full_address', 'address_line1', 'city', 'state', 'zip_code', 'latitude', 'longitude',
                'address_source', 'address_validated', 'primary_phone', 'primary_verification_id',
                'verification_completed', 'verification_code', 'created_at', 'updated_at',
                'phone_numbers', 'sms_history', 'metadata'
            }
            
            filtered_data = {k: v for k, v in customer_data.items() if k in valid_fields}
            
            customer_record = CustomerRecord(**filtered_data)
            self.customers[customer_record.customer_id] = customer_record
            self._save_customers()
            
            self.logger.debug(f"Customer saved: {customer_record.customer_id}")
            return customer_record.customer_id
        
        except Exception as e:
            self.logger.error(f"Failed to save customer: {e}")
            raise
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict]:
        """Get customer data by ID"""
        if customer_id not in self.customers:
            return None
        
        customer = self.customers[customer_id]
        return {
            'customer_id': customer.customer_id,
            'full_name': customer.full_name,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email,
            'password': customer.password,
            'full_address': customer.full_address,
            'address_line1': customer.address_line1,
            'city': customer.city,
            'state': customer.state,
            'zip_code': customer.zip_code,
            'latitude': customer.latitude,
            'longitude': customer.longitude,
            'address_source': customer.address_source,
            'address_validated': customer.address_validated,
            'primary_phone': customer.primary_phone,
            'primary_verification_id': customer.primary_verification_id,
            'verification_completed': customer.verification_completed,
            'verification_code': customer.verification_code,
            'created_at': customer.created_at,
            'updated_at': customer.updated_at,
            'phone_numbers': customer.phone_numbers,
            'sms_history': customer.sms_history,
            'metadata': customer.metadata
        }

    def search_customers(self, search_term: str) -> List[Dict]:
        """Search customers by name, email, or phone"""
        results = []
        search_term = search_term.lower()
        
        for customer in self.customers.values():
            if (search_term in customer.full_name.lower() or
                search_term in customer.email.lower() or
                (customer.primary_phone and search_term in customer.primary_phone)):
                
                results.append({
                    'customer_id': customer.customer_id,
                    'full_name': customer.full_name,
                    'email': customer.email,
                    'password': customer.password,
                    'primary_phone': customer.primary_phone,
                    'city': customer.city,
                    'state': customer.state,
                    'primary_verification_id': customer.primary_verification_id,
                    'verification_completed': customer.verification_completed
                })
        
        return results
    
    def get_recent_customers(self, limit: int = 10) -> List[Dict]:
        """Get most recently created/updated customers"""
        # Sort customers by updated_at (most recent first), then by created_at
        sorted_customers = sorted(
            self.customers.values(),
            key=lambda c: c.updated_at if c.updated_at else c.created_at,
            reverse=True
        )
        
        results = []
        for customer in sorted_customers[:limit]:
            results.append({
                'customer_id': customer.customer_id,
                'full_name': customer.full_name,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'password': customer.password,
                'primary_phone': customer.primary_phone or 'No phone',
                'city': customer.city,
                'state': customer.state,
                'verification_completed': customer.verification_completed,
                'created_at': customer.created_at,
                'updated_at': customer.updated_at,
                'primary_verification_id': customer.primary_verification_id
            })
        
        return results
    
    def get_recent_addresses(self, limit: int = 10) -> List[Dict]:
        """Get most recently used addresses for quick selection"""
        # Get unique addresses from recent customers
        recent_customers = sorted(
            self.customers.values(),
            key=lambda c: c.updated_at if c.updated_at else c.created_at,
            reverse=True
        )
        
        seen_addresses = set()
        recent_addresses = []
        
        for customer in recent_customers:
            # Create a normalized address key for uniqueness
            address_key = f"{customer.city.lower()}, {customer.state.lower()}" if customer.city and customer.state else customer.full_address.lower()
            
            if address_key not in seen_addresses and customer.full_address:
                seen_addresses.add(address_key)
                recent_addresses.append({
                    'full_address': customer.full_address,
                    'city': customer.city,
                    'state': customer.state,
                    'zip_code': customer.zip_code,
                    'address_source': customer.address_source,
                    'latitude': customer.latitude,
                    'longitude': customer.longitude,
                    'last_used': customer.updated_at if customer.updated_at else customer.created_at
                })
                
                if len(recent_addresses) >= limit:
                    break
        
        return recent_addresses
    
    def load_all_customers(self) -> List[Dict]:
        """Load all customers for display"""
        return [
            {
                'customer_id': customer.customer_id,
                'full_name': customer.full_name,
                'email': customer.email,
                'password': customer.password,
                'primary_phone': customer.primary_phone,
                'city': customer.city,
                'state': customer.state,
                'address_source': customer.address_source,
                'verification_completed': customer.verification_completed,
                'created_at': customer.created_at
            }
            for customer in self.customers.values()
        ]
    
    def update_customer_verification(self, customer_id: str, completed: bool, code: str = None):
        """Update customer verification status"""
        if customer_id in self.customers:
            self.customers[customer_id].verification_completed = completed
            if code:
                self.customers[customer_id].verification_code = code
            self.customers[customer_id].updated_at = datetime.now(timezone.utc).isoformat()
            self._save_customers()
    
    def assign_new_number(self, customer_id: str, phone_data: Dict) -> bool:
        """Assign new phone number to customer"""
        try:
            if customer_id not in self.customers:
                return False
            
            customer = self.customers[customer_id]
            
            # Add new phone number
            new_phone = {
                'phone_number': phone_data['phone_number'],
                'verification_id': phone_data['verification_id'],
                'is_primary': True,
                'status': 'active',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Mark old numbers as non-primary
            for phone in customer.phone_numbers:
                phone['is_primary'] = False
            
            customer.phone_numbers.append(new_phone)
            customer.primary_phone = phone_data['phone_number']
            customer.primary_verification_id = phone_data['verification_id']
            customer.updated_at = datetime.now(timezone.utc).isoformat()
            
            self._save_customers()
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to assign new number: {e}")
            return False
    
    def log_sms_received(self, customer_id: str, phone_number: str, sms_code: str):
        """Log SMS code received"""
        if customer_id in self.customers:
            sms_entry = {
                'phone_number': phone_number,
                'sms_code': sms_code,
                'received_at': datetime.now(timezone.utc).isoformat(),
                'service_used': 'daisysms'
            }
            
            self.customers[customer_id].sms_history.append(sms_entry)
            self._save_customers()
    
    def generate_analytics(self) -> Dict:
        """Generate comprehensive analytics including address data"""
        total_customers = len(self.customers)
        
        if total_customers == 0:
            return {
                'summary': {},
                'address_analytics': {},
                'sms_performance': {}
            }
        
        # Basic metrics
        verified_count = sum(1 for c in self.customers.values() if c.verification_completed)
        mapquest_count = sum(1 for c in self.customers.values() if 'mapquest' in c.address_source)
        
        # Address analytics
        address_sources = {}
        states = {}
        cities = {}
        validated_addresses = 0
        
        for customer in self.customers.values():
            # Address sources
            source = customer.address_source
            address_sources[source] = address_sources.get(source, 0) + 1
            
            # Geographic distribution
            if customer.state:
                states[customer.state] = states.get(customer.state, 0) + 1
            if customer.city:
                cities[customer.city] = cities.get(customer.city, 0) + 1
            
            # Validation count
            if customer.address_validated:
                validated_addresses += 1
        
        # SMS performance
        total_sms = sum(len(c.sms_history) for c in self.customers.values())
        customers_with_sms = sum(1 for c in self.customers.values() if c.sms_history)
        
        return {
            'summary': {
                'total_customers': total_customers,
                'verified_customers': verified_count,
                'verification_rate': round((verified_count / total_customers) * 100, 2),
                'mapquest_addresses': mapquest_count,
                'real_address_rate': round((mapquest_count / total_customers) * 100, 2),
                'total_sms_received': total_sms
            },
            'address_analytics': {
                'address_sources': address_sources,
                'validation_rate': round((validated_addresses / total_customers) * 100, 2),
                'geographic_distribution': {
                    'unique_states': len(states),
                    'unique_cities': len(cities),
                    'top_states': sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]
                },
                'mapquest_usage': {
                    'mapquest_enabled': self.mapquest_manager is not None,
                    'real_addresses': mapquest_count,
                    'fallback_addresses': total_customers - mapquest_count
                }
            },
            'sms_performance': {
                'total_sms': total_sms,
                'customers_with_sms': customers_with_sms,
                'avg_sms_per_customer': round(total_sms / total_customers, 2) if total_customers > 0 else 0
            }
        }
    
    def export_customers(self, format_type: str = 'json') -> str:
        """Export customer data in specified format"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Prepare export data
        export_data = []
        for customer in self.customers.values():
            export_record = {
                'customer_id': customer.customer_id,
                'full_name': customer.full_name,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'full_address': customer.full_address,
                'address_line1': customer.address_line1,
                'city': customer.city,
                'state': customer.state,
                'zip_code': customer.zip_code,
                'latitude': customer.latitude,
                'longitude': customer.longitude,
                'address_source': customer.address_source,
                'address_validated': customer.address_validated,
                'primary_phone': customer.primary_phone,
                'verification_completed': customer.verification_completed,
                'created_at': customer.created_at,
                'phone_count': len(customer.phone_numbers),
                'sms_count': len(customer.sms_history)
            }
            export_data.append(export_record)
        
        # Export based on format
        export_dir = Path('exports')
        export_dir.mkdir(exist_ok=True)
        
        if format_type == 'json':
            filename = export_dir / f'customers_export_{timestamp}.json'
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        
        elif format_type == 'csv':
            import csv
            filename = export_dir / f'customers_export_{timestamp}.csv'
            
            if export_data:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=export_data[0].keys())
                    writer.writeheader()
                    writer.writerows(export_data)
        
        elif format_type == 'txt':
            filename = export_dir / f'customers_export_{timestamp}.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                for record in export_data:
                    f.write("=" * 50 + "\n")
                    for key, value in record.items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
        
        return str(filename)