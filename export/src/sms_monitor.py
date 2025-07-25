#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMS Monitor - Real-time SMS Activity Monitoring
===============================================
Monitors SMS verifications in real-time.
"""

import time
import logging
from datetime import datetime
from typing import Dict, List

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    class Console:
        def print(self, *args, **kwargs): print(*args)
    console = Console()

class SMSMonitor:
    """Real-time SMS activity monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_verifications = {}
        self.completed_verifications = {}
        self.failed_verifications = {}
        self.monitoring = False
    
    def add_verification(self, customer_id: str, verification_id: str, phone_number: str):
        """Add verification to monitoring queue"""
        self.active_verifications[verification_id] = {
            'customer_id': customer_id,
            'phone_number': phone_number,
            'started_at': datetime.now(),
            'attempts': 0,
            'last_check': None
        }
        
        console.print(f"📱 Added to monitoring: {phone_number}", style="blue")
    
    def start_monitoring(self, database, sms_manager):
        """Start real-time monitoring"""
        self.monitoring = True
        
        try:
            if RICH_AVAILABLE:
                self._start_rich_monitoring(database, sms_manager)
            else:
                self._start_simple_monitoring(database, sms_manager)
        except KeyboardInterrupt:
            console.print("\n🛑 Monitoring stopped by user", style="yellow")
        finally:
            self.monitoring = False
    
    def _start_rich_monitoring(self, database, sms_manager):
        """Start monitoring with Rich interface (no Live panels)"""
        update_count = 0
        
        while self.monitoring and self.active_verifications:
            # Check all active verifications
            self._check_all_verifications(database, sms_manager)
            
            # Show table update every 5 iterations (about 10 seconds)
            update_count += 1
            if update_count % 5 == 0:
                # Create and display monitoring table
                table = self._create_monitoring_table()
                console.print("\n" + "=" * 60)
                console.print(table)
                console.print("💡 Press Ctrl+C to stop monitoring", style="dim")
            
            time.sleep(2)
        
        # Show final summary
        self._show_final_summary()
    
    def _start_simple_monitoring(self, database, sms_manager):
        """Start monitoring with simple text interface"""
        while self.monitoring and self.active_verifications:
            console.print(f"\n🔍 Checking {len(self.active_verifications)} active verifications...")
            
            self._check_all_verifications(database, sms_manager)
            
            # Show status
            for verification_id, data in self.active_verifications.items():
                wait_time = datetime.now() - data['started_at']
                console.print(
                    f"📱 {data['phone_number']} - "
                    f"Attempts: {data['attempts']} - "
                    f"Wait: {wait_time.total_seconds():.0f}s",
                    style="cyan"
                )
            
            time.sleep(5)
    
    def _check_all_verifications(self, database, sms_manager):
        """Check status of all active verifications"""
        completed_ids = []
        
        for verification_id, data in self.active_verifications.items():
            try:
                # Check for SMS code
                code = sms_manager.get_verification_code(verification_id, max_attempts=1)
                data['attempts'] += 1
                data['last_check'] = datetime.now()
                
                if code:
                    # SMS received!
                    self.completed_verifications[verification_id] = {
                        **data,
                        'completed_at': datetime.now(),
                        'code': code,
                        'total_wait_time': (datetime.now() - data['started_at']).total_seconds()
                    }
                    completed_ids.append(verification_id)
                    
                    # Update database
                    database.log_sms_received(
                        data['customer_id'],
                        data['phone_number'],
                        code
                    )
                    
                    console.print(f"✅ SMS received: {data['phone_number']} - {code}", style="green")
                
                # Check for timeout (5 minutes)
                elif (datetime.now() - data['started_at']).total_seconds() > 300:
                    self.failed_verifications[verification_id] = {
                        **data,
                        'failed_at': datetime.now(),
                        'failure_reason': 'timeout',
                        'total_attempts': data['attempts']
                    }
                    completed_ids.append(verification_id)
                    
                    console.print(f"❌ Timeout: {data['phone_number']}", style="red")
            
            except Exception as e:
                self.logger.error(f"Error checking verification {verification_id}: {e}")
        
        # Remove completed verifications
        for verification_id in completed_ids:
            if verification_id in self.active_verifications:
                del self.active_verifications[verification_id]
    
    def _create_monitoring_table(self):
        """Create monitoring status table"""
        table = Table(title="📱 SMS Activity Monitor", box=box.ROUNDED)
        table.add_column("Phone Number", style="green", width=15)
        table.add_column("Status", style="yellow", width=15)
        table.add_column("Wait Time", style="red", width=10)
        table.add_column("Attempts", style="blue", width=8)
        table.add_column("Last Check", style="dim", width=10)
        
        # Add active verifications
        for verification_id, data in self.active_verifications.items():
            wait_time = datetime.now() - data['started_at']
            wait_str = f"{wait_time.total_seconds():.0f}s"
            last_check = data['last_check'].strftime("%H:%M:%S") if data['last_check'] else "Never"
            
            table.add_row(
                data['phone_number'],
                "🔄 Waiting",
                wait_str,
                str(data['attempts']),
                last_check
            )
        
        # Add recently completed (last 3)
        recent_completed = list(self.completed_verifications.items())[-3:]
        for verification_id, data in recent_completed:
            table.add_row(
                data['phone_number'],
                f"✅ {data['code']}",
                f"{data['total_wait_time']:.0f}s",
                str(data['attempts']),
                data['completed_at'].strftime("%H:%M:%S")
            )
        
        return table
    
    def _show_final_summary(self):
        """Show final monitoring summary"""
        total_checked = len(self.completed_verifications) + len(self.failed_verifications)
        successful = len(self.completed_verifications)
        success_rate = (successful / total_checked * 100) if total_checked > 0 else 0
        
        console.print(f"\n📊 Monitoring Summary:", style="bold cyan")
        console.print(f"   Total Checked: {total_checked}", style="white")
        console.print(f"   Successful: {successful}", style="green")
        console.print(f"   Failed: {len(self.failed_verifications)}", style="red")
        console.print(f"   Success Rate: {success_rate:.1f}%", style="cyan")
    
    def wait_for_code(self, verification_id: str, timeout: int = 180) -> str:
        """Wait for SMS code with progress indication"""
        start_time = datetime.now()
        attempts = 0
        
        console.print(f"⏳ Waiting for SMS (timeout: {timeout}s)...", style="yellow")
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                # This would use the sms_manager passed in, but for now return None
                # In actual implementation, would call sms_manager.get_verification_code
                time.sleep(3)
                attempts += 1
                
                # Show progress every 10 attempts
                if attempts % 10 == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    console.print(f"🔄 Still waiting... ({elapsed:.0f}s elapsed)", style="dim")
            
            except Exception as e:
                console.print(f"❌ Error waiting for code: {e}", style="red")
                break
        
        console.print("❌ SMS timeout", style="red")
        return None
    
    def get_monitoring_stats(self) -> Dict:
        """Get current monitoring statistics"""
        return {
            'active_count': len(self.active_verifications),
            'completed_count': len(self.completed_verifications),
            'failed_count': len(self.failed_verifications),
            'monitoring_active': self.monitoring,
            'success_rate': self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate current success rate"""
        total = len(self.completed_verifications) + len(self.failed_verifications)
        if total == 0:
            return 0.0
        return (len(self.completed_verifications) / total) * 100
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        console.print("🛑 Monitoring stopped", style="yellow")
