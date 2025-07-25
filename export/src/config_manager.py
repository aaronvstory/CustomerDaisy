#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager - Application Settings Management
======================================================
Handles configuration loading and management with secure environment variable support.
"""

import configparser
import os
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass

class ConfigManager:
    """Configuration management for CustomerDaisy"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables"""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            self._create_default_config()
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _create_default_config(self):
        """Create default configuration file with placeholders (no sensitive data)"""
        default_config = {
            'DAISYSMS': {
                'api_key': 'PLACEHOLDER_SET_VIA_ENV_VAR',
                'base_url': 'https://daisysms.com/stubs/handler_api.php',
                'service_code': 'ac',
                'max_price': '0.50',
                'verification_timeout': '180',
                'polling_interval': '3'
            },
            'MAILTM': {
                'base_url': 'https://api.mail.tm',
                'default_password': 'PLACEHOLDER_SET_VIA_ENV_VAR',
                'email_digits': '2',
                'domain_cache_duration': '3600'
            },
            'MAPQUEST': {
                'api_key': 'PLACEHOLDER_SET_VIA_ENV_VAR',
                'base_url': 'https://www.mapquestapi.com',
                'default_radius_miles': '10.0',
                'enable_address_validation': 'true',
                'enable_auto_complete': 'true'
            },
            'CUSTOMER_GENERATION': {
                'gender_preference': 'female'
            },
            'DATABASE': {
                'database_path': 'data/customers.db',
                'json_backup_path': 'data/customers_backup.json',
                'data_directory': 'customer_data',
                'backup_directory': 'backups',
                'auto_backup': 'true',
                'backup_interval_hours': '6'
            },
            'LOGGING': {
                'log_directory': 'logs',
                'log_level': 'INFO',
                'max_log_size_mb': '100',
                'log_retention_days': '30',
                'enable_api_logging': 'true',
                'enable_sms_logging': 'true'
            },
            'PERFORMANCE': {
                'batch_size': '5',
                'rate_limit_delay_min': '2',
                'rate_limit_delay_max': '5',
                'batch_delay_min': '30',
                'batch_delay_max': '60',
                'max_concurrent_verifications': '10'
            },
            'UI': {
                'console_width': '120',
                'refresh_rate': '1',
                'theme': 'dark',
                'enable_animations': 'true',
                'show_progress_bars': 'true'
            },
            'NOTIFICATIONS': {
                'enable_notifications': 'false',
                'notification_webhook': '',
                'notification_on_success': 'true',
                'notification_on_failure': 'true'
            }
        }
        
        for section, options in default_config.items():
            self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def _load_env_overrides(self):
        """Load environment variable overrides with comprehensive mapping"""
        env_mappings = {
            # DaisySMS Configuration
            'DAISYSMS_API_KEY': ('DAISYSMS', 'api_key'),
            'DAISYSMS_BASE_URL': ('DAISYSMS', 'base_url'),
            'DAISYSMS_SERVICE_CODE': ('DAISYSMS', 'service_code'),
            'DAISYSMS_MAX_PRICE': ('DAISYSMS', 'max_price'),
            'DAISYSMS_VERIFICATION_TIMEOUT': ('DAISYSMS', 'verification_timeout'),
            'DAISYSMS_POLLING_INTERVAL': ('DAISYSMS', 'polling_interval'),
            
            # Mail.tm Configuration
            'MAILTM_BASE_URL': ('MAILTM', 'base_url'),
            'MAILTM_DEFAULT_PASSWORD': ('MAILTM', 'default_password'),
            'MAILTM_EMAIL_DIGITS': ('MAILTM', 'email_digits'),
            'MAILTM_DOMAIN_CACHE_DURATION': ('MAILTM', 'domain_cache_duration'),
            
            # MapQuest Configuration
            'MAPQUEST_API_KEY': ('MAPQUEST', 'api_key'),
            'MAPQUEST_BASE_URL': ('MAPQUEST', 'base_url'),
            'MAPQUEST_DEFAULT_RADIUS_MILES': ('MAPQUEST', 'default_radius_miles'),
            'MAPQUEST_ENABLE_ADDRESS_VALIDATION': ('MAPQUEST', 'enable_address_validation'),
            'MAPQUEST_ENABLE_AUTO_COMPLETE': ('MAPQUEST', 'enable_auto_complete'),
            
            # Customer Generation
            'CUSTOMER_GENDER_PREFERENCE': ('CUSTOMER_GENERATION', 'gender_preference'),
            
            # Database Configuration
            'DATABASE_DATA_DIRECTORY': ('DATABASE', 'data_directory'),
            'DATABASE_BACKUP_DIRECTORY': ('DATABASE', 'backup_directory'),
            'DATABASE_AUTO_BACKUP': ('DATABASE', 'auto_backup'),
            'DATABASE_BACKUP_INTERVAL_HOURS': ('DATABASE', 'backup_interval_hours'),
            
            # Logging Configuration
            'LOG_DIRECTORY': ('LOGGING', 'log_directory'),
            'LOG_LEVEL': ('LOGGING', 'log_level'),
            'LOG_MAX_SIZE_MB': ('LOGGING', 'max_log_size_mb'),
            'LOG_RETENTION_DAYS': ('LOGGING', 'log_retention_days'),
            'LOG_ENABLE_API_LOGGING': ('LOGGING', 'enable_api_logging'),
            'LOG_ENABLE_SMS_LOGGING': ('LOGGING', 'enable_sms_logging'),
            
            # Performance Settings
            'PERFORMANCE_BATCH_SIZE': ('PERFORMANCE', 'batch_size'),
            'PERFORMANCE_RATE_LIMIT_DELAY_MIN': ('PERFORMANCE', 'rate_limit_delay_min'),
            'PERFORMANCE_RATE_LIMIT_DELAY_MAX': ('PERFORMANCE', 'rate_limit_delay_max'),
            'PERFORMANCE_BATCH_DELAY_MIN': ('PERFORMANCE', 'batch_delay_min'),
            'PERFORMANCE_BATCH_DELAY_MAX': ('PERFORMANCE', 'batch_delay_max'),
            'PERFORMANCE_MAX_CONCURRENT_VERIFICATIONS': ('PERFORMANCE', 'max_concurrent_verifications'),
            
            # UI Configuration
            'UI_CONSOLE_WIDTH': ('UI', 'console_width'),
            'UI_REFRESH_RATE': ('UI', 'refresh_rate'),
            'UI_THEME': ('UI', 'theme'),
            'UI_ENABLE_ANIMATIONS': ('UI', 'enable_animations'),
            'UI_SHOW_PROGRESS_BARS': ('UI', 'show_progress_bars'),
            
            # Notification Settings
            'NOTIFICATIONS_ENABLE': ('NOTIFICATIONS', 'enable_notifications'),
            'NOTIFICATIONS_WEBHOOK': ('NOTIFICATIONS', 'notification_webhook'),
            'NOTIFICATIONS_ON_SUCCESS': ('NOTIFICATIONS', 'notification_on_success'),
            'NOTIFICATIONS_ON_FAILURE': ('NOTIFICATIONS', 'notification_on_failure'),
        }
        
        for env_var, (section, option) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:  # Allow empty strings but not None
                # Ensure section exists
                if not self.config.has_section(section):
                    self.config.add_section(section)
                self.config.set(section, option, value)
    
    def get_config(self) -> configparser.ConfigParser:
        """Get the configuration object"""
        return self.config
    
    def get_section(self, section: str) -> Dict[str, str]:
        """Get a configuration section as dictionary"""
        if self.config.has_section(section):
            return dict(self.config.items(section))
        return {}
    
    def update_config(self, section: str, option: str, value: str):
        """Update a configuration value and save to file"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, option, value)
        
        # Save to file immediately to ensure persistence
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            print(f"📝 Configuration saved: [{section}] {option} = {value}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def get_value(self, section: str, option: str, fallback: str = '') -> str:
        """Get a specific configuration value"""
        return self.config.get(section, option, fallback=fallback)
