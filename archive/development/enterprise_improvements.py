#!/usr/bin/env python3
"""
Enterprise-Grade Improvements for CustomerDaisy
===============================================
Implements enterprise-level features for production deployment.
"""

import logging
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import os

class AuditLogger:
    """Enterprise audit logging for compliance and monitoring"""
    
    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup audit logger
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # Create audit log handler
        audit_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(audit_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_action(self, action: str, user: str = "system", details: Dict = None):
        """Log user action for audit trail"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user': user,
            'details': details or {},
            'session_id': getattr(self, 'current_session_id', 'unknown')
        }
        self.logger.info(json.dumps(audit_entry))
    
    def log_api_call(self, service: str, method: str, response_code: int, duration: float):
        """Log API calls for monitoring"""
        self.log_action('api_call', details={
            'service': service,
            'method': method,
            'response_code': response_code,
            'duration_ms': round(duration * 1000, 2)
        })
    
    def log_database_operation(self, operation: str, table: str, records_affected: int):
        """Log database operations"""
        self.log_action('database_operation', details={
            'operation': operation,
            'table': table,
            'records_affected': records_affected
        })

class SecurityManager:
    """Enterprise security features"""
    
    def __init__(self):
        self.failed_attempts = {}
        self.rate_limits = {}
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutes
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def check_rate_limit(self, identifier: str, max_requests: int = 100, 
                        time_window: int = 3600) -> bool:
        """Check if request is within rate limits"""
        now = time.time()
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # Clean old requests
        self.rate_limits[identifier] = [
            req_time for req_time in self.rate_limits[identifier]
            if now - req_time < time_window
        ]
        
        # Check if under limit
        if len(self.rate_limits[identifier]) < max_requests:
            self.rate_limits[identifier].append(now)
            return True
        
        return False
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not isinstance(input_data, str):
            return str(input_data)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`']
        sanitized = input_data
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()

class HealthMonitor:
    """Application health monitoring"""
    
    def __init__(self):
        self.metrics = {
            'start_time': datetime.now(),
            'requests_processed': 0,
            'errors_encountered': 0,
            'api_calls_made': 0,
            'database_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self.health_checks = []
    
    def increment_metric(self, metric_name: str, value: int = 1):
        """Increment a metric counter"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    def get_health_status(self) -> Dict:
        """Get comprehensive health status"""
        uptime = datetime.now() - self.metrics['start_time']
        
        # Calculate error rate
        total_requests = self.metrics['requests_processed']
        error_rate = (self.metrics['errors_encountered'] / total_requests * 100 
                     if total_requests > 0 else 0)
        
        # Calculate cache hit rate
        total_cache_ops = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (self.metrics['cache_hits'] / total_cache_ops * 100 
                         if total_cache_ops > 0 else 0)
        
        return {
            'status': 'healthy' if error_rate < 5 else 'degraded',
            'uptime_seconds': uptime.total_seconds(),
            'uptime_human': str(uptime),
            'error_rate_percent': round(error_rate, 2),
            'cache_hit_rate_percent': round(cache_hit_rate, 2),
            'metrics': self.metrics.copy(),
            'health_checks': self.health_checks
        }
    
    def add_health_check(self, name: str, status: str, message: str = ""):
        """Add a health check result"""
        self.health_checks.append({
            'name': name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 health checks
        self.health_checks = self.health_checks[-10:]

class ConfigurationValidator:
    """Validate configuration for enterprise deployment"""
    
    def __init__(self):
        self.validation_rules = {
            'DAISYSMS': {
                'required': ['api_key', 'base_url'],
                'security': ['api_key should not be default'],
                'performance': ['polling_interval should be >= 3']
            },
            'DATABASE': {
                'required': ['database_path', 'json_backup_path'],
                'security': ['database should be in secure directory'],
                'performance': ['backup_interval should be reasonable']
            },
            'MAPQUEST': {
                'required': ['api_key'],
                'security': ['api_key should not be default'],
                'performance': ['cache_duration should be reasonable']
            }
        }
    
    def validate_config(self, config: Dict) -> Dict[str, List[str]]:
        """Validate configuration against enterprise standards"""
        issues = {
            'critical': [],
            'warnings': [],
            'recommendations': []
        }
        
        for section_name, rules in self.validation_rules.items():
            section = config.get(section_name, {})
            
            # Check required fields
            for field in rules.get('required', []):
                if field not in section or not section[field]:
                    issues['critical'].append(f"{section_name}.{field} is required")
            
            # Security checks
            if 'api_key' in section:
                if section['api_key'] in ['your_api_key_here', 'default', '']:
                    issues['warnings'].append(f"{section_name}.api_key is not configured")
            
            # Performance checks
            if section_name == 'DAISYSMS' and 'polling_interval' in section:
                if int(section.get('polling_interval', 0)) < 3:
                    issues['recommendations'].append(
                        f"{section_name}.polling_interval should be >= 3 for better performance"
                    )
        
        return issues

class BackupManager:
    """Automated backup management"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, source_files: List[str], backup_name: str = None) -> str:
        """Create timestamped backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = backup_name or f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        import shutil
        backed_up_files = []
        
        for source_file in source_files:
            source_path = Path(source_file)
            if source_path.exists():
                dest_path = backup_path / source_path.name
                if source_path.is_file():
                    shutil.copy2(source_path, dest_path)
                else:
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                backed_up_files.append(str(dest_path))
        
        # Create backup manifest
        manifest = {
            'created_at': datetime.now().isoformat(),
            'source_files': source_files,
            'backed_up_files': backed_up_files,
            'backup_path': str(backup_path)
        }
        
        with open(backup_path / 'manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return str(backup_path)
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Remove backups older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                # Check backup creation time
                manifest_file = backup_dir / 'manifest.json'
                if manifest_file.exists():
                    try:
                        with open(manifest_file) as f:
                            manifest = json.load(f)
                        
                        created_at = datetime.fromisoformat(manifest['created_at'])
                        if created_at < cutoff_date:
                            import shutil
                            shutil.rmtree(backup_dir)
                            print(f"Removed old backup: {backup_dir}")
                    
                    except Exception as e:
                        print(f"Error processing backup {backup_dir}: {e}")

def apply_enterprise_improvements(app_instance):
    """Apply enterprise improvements to application instance"""
    
    # Initialize enterprise components
    audit_logger = AuditLogger()
    security_manager = SecurityManager()
    health_monitor = HealthMonitor()
    config_validator = ConfigurationValidator()
    backup_manager = BackupManager()
    
    # Validate configuration
    config_issues = config_validator.validate_config(app_instance.config)
    
    # Create initial backup
    backup_files = [
        'data/customers.db',
        'config.ini',
        'logs/'
    ]
    backup_path = backup_manager.create_backup(backup_files)
    
    # Add enterprise components to app instance
    app_instance.audit_logger = audit_logger
    app_instance.security_manager = security_manager
    app_instance.health_monitor = health_monitor
    app_instance.backup_manager = backup_manager
    
    # Log enterprise initialization
    audit_logger.log_action('enterprise_initialization', details={
        'backup_created': backup_path,
        'config_issues': config_issues
    })
    
    print("✅ Enterprise improvements applied successfully!")
    print(f"📋 Configuration issues: {sum(len(v) for v in config_issues.values())}")
    print(f"💾 Backup created: {backup_path}")
    
    return {
        'config_issues': config_issues,
        'backup_path': backup_path,
        'components_initialized': True
    }

if __name__ == "__main__":
    print("🏢 Enterprise Improvements Module")
    print("=" * 50)
    
    # Demo the enterprise features
    audit_logger = AuditLogger()
    audit_logger.log_action('system_startup')
    
    security_manager = SecurityManager()
    test_input = "<script>alert('test')</script>"
    sanitized = security_manager.sanitize_input(test_input)
    print(f"Input sanitization: '{test_input}' -> '{sanitized}'")
    
    health_monitor = HealthMonitor()
    health_monitor.increment_metric('requests_processed', 10)
    health_monitor.increment_metric('errors_encountered', 1)
    health_status = health_monitor.get_health_status()
    print(f"Health status: {health_status['status']}")
    
    print("✅ Enterprise features demo complete!")