#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CustomerDaisy - Main Application Entry Point with MapQuest Integration
======================================================================
Author: Claude (AI Development Partner)
Version: 1.0.0
Complete customer creation system with DaisySMS integration and REAL addresses.
"""

import sys
import configparser
import logging
import time
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# UTF-8 safety for terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Rich imports with graceful fallback
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.prompt import Confirm, Prompt, IntPrompt
    from rich.markup import escape
    from rich import box
    from rich.align import Align
    from rich.text import Text
    from rich.columns import Columns
    from datetime import datetime, timezone
    import time
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback classes when Rich is not available
    class Console:
        def __init__(self, *args, **kwargs):
            pass
        def print(self, *args, **kwargs): 
            print(*args)
    def escape(text): 
        return str(text)

# Questionary for enhanced interactive menus
try:
    import questionary
    from questionary import Choice
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False

# Clipboard functionality with graceful fallback
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    class pyperclip:
        @staticmethod
        def copy(text):
            pass

__version__ = "1.0.0"
# Initialize console with proper fallback
if RICH_AVAILABLE:
    try:
        console = Console(force_terminal=True, width=120)
    except TypeError:
        # Fallback for older Rich versions
        console = Console(width=120)
else:
    console = Console()

# Import our modules
from src.daisy_sms import DaisySMSManager
from src.mail_tm import MailTmManager  
from src.customer_db import CustomerDatabase
from src.config_manager import ConfigManager
from src.sms_monitor import SMSMonitor
from src.mapquest_address import MapQuestAddressManager


def enhanced_confirm(message: str, default: bool = False) -> bool:
    """Enhanced confirmation dialog with questionary fallback to Rich Prompt"""
    if QUESTIONARY_AVAILABLE:
        try:
            return questionary.confirm(message, default=default).ask()
        except (KeyboardInterrupt, Exception) as e:
            if isinstance(e, KeyboardInterrupt):
                return False
            # Fallback to Rich
    
    # Rich Prompt fallback
    choice = Prompt.ask(message, choices=["yes", "no"], default="yes" if default else "no")
    return choice.lower() == "yes"


def enhanced_text_input(message: str, default: str = "", password: bool = False) -> str:
    """Enhanced text input with questionary fallback to Rich Prompt"""
    if QUESTIONARY_AVAILABLE and not password:
        try:
            return questionary.text(message, default=default).ask() or default
        except (KeyboardInterrupt, Exception):
            pass
    
    # Rich Prompt fallback
    if password:
        return Prompt.ask(message, password=True, default=default)
    else:
        return Prompt.ask(message, default=default)


def enhanced_select(message: str, choices: list, default: str = None) -> str:
    """Enhanced selection with questionary fallback to Rich Prompt"""
    if QUESTIONARY_AVAILABLE:
        try:
            # Convert simple choices to Choice objects
            if isinstance(choices[0], str):
                questionary_choices = [Choice(choice, value=choice) for choice in choices]
            else:
                questionary_choices = choices
                
            return questionary.select(
                message, 
                choices=questionary_choices,
                default=default
            ).ask()
        except (KeyboardInterrupt, Exception) as e:
            if isinstance(e, KeyboardInterrupt):
                return default or choices[0]
            # Fallback to Rich
    
    # Rich Prompt fallback
    return Prompt.ask(message, choices=choices, default=default)


class CustomerDaisyApp:
    """Main CustomerDaisy application with MapQuest real addresses"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        
        # Initialize components
        self.sms_manager = DaisySMSManager(self.config_manager.get_section('DAISYSMS'))
        self.mail_manager = MailTmManager(self.config_manager.get_section('MAILTM'))
        self.mapquest_manager = MapQuestAddressManager(self.config_manager.get_section('MAPQUEST'))
        
        # Combine database and customer generation config
        db_config = self.config_manager.get_section('DATABASE')
        customer_gen_config = self.config_manager.get_section('CUSTOMER_GENERATION')
        db_config.update(customer_gen_config)
        
        self.database = CustomerDatabase(
            db_config, 
            self.config_manager.get_section('MAPQUEST'),
            self.mapquest_manager
        )
        self.sms_monitor = SMSMonitor()
        
        # Setup logging
        self._setup_logging()
        
        console.print(f"🌸 CustomerDaisy v{__version__} ready", style="green")
    
    def _setup_logging(self):
        """Setup application logging"""
        log_config = self.config_manager.get_section('LOGGING')
        log_level = getattr(logging, log_config.get('log_level', 'INFO'))
        
        # Configure file and console logging separately
        file_handler = logging.FileHandler('logs/customer_daisy.log')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # Console handler only shows warnings and errors to reduce clutter
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        
        logging.basicConfig(
            level=log_level,
            handlers=[file_handler, console_handler]
        )
        self.logger = logging.getLogger(__name__)
    
    def _safe_copy(self, text: str) -> str:
        """Safe cross-platform clipboard copy with fallbacks"""
        try:
            import subprocess
            import platform
            
            if CLIPBOARD_AVAILABLE:
                # Clear clipboard first
                pyperclip.copy('')
                time.sleep(0.1)  # Small delay for Windows clipboard
                
                # Copy the actual text
                pyperclip.copy(text)
                time.sleep(0.1)  # Another small delay
                
                # Test that copy actually worked with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    test_paste = pyperclip.paste()
                    if test_paste == text:
                        return "📋 Copied to clipboard!"
                    elif attempt < max_retries - 1:
                        time.sleep(0.2)  # Wait longer before retry
                        pyperclip.copy(text)  # Retry copy
                
                # If verification failed, try Windows clip as fallback
                system = platform.system()
                if system == "Windows":
                    try:
                        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, text=True)
                        process.communicate(input=text)
                        if process.returncode == 0:
                            return "📋 Copied to clipboard (Windows clip)!"
                    except Exception:
                        pass
                
                return "📋 Copy failed - paste test mismatch"
            else:
                # Platform-specific fallback
                system = platform.system()
                try:
                    if system == "Darwin":  # macOS
                        subprocess.run(["pbcopy"], input=text, text=True, check=True)
                        return "📋 Copied to clipboard (pbcopy)!"
                    elif system == "Windows":
                        subprocess.run(["clip"], input=text, text=True, check=True)
                        return "📋 Copied to clipboard (clip)!"
                    elif system == "Linux":
                        subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
                        return "📋 Copied to clipboard (xclip)!"
                    else:
                        return "📋 Clipboard unavailable on this platform"
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return "📋 Platform clipboard helper not found"
                    
        except Exception as e:
            return f"📋 Copy error: {str(e)[:20]}..."
    
    def _format_phone_for_user(self, phone_number: str) -> Tuple[str, str]:
        """Format phone number for user display (remove country prefix) and copy to clipboard"""
        if not phone_number:
            return "N/A", ""
        
        # Remove country code prefix (1 for US numbers)
        formatted_phone = phone_number
        if phone_number.startswith('1') and len(phone_number) == 11:
            formatted_phone = phone_number[1:]  # Remove the '1' prefix
        
        # Use safe clipboard copy
        clipboard_status = self._safe_copy(formatted_phone)
        
        return formatted_phone, clipboard_status
    
    def _copy_to_clipboard_manual(self, text: str, description: str = "text"):
        """Manual clipboard copy with user feedback and Windows-specific fixes"""
        if CLIPBOARD_AVAILABLE:
            try:
                # Clear clipboard first
                pyperclip.copy('')
                time.sleep(0.1)  # Small delay for Windows clipboard
                
                # Copy the actual text
                pyperclip.copy(text)
                time.sleep(0.1)  # Another small delay
                
                # Verify copy worked with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    test_paste = pyperclip.paste()
                    if test_paste == text:
                        console.print(f"✅ {description} copied to clipboard: {text}", style="green")
                        return True
                    elif attempt < max_retries - 1:
                        time.sleep(0.2)  # Wait longer before retry
                        pyperclip.copy(text)  # Retry copy
                    
                console.print(f"❌ Clipboard copy verification failed for {description} after {max_retries} attempts", style="red")
                console.print(f"Expected: {text}", style="dim")
                console.print(f"Got: {test_paste}", style="dim")
                
            except Exception as e:
                console.print(f"❌ Clipboard error for {description}: {str(e)}", style="red")
                # Try Windows-specific fallback
                try:
                    import subprocess
                    import platform
                    if platform.system() == "Windows":
                        # Use Windows clip command as fallback
                        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, text=True)
                        process.communicate(input=text)
                        if process.returncode == 0:
                            console.print(f"✅ {description} copied to clipboard using Windows clip: {text}", style="green")
                            return True
                except Exception as fallback_e:
                    console.print(f"❌ Windows clip fallback also failed: {fallback_e}", style="red")
        else:
            console.print(f"❌ Clipboard not available - manual copy: {text}", style="yellow")
        
        return False
    
    def _show_sms_verification_options(self, customer_data):
        """Show SMS verification options with enhanced questionary interface"""
        console.print()
        console.print("─" * 80, style="cyan")
        console.print("📱 SMS Verification Options", style="bold cyan")
        console.print("─" * 80, style="cyan")
        console.print()
        
        # Display phone number for reference in a clean panel
        formatted_phone, _ = self._format_phone_for_user(customer_data.get('phone_number', ''))
        phone_panel = Panel.fit(
            f"📞 Phone Number: {formatted_phone}",
            title="📱 Current Number",
            border_style="blue",
            padding=(0, 2)
        )
        console.print(phone_panel)
        console.print()
        
        # Use questionary for modern interface
        if QUESTIONARY_AVAILABLE:
            try:
                import sys
                if sys.stdin.isatty() and sys.stdout.isatty():
                    choices = [
                        Choice("📱 Check for SMS Code", value="1"),
                        Choice("🔄 Assign New Phone Number", value="2"),
                        Choice("📋 Copy Phone Number to Clipboard", value="3"),
                        Choice("⏳ Skip Verification (check later)", value="4"),
                        Choice("🔙 Cancel & Return to Main Menu", value="5")
                    ]
                    
                    choice = questionary.select(
                        "What would you like to do?",
                        choices=choices,
                        use_shortcuts=True
                    ).ask()
                    
                    if choice:
                        # Continue with the choice processing
                        pass
                    else:
                        choice = "5"  # Default to cancel if no selection
                else:
                    raise RuntimeError("Non-interactive terminal")
                    
            except (KeyboardInterrupt, Exception) as e:
                if isinstance(e, KeyboardInterrupt):
                    choice = "5"
                else:
                    # Fall back to Rich interface
                    choice = enhanced_select(
                        "What would you like to do?",
                        ["📱 Check for SMS Code", "🔄 Assign New Number", "📋 Copy Phone", "⏳ Skip Verification", "🔙 Cancel"],
                        default="📱 Check for SMS Code"
                    )
                    # Convert choice to number
                    choice_map = {
                        "📱 Check for SMS Code": "1",
                        "🔄 Assign New Number": "2", 
                        "📋 Copy Phone": "3",
                        "⏳ Skip Verification": "4",
                        "🔙 Cancel": "5"
                    }
                    choice = choice_map.get(choice, "1")
        else:
            # Rich fallback
            choice = enhanced_select(
                "What would you like to do?",
                ["📱 Check for SMS Code", "🔄 Assign New Number", "📋 Copy Phone", "⏳ Skip Verification", "🔙 Cancel"],
                default="📱 Check for SMS Code"
            )
            choice_map = {
                "📱 Check for SMS Code": "1",
                "🔄 Assign New Number": "2", 
                "📋 Copy Phone": "3",
                "⏳ Skip Verification": "4",
                "🔙 Cancel": "5"
            }
            choice = choice_map.get(choice, "1")
        
        if choice == "1":
            self._check_sms_manually(customer_data)
        elif choice == "2":
            self._assign_new_number(customer_data['customer_id'])
            # After assigning new number, automatically start live monitoring
            updated = self.database.get_customer_by_id(customer_data['customer_id'])
            if updated:
                self._start_live_sms_monitoring(updated)
        elif choice == "3":
            # Manual clipboard copy
            phone_number = customer_data.get('phone_number', '')
            formatted_phone, _ = self._format_phone_for_user(phone_number)
            self._copy_to_clipboard_manual(formatted_phone, "phone number")
            # Return to options menu
            self._show_sms_verification_options(customer_data)
        elif choice == "4":
            console.print("⏳ SMS verification deferred - you can check later via option 2", style="yellow")
        elif choice == "5":
            console.print("🔙 Returning to main menu", style="blue")
            return
    
    def _check_sms_manually(self, customer_data):
        """Check for SMS codes manually - single check per user request"""
        verification_id = customer_data.get('verification_id') or customer_data.get('primary_verification_id')
        phone_number = customer_data.get('phone_number') or customer_data.get('primary_phone')
        formatted_phone, _ = self._format_phone_for_user(phone_number)
        
        console.print()
        console.print("━" * 80, style="cyan")
        console.print("📱 Checking for SMS Codes", style="bold cyan")
        console.print("━" * 80, style="cyan")
        console.print()
        
        # Display phone number info in a clean panel
        phone_panel = Panel.fit(
            f"📞 Phone Number: {formatted_phone}\n"
            f"🆔 Verification ID: {verification_id}",
            title="📱 SMS Check Details",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(phone_panel)
        console.print()
        
        # Check if verification is still active
        verification_info = self.sms_manager.active_verifications.get(verification_id)
        if verification_info and verification_info.get('status') == 'cancelled':
            error_panel = Panel.fit(
                "❌ Verification was cancelled/refunded\n"
                "💡 You'll need to assign a new phone number",
                title="⚠️ Verification Status",
                border_style="red",
                padding=(1, 2)
            )
            console.print(error_panel)
            console.print()
            self._show_sms_verification_options(customer_data)
            return
        
        # Get the customer's SMS history from database
        customer_record = self.database.get_customer_by_id(customer_data['customer_id'])
        previous_codes = []
        sms_history = []
        if customer_record and customer_record.get('sms_history'):
            sms_history = customer_record['sms_history']
            previous_codes = [sms['sms_code'] for sms in sms_history]
        
        # Check for new SMS code
        console.print("🔍 Checking DaisySMS API...", style="yellow")
        self.logger.info(f"Checking for SMS code for verification ID: {verification_id}")
        code = self.sms_manager.get_verification_code(verification_id, max_attempts=1, silent=True)
        
        if code:
            if code not in previous_codes:
                # New code received!
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.logger.info(f"New SMS code received: {code} for customer {customer_data['customer_id']}")
                
                # Log the SMS
                self.database.log_sms_received(
                    customer_data['customer_id'],
                    phone_number,
                    code
                )
                
                # Update verification status
                self.database.update_customer_verification(
                    customer_data['customer_id'], True, code
                )
                self.logger.info(f"Customer {customer_data['customer_id']} verification status updated to completed")
                
                # Show new code
                new_code_panel = Panel.fit(
                    f"🎉 NEW SMS CODE RECEIVED!\n\n"
                    f"📱 Code: [bold green]{code}[/bold green]\n"
                    f"🕐 Received at: {timestamp}",
                    title="✅ New SMS Code",
                    border_style="green",
                    padding=(1, 2)
                )
                console.print(new_code_panel)
                
                # Copy to clipboard
                self._copy_to_clipboard_manual(code, "SMS code")
                
                # Show previous codes if any
                if sms_history:
                    previous_entries = []
                    for entry in sms_history:
                        # Parse the timestamp to show only time (HH:MM:SS)
                        try:
                            from datetime import datetime
                            received_dt = datetime.fromisoformat(entry['received_at'].replace('Z', '+00:00'))
                            time_str = received_dt.strftime("%H:%M:%S")
                        except:
                            time_str = "Unknown"
                        
                        previous_entries.append(f"📱 {entry['sms_code']} - {time_str}")
                    
                    previous_text = "\n".join(previous_entries)
                    history_panel = Panel.fit(
                        f"Previous codes:\n{previous_text}",
                        title="📜 SMS History",
                        border_style="dim",
                        padding=(1, 2)
                    )
                    console.print(history_panel)
                
            else:
                # Same code as before
                self.logger.info(f"Same SMS code received again: {code} for customer {customer_data['customer_id']}")
                
                # Find when this code was last received
                last_received_time = "Unknown"
                for entry in reversed(sms_history):  # Check most recent first
                    if entry['sms_code'] == code:
                        try:
                            from datetime import datetime
                            received_dt = datetime.fromisoformat(entry['received_at'].replace('Z', '+00:00'))
                            last_received_time = received_dt.strftime("%H:%M:%S")
                        except:
                            pass
                        break
                
                same_code_panel = Panel.fit(
                    f"📱 Code: [yellow]{code}[/yellow]\n\n"
                    f"ℹ️  Same code as last check\n"
                    f"🕐 Originally received at: {last_received_time}\n"
                    f"💡 Code has been copied to clipboard again",
                    title="📱 Same SMS Code",
                    border_style="yellow",
                    padding=(1, 2)
                )
                console.print(same_code_panel)
                
                # Still copy to clipboard for convenience
                self._copy_to_clipboard_manual(code, "SMS code")
                
                # Show complete SMS history for context
                if len(sms_history) > 1:
                    all_entries = []
                    for entry in sms_history:
                        try:
                            received_dt = datetime.fromisoformat(entry['received_at'].replace('Z', '+00:00'))
                            time_str = received_dt.strftime("%H:%M:%S")
                        except:
                            time_str = "Unknown"
                        
                        marker = "➤" if entry['sms_code'] == code else "📱"
                        all_entries.append(f"{marker} {entry['sms_code']} - {time_str}")
                    
                    history_text = "\n".join(all_entries)
                    full_history_panel = Panel.fit(
                        f"Complete SMS history:\n{history_text}\n\n➤ = Current code",
                        title="📜 Complete SMS History",
                        border_style="dim",
                        padding=(1, 2)
                    )
                    console.print(full_history_panel)
        else:
            # No code received yet
            self.logger.info(f"No SMS code available yet for verification ID: {verification_id}")
            
            no_code_panel = Panel.fit(
                f"⏳ No SMS code received yet\n\n"
                f"💡 Try sending the SMS code from your service\n"
                f"🔄 Then use 'Check for SMS Code' again",
                title="📱 No SMS Yet",
                border_style="yellow",
                padding=(1, 2)
            )
            console.print(no_code_panel)
        
        console.print()
        console.print("━" * 80, style="cyan")
        console.print()
        
        # Return to options menu
        self._show_sms_verification_options(customer_data)
    
    def run(self):
        """Main application loop"""
        try:
            self.show_banner()
            
            while True:
                choice = self.show_main_menu()
                
                if choice == "1":
                    self.create_new_customer()
                elif choice == "2":
                    self.get_sms_for_customer()
                elif choice == "3":
                    self.assign_new_number()
                elif choice == "4":
                    self.view_customer_database()
                elif choice == "5":
                    self.sms_activity_monitor()
                elif choice == "6":
                    self.performance_analytics()
                elif choice == "7":
                    self.export_customer_data()
                elif choice == "8":
                    self.check_daisysms_status()
                elif choice == "9":
                    self.address_management_menu()
                elif choice == "c" or choice == "C":
                    self.show_configuration_menu()
                elif choice == "0":
                    break
                else:
                    console.print("Invalid choice. Please try again.", style="red")
            
            console.print("👋 Thank you for using CustomerDaisy!", style="cyan")
            return 0
            
        except KeyboardInterrupt:
            console.print("\n🛑 Application interrupted by user.", style="yellow")
            return 130
        except Exception as e:
            console.print(f"❌ Critical error: {e}", style="red")
            self.logger.exception("Critical application error")
            return 1

    def show_banner(self):
        """Display clean application banner"""
        if RICH_AVAILABLE:
            banner_text = f"""[bold magenta]🌸 CustomerDaisy v{__version__}[/bold magenta]
[cyan]Customer Creation & SMS Verification System[/cyan]"""
            
            panel = Panel(
                Align.center(banner_text),
                box=box.ROUNDED,
                border_style="magenta",
                padding=(0, 1),
                width=80
            )
            console.print(panel)
        else:
            console.print(f"🌸 CustomerDaisy v{__version__}")
            console.print("Customer Creation & SMS Verification System\n")
    
    def show_main_menu(self):
        """Display main menu with enhanced questionnaire interface"""
        console.print("\n")  # Clean spacing
        
        # Check if questionary will be used for dynamic instruction
        import sys
        use_questionary = QUESTIONARY_AVAILABLE and sys.stdin.isatty() and sys.stdout.isatty()
        
        if not use_questionary and RICH_AVAILABLE:
            # Only show menu panel for traditional interface
            instruction = "Select an action by number"
            panel = Panel(
                f"[bold cyan]Main Menu[/bold cyan]\n[dim]{instruction}[/dim]",
                border_style="cyan",
                padding=(0, 1),
                width=60
            )
            console.print(panel)
        
        # Use questionary for modern interface
        if QUESTIONARY_AVAILABLE:
            try:
                # Check if we have a proper interactive terminal
                import sys
                if not sys.stdin.isatty() or not sys.stdout.isatty():
                    raise RuntimeError("Non-interactive terminal detected")
                
                choices = [
                    Choice("🌸 Create New Customer (with MapQuest addresses)", value="1"),
                    Choice("📱 Get SMS Code for Existing Customer", value="2"),
                    Choice("🔄 Assign New Number to Customer", value="3"),
                    Choice("📊 View Customer Database", value="4"),
                    Choice("📡 SMS Activity Monitor", value="5"),
                    Choice("📈 Performance Analytics", value="6"),
                    Choice("📤 Export Customer Data", value="7"),
                    Choice("💰 DaisySMS Account Status", value="8"),
                    Choice("🗺️ Address Management & Testing", value="9"),
                    Choice("⚙️ Configuration Settings", value="c"),
                    Choice("🚪 Exit Application", value="0")
                ]
                
                result = questionary.select(
                    "Select an action:",
                    choices=choices,
                    use_shortcuts=True
                ).ask()
                
                return result
                
            except (KeyboardInterrupt, Exception) as e:
                # Fall through to Rich-based menu on any error
                if isinstance(e, KeyboardInterrupt):
                    return "0"
                # Only show debug info if it's not a common environment issue
                if "NonInteractiveTerminal" not in str(e) and "NoConsoleScreenBuffer" not in str(e):
                    console.print(f"💡 Using fallback menu interface ({type(e).__name__})", style="dim")
        
        # Fallback to traditional menu
        if RICH_AVAILABLE:
            menu_items = [
                "[1] Create New Customer (with MapQuest addresses)",
                "[2] Get SMS Code for Existing Customer", 
                "[3] Assign New Number to Customer",
                "[4] View Customer Database",
                "[5] SMS Activity Monitor",
                "[6] Performance Analytics",
                "[7] Export Customer Data",
                "[8] DaisySMS Account Status",
                "[9] Address Management & Testing",
                "[C] Configuration Settings",
                "[0] Exit"
            ]
            
            menu_text = "\n".join(f"  {item}" for item in menu_items)
            panel = Panel(
                menu_text,
                title="🌸 Main Menu",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(panel)
            
            return Prompt.ask("[bold green]Select an option[/bold green]", 
                             choices=["0","1","2","3","4","5","6","7","8","9","c","C"])
        else:
            # Text-only fallback
            console.print("\n=== Main Menu ===")
            console.print("1. Create New Customer (with MapQuest addresses)")
            console.print("2. Get SMS Code for Existing Customer")
            console.print("3. Assign New Number to Customer")
            console.print("4. View Customer Database")
            console.print("5. SMS Activity Monitor")
            console.print("6. Performance Analytics")
            console.print("7. Export Customer Data")
            console.print("8. DaisySMS Account Status")
            console.print("9. Address Management & Testing")
            console.print("C. Configuration Settings")
            console.print("0. Exit")
            return input("Select option: ")
    
    def create_new_customer(self):
        """Create a new customer with SMS verification and MapQuest addresses"""
        console.print("\n🌸 Creating New Customer", style="bold cyan")
        
        try:
            self.logger.info("Starting new customer creation process")
            
            # Step 1: Check DaisySMS balance
            console.print("💰 Checking balance...", style="blue")
            balance = self.sms_manager.get_balance()
            console.print(f"Balance: ${balance:.2f}", style="green")
            self.logger.info(f"DaisySMS balance checked: ${balance:.2f}")
            
            if balance < 0.05:
                console.print("❌ Insufficient DaisySMS balance", style="red")
                self.logger.warning(f"Insufficient DaisySMS balance: ${balance:.2f}")
                return
            
            # Step 2: Address selection
            address_choice = self._get_address_selection_choice()
            
            if address_choice == "recent":
                # Use recent address selection
                selected_address = self._select_recent_address()
                if selected_address:
                    # Create customer using the selected recent address
                    customer_data = self.database.generate_customer_data()
                    # Update with the selected address data
                    customer_data.update({
                        'full_address': selected_address['full_address'],
                        'city': selected_address['city'],
                        'state': selected_address['state'],
                        'zip_code': selected_address['zip_code'],
                        'latitude': selected_address['latitude'],
                        'longitude': selected_address['longitude'],
                        'address_source': f"recent_{selected_address['address_source']}"
                    })
                else:
                    # Fall back to random if no address selected
                    console.print("🎲 No address selected, using random address", style="yellow")
                    customer_data = self.database.generate_customer_data()
            elif address_choice == "custom":
                customer_data = self.database.generate_customer_data(
                    custom_address=self._get_custom_address()
                )
            elif address_choice == "near":
                origin_address = enhanced_text_input("🗺️ Enter city or address to search near:")
                customer_data = self.database.generate_customer_data(
                    origin_address=origin_address
                )
            elif address_choice == "interactive":
                # Use interactive address selection
                address_data = self.database.interactive_address_selection()
                customer_data = self.database.generate_customer_data()
                customer_data.update(address_data)
            else:
                # Random address
                customer_data = self.database.generate_customer_data()
            
            # Step 3: Create email account
            console.print("📧 Creating email account...", style="blue")
            self.logger.info(f"Creating email account for {customer_data['first_name']} {customer_data['last_name']}")
            
            email_data = self.mail_manager.create_account(
                customer_data['first_name'], 
                customer_data['last_name']
            )
            customer_data.update(email_data)
            self.logger.info(f"Email account created: {email_data.get('email', 'N/A')}")
            
            # Step 4: Get phone number
            console.print("📱 Renting phone number...", style="blue")
            self.logger.info("Requesting phone number from DaisySMS")
            
            phone_data = self.sms_manager.create_verification()
            if not phone_data:
                console.print("❌ Failed to get phone number", style="red")
                self.logger.error("Failed to rent phone number from DaisySMS")
                return
            
            customer_data.update(phone_data)
            self.logger.info(f"Phone number rented: {phone_data.get('phone_number', 'N/A')}, ID: {phone_data.get('verification_id', 'N/A')}")
            
            # Step 5: Save customer
            customer_id = self.database.save_customer(customer_data)
            console.print(f"💾 Customer saved: {customer_id[:8]}...", style="green")
            self.logger.info(f"Customer saved to database with ID: {customer_id}")
            
            # Step 6: Display customer info and verification options
            self._display_customer_info(customer_data)
            self._show_sms_verification_options(customer_data)
        
        except Exception as e:
            console.print(f"❌ Error creating customer: {e}", style="red")
            self.logger.exception("Customer creation error")
    
    def _get_address_selection_choice(self):
        """Get user's address selection preference with enhanced questionnaire interface"""
        # Check if we have recent addresses
        recent_addresses = self.database.get_recent_addresses(10)
        
        if QUESTIONARY_AVAILABLE:
            try:
                # Build choices based on whether recent addresses exist
                choices = []
                
                if recent_addresses:
                    choices.append(Choice("📍 Select from recent addresses", value="recent"))
                
                choices.extend([
                    Choice("➕ Enter custom address", value="custom"),
                    Choice("🗺️ Near location (search around a city)", value="near"),
                    Choice("🔍 Interactive selection (with auto-complete)", value="interactive"),
                    Choice("🎲 Random US address", value="random")
                ])
                
                selection = questionary.select(
                    "🏠 Choose address option:",
                    choices=choices
                ).ask()
                
                return selection if selection else "random"
                
            except (KeyboardInterrupt, Exception) as e:
                if isinstance(e, KeyboardInterrupt):
                    console.print("\n🔙 Using random address", style="yellow")
                    return "random"
                console.print(f"💡 Using traditional address selection ({type(e).__name__})", style="dim")
        
        # Fallback to Rich-based selection
        console.print("\n📍 Address Options:")
        if recent_addresses:
            console.print("1. Recent addresses (select from previously used)")
            console.print("2. Custom address (enter specific address)")
            console.print("3. Near location (search around a city/address)")
            console.print("4. Interactive selection (with auto-complete)")
            console.print("5. Random US address")
            console.print()  # Add spacing
            
            choice = Prompt.ask("Select address option [1/2/3/4/5]", choices=["1", "2", "3", "4", "5"], default="5", show_default=True)
            
            choice_map = {
                "1": "recent",
                "2": "custom",
                "3": "near", 
                "4": "interactive",
                "5": "random"
            }
        else:
            console.print("1. Custom address (enter specific address)")
            console.print("2. Near location (search around a city/address)")
            console.print("3. Interactive selection (with auto-complete)")
            console.print("4. Random US address")
            console.print()  # Add spacing
            
            choice = Prompt.ask("Select address option [1/2/3/4]", choices=["1", "2", "3", "4"], default="4", show_default=True)
            
            choice_map = {
                "1": "custom",
                "2": "near", 
                "3": "interactive",
                "4": "random"
            }
        
        return choice_map[choice]
    def _get_custom_address(self):
        """Get custom address from user with validation"""
        console.print("💡 Enter a specific address (will be validated with MapQuest)", style="blue")
        
        while True:
            address = Prompt.ask("Enter full address")
            
            if not address.strip():
                console.print("❌ Please enter a valid address", style="red")
                continue
                
            # Show preview of what will be validated
            console.print(f"🔍 Will validate: {address}", style="dim")
            
            address_choice = Prompt.ask(
                "Use this address?", 
                choices=["yes", "no", "edit"], 
                default="yes",
                show_choices=False
            )
            
            if address_choice == "yes" or address_choice == "y":
                return address
            elif address_choice == "edit":
                continue
            else:
                continue
    
    def get_sms_for_customer(self):
        """Get SMS code for existing customer - Enhanced UX with recent customers"""
        console.print("\n📱 Get SMS Code", style="bold cyan")
        
        # Get 10 most recent customers for quick selection
        recent_customers = self.database.get_recent_customers(10)
        
        if not recent_customers:
            console.print("❌ No customers in database", style="red")
            create_new = enhanced_confirm("Would you like to create a new customer?", default=False)
            if create_new:
                self.create_new_customer()
            return
        
        # Show recent customers with beautiful interactive selection
        console.print(f"📋 Showing {len(recent_customers)} most recent customers", style="dim")
        
        # Use enhanced customer selection
        customer = self._select_customer_interactive(recent_customers)
        
        # Check if customer selection was cancelled
        if customer is None:
            return
        
        # Get SMS code
        console.print(f"📱 Getting SMS for {customer['full_name']}", style="cyan")
        
        try:
            code = self.sms_manager.get_verification_code(customer['primary_verification_id'])
            
            if code:
                console.print(f"✅ SMS Code: [bold green]{code}[/bold green]", style="white")
                self._copy_to_clipboard_manual(code, "SMS code")
                
                # Log the SMS
                self.database.log_sms_received(
                    customer['customer_id'],
                    customer['primary_phone'],
                    code
                )
            else:
                console.print("❌ No SMS received", style="red")
                
                action_choice = Prompt.ask(
                    "Next action", 
                    choices=["new_number", "wait_more", "menu"], 
                    default="new_number",
                    show_choices=True
                )
                
                if action_choice == "new_number":
                    self._assign_new_number(customer['customer_id'])
                elif action_choice == "wait_more":
                    console.print("⏳ You can check again later using option 2", style="blue")
                else:
                    console.print("🔙 Returning to main menu", style="blue")
        
        except Exception as e:
            console.print(f"❌ Error getting SMS: {e}", style="red")
    def assign_new_number(self):
        """Assign new number to existing customer - Enhanced UX with recent customers"""
        console.print("\n🔄 Assign New Number", style="bold cyan")
        
        # Get 10 most recent customers for quick selection
        recent_customers = self.database.get_recent_customers(10)
        
        if not recent_customers:
            console.print("❌ No customers in database", style="red")
            create_new = enhanced_confirm("Would you like to create a new customer?", default=False)
            if create_new:
                self.create_new_customer()
            return
        
        # Show recent customers with beautiful interactive selection
        console.print(f"📋 Showing {len(recent_customers)} most recent customers", style="dim")
        
        # Use enhanced customer selection
        customer = self._select_customer_interactive(recent_customers)
        
        # Check if customer selection was cancelled
        if customer is None:
            return
        
        # Confirm the assignment
        assign_choice = enhanced_confirm(
            f"Assign new number to {customer['full_name']}?",
            default=True
        )
        
        if assign_choice:
            self._assign_new_number(customer['customer_id'])
        else:
            console.print("🔙 Assignment cancelled", style="blue")
    
    def view_customer_database(self):
        """View customer database with pagination and address information"""
        console.print("\n📊 Customer Database", style="bold cyan")
        console.print("=" * 60, style="cyan")
        
        customers = self.database.load_all_customers()
        
        if not customers:
            no_customers_banner = self._create_status_banner(
                "📭 Empty Database",
                "No Customers Found",
                [
                    ("Total Customers", "0"),
                    ("Suggestion", "Create your first customer using option 1")
                ],
                "yellow"
            )
            console.print(no_customers_banner)
            return
        
        # Display summary
        total_customers = len(customers)
        verified_customers = len([c for c in customers if c.get('verification_completed')])
        mapquest_addresses = len([c for c in customers if 'mapquest' in c.get('address_source', '')])
        success_rate = (verified_customers/total_customers*100) if total_customers > 0 else 0
        address_rate = (mapquest_addresses/total_customers*100) if total_customers > 0 else 0
        
        # Create database summary banner
        summary_banner = self._create_info_banner(
            "📈 Database Summary",
            [
                ("Total Customers", str(total_customers)),
                ("Verified Customers", f"{verified_customers} ({success_rate:.1f}%)"),
                ("MapQuest Addresses", f"{mapquest_addresses} ({address_rate:.1f}%)"),
                ("Database Health", "🟢 Excellent" if success_rate > 80 else "🟡 Good" if success_rate > 60 else "🔴 Needs Attention")
            ],
            "green"
        )
        
        console.print(summary_banner)        # Display recent customers with address info
        def safe_datetime_sort_key(customer):
            created_at = customer.get('created_at', '')
            if isinstance(created_at, str):
                try:
                    # Try parsing ISO format string to datetime for proper sorting
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    # Ensure timezone aware datetime for consistent comparison
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except (ValueError, AttributeError):
                    # If parsing fails, return epoch time for consistent sorting
                    return datetime.fromtimestamp(0, tz=timezone.utc)
            elif isinstance(created_at, datetime):
                # Ensure timezone aware datetime
                if created_at.tzinfo is None:
                    return created_at.replace(tzinfo=timezone.utc)
                return created_at
            else:
                # For any other type, return epoch time
                return datetime.fromtimestamp(0, tz=timezone.utc)
        
        recent_customers = sorted(customers, key=safe_datetime_sort_key, reverse=True)[:10]
        
        customer_table = Table(title="Recent Customers")
        customer_table.add_column("Name", style="cyan")
        customer_table.add_column("Email", style="green")
        customer_table.add_column("Password", style="red")
        customer_table.add_column("Phone", style="yellow")
        customer_table.add_column("City, State", style="blue")
        customer_table.add_column("Address Source", style="magenta")
        customer_table.add_column("Status", style="white")
        
        for customer in recent_customers:
            status = "✅ Verified" if customer.get('verification_completed') else "⏳ Pending"
            city_state = f"{customer.get('city', 'N/A')}, {customer.get('state', 'N/A')}"
            address_source = customer.get('address_source', 'unknown')
            
            # Truncate long email
            email = customer.get('email', 'N/A')
            if len(email) > 25:
                email = email[:22] + "..."
            
            customer_table.add_row(
                customer.get('full_name', 'N/A'),
                email,
                customer.get('password', 'N/A'),
                customer.get('primary_phone', 'N/A'),
                city_state,
                address_source,
                status
            )
        
        console.print(customer_table)
    
    def sms_activity_monitor(self):
        """Real-time SMS activity monitoring"""
        console.print("\n🔍 SMS Activity Monitor", style="bold cyan")
        console.print("Monitoring active SMS verifications...", style="blue")
        console.print("Press Ctrl+C to exit", style="dim")
        
        try:
            self.sms_monitor.start_monitoring(self.database, self.sms_manager)
        except KeyboardInterrupt:
            console.print("\n🛑 Monitoring stopped", style="yellow")
    def performance_analytics(self):
        """Show performance analytics including address analytics"""
        console.print("\n📈 Performance Analytics", style="bold cyan")
        console.print("=" * 60, style="cyan")
        
        analytics = self.database.generate_analytics()
        
        # Create performance summary banner
        summary_items = []
        for metric, value in analytics['summary'].items():
            formatted_metric = metric.replace('_', ' ').title()
            summary_items.append((formatted_metric, str(value)))
        
        performance_banner = self._create_info_banner(
            "🎯 Performance Summary",
            summary_items,
            "cyan"
        )
        
        console.print(performance_banner)
        
        # Address analytics
        if analytics.get('address_analytics'):
            address_analytics = analytics['address_analytics']
            mapquest_usage = address_analytics.get('mapquest_usage', {})
            
            address_banner = self._create_info_banner(
                "🗺️ Address Analytics",
                [
                    ("MapQuest Enabled", "✅ Yes" if mapquest_usage.get('mapquest_enabled') else "❌ No"),
                    ("Real Addresses", str(mapquest_usage.get('real_addresses', 0))),
                    ("Fallback Addresses", str(mapquest_usage.get('fallback_addresses', 0))),
                    ("Validation Rate", f"{address_analytics.get('validation_rate', 0)}%")
                ],
                "magenta"
            )
            
            console.print(address_banner)
        
        # SMS performance
        if analytics.get('sms_performance'):
            sms_items = []
            for metric, value in analytics['sms_performance'].items():
                formatted_metric = metric.replace('_', ' ').title()
                sms_items.append((formatted_metric, str(value)))
            
            sms_banner = self._create_info_banner(
                "📱 SMS Performance",
                sms_items,
                "yellow"
            )
            
            console.print(sms_banner)
    def export_customer_data(self):
        """Export customer data in various formats"""
        console.print("\n📤 Export Customer Data", style="bold cyan")
        
        formats = ["json", "csv", "txt"]
        format_choice = enhanced_select("📤 Export format:", formats, default="json")
        
        try:
            filename = self.database.export_customers(format_choice)
            console.print(f"✅ Data exported to: {filename}", style="green")
            console.print("💡 Export includes MapQuest address data and coordinates", style="blue")
        except Exception as e:
            console.print(f"❌ Export failed: {e}", style="red")
    
    def _create_info_banner(self, title: str, items: list, style: str = "cyan") -> Panel:
        """Create a compact information banner"""
        content_lines = []
        
        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                label, value = item
                content_lines.append(f"[bold {style}]{label}:[/bold {style}] [white]{value}[/white]")
            else:
                content_lines.append(f"[white]{item}[/white]")
        
        content = "\n".join(content_lines)
        
        return Panel(
            content,
            title=f"[bold {style}]{title}[/bold {style}]",
            border_style=style,
            padding=(0, 1),
            expand=False,
            width=80
        )
    
    def _create_status_banner(self, title: str, status: str, details: list, color: str = "green") -> Panel:
        """Create a compact status banner"""
        status_icon = "🟢" if color == "green" else "🟡" if color == "yellow" else "🔴"
        
        content_lines = [f"[bold {color}]{status_icon} {status}[/bold {color}]"]
        
        for detail in details:
            if isinstance(detail, tuple) and len(detail) == 2:
                label, value = detail
                content_lines.append(f"[dim]{label}:[/dim] [white]{value}[/white]")
            else:
                content_lines.append(f"[white]{detail}[/white]")
        
        content = "\n".join(content_lines)
        
        return Panel(
            content,
            title=f"[bold {color}]{title}[/bold {color}]",
            border_style=color,
            padding=(0, 1),
            expand=False,
            width=80
        )

    def check_daisysms_status(self):
        """Check DaisySMS account status with beautiful banners"""
        console.print("\n💰 DaisySMS Account Status", style="bold cyan")
        console.print("=" * 60, style="cyan")
        
        try:
            # Get balance
            balance = self.sms_manager.get_balance()
            
            # Get pricing info
            pricing = self.sms_manager.get_pricing_info()
            
            # Create account info banner
            account_info = self._create_info_banner(
                "💳 Account Information",
                [
                    ("Balance", f"${balance:.2f}"),
                    ("API Key", f"{'✅ Active' if balance > 0 else '❌ Invalid'}"),
                    ("Last Updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                ],
                "blue"
            )
            
            # Create service info banner
            service_name = pricing.get('service_name', 'Unknown')
            service_price = pricing.get('price', 0)
            max_price = pricing.get('max_price', 0)
            
            service_info = self._create_info_banner(
                f"📱 Service: {service_name}",
                [
                    ("Service Code", pricing.get('service', 'N/A')),
                    ("Typical Price", f"${service_price:.2f}"),
                    ("Your Max Price", f"${max_price:.2f}"),
                    ("Country", "USA (0)" if pricing.get('country', 0) == 0 else f"Country {pricing.get('country', 0)}")
                ],
                "magenta"
            )
            
            # Create availability status banner
            available_count = pricing.get('count', 0)
            is_available = available_count > 0
            
            availability_status = self._create_status_banner(
                "📊 Service Availability",
                "Service Available" if is_available else "Service Unavailable",
                [
                    ("Available Numbers", f"{available_count}+" if available_count >= 100 else str(available_count)),
                    ("Status", "Ready for use" if is_available else "No numbers available"),
                    ("Can Rent", "Yes" if balance >= service_price and is_available else "No")
                ],
                "green" if is_available else "red"
            )
            
            # Display all banners
            console.print(account_info)
            console.print(service_info)
            console.print(availability_status)
            
            # Show balance warning if low
            if balance < 1.0:
                warning_banner = self._create_status_banner(
                    "⚠️ Low Balance Warning",
                    "Balance Running Low",
                    [
                        ("Current Balance", f"${balance:.2f}"),
                        ("Recommended", "Add funds to continue"),
                        ("Minimum for Service", f"${service_price:.2f}")
                    ],
                    "yellow"
                )
                console.print(warning_banner)
            
        except Exception as e:
            error_banner = self._create_status_banner(
                "❌ Connection Error",
                "Failed to Check Status",
                [
                    ("Error", str(e)),
                    ("Suggestion", "Check your API key and internet connection")
                ],
                "red"
            )
            console.print(error_banner)
    def address_management_menu(self):
        """Address management and testing menu with questionary interface"""
        console.print("\n🗺️ Address Management & Testing", style="bold cyan")
        
        while True:
            # Use questionary for modern interface  
            if QUESTIONARY_AVAILABLE:
                try:
                    import sys
                    if sys.stdin.isatty() and sys.stdout.isatty():
                        choices = [
                            Choice("🔗 Test MapQuest API connection", value="1"),
                            Choice("✅ Validate a specific address", value="2"),
                            Choice("🔍 Search addresses", value="3"),
                            Choice("📍 Get random address near location", value="4"),
                            Choice("🎲 Get random US address", value="5"),
                            Choice("📊 View address analytics", value="6"),
                            Choice("🔙 Back to main menu", value="0")
                        ]
                        
                        choice = questionary.select(
                            "Select an address management option:",
                            choices=choices,
                            use_shortcuts=True
                        ).ask()
                        
                        if not choice:
                            choice = "0"
                    else:
                        raise RuntimeError("Non-interactive terminal")
                        
                except (KeyboardInterrupt, Exception) as e:
                    if isinstance(e, KeyboardInterrupt):
                        choice = "0"
                    else:
                        # Fallback to enhanced_select
                        choice = enhanced_select(
                            "Select an option:",
                            ["🔗 Test API", "✅ Validate address", "🔍 Search", "📍 Near location", "🎲 Random US", "📊 Analytics", "🔙 Back"],
                            default="🔙 Back"
                        )
                        choice_map = {
                            "🔗 Test API": "1", "✅ Validate address": "2", "🔍 Search": "3",
                            "📍 Near location": "4", "🎲 Random US": "5", "📊 Analytics": "6", "🔙 Back": "0"
                        }
                        choice = choice_map.get(choice, "0")
            else:
                # Rich fallback
                choice = enhanced_select(
                    "Select an option:",
                    ["🔗 Test API", "✅ Validate address", "🔍 Search", "📍 Near location", "🎲 Random US", "📊 Analytics", "🔙 Back"],
                    default="🔙 Back"
                )
                choice_map = {
                    "🔗 Test API": "1", "✅ Validate address": "2", "🔍 Search": "3",
                    "📍 Near location": "4", "🎲 Random US": "5", "📊 Analytics": "6", "🔙 Back": "0"
                }
                choice = choice_map.get(choice, "0")
            
            if choice == "0":
                break
            elif choice == "1":
                self._test_mapquest_connection()
            elif choice == "2":
                self._validate_address_interactive()
            elif choice == "3":
                self._search_addresses_interactive()
            elif choice == "4":
                self._get_address_near_location()
            elif choice == "5":
                self._get_random_us_address()
            elif choice == "6":
                self._show_address_analytics()
    
    def _test_mapquest_connection(self):
        """Test MapQuest API connection"""
        console.print("\n🔗 Testing MapQuest API connection...", style="blue")
        
        if self.mapquest_manager.test_api_connection():
            stats = self.mapquest_manager.get_api_stats()
            
            stats_table = Table(title="MapQuest API Status")
            stats_table.add_column("Property", style="cyan")
            stats_table.add_column("Value", style="white")
            
            for key, value in stats.items():
                stats_table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(stats_table)
        else:
            console.print("❌ MapQuest API test failed", style="red")
    def _validate_address_interactive(self):
        """Interactive address validation"""
        address = Prompt.ask("\nEnter address to validate")
        
        console.print("🔍 Validating address...", style="yellow")
        result = self.mapquest_manager.validate_address(address)
        
        if result:
            validation_table = Table(title="Address Validation Result")
            validation_table.add_column("Field", style="cyan")
            validation_table.add_column("Value", style="white")
            
            validation_table.add_row("Original", address)
            validation_table.add_row("Standardized", result['full_address'])
            validation_table.add_row("Street", result['address_line1'])
            validation_table.add_row("City", result['city'])
            validation_table.add_row("State", result['state'])
            validation_table.add_row("ZIP", result['zip_code'])
            validation_table.add_row("Latitude", str(result.get('latitude', 'N/A')))
            validation_table.add_row("Longitude", str(result.get('longitude', 'N/A')))
            validation_table.add_row("Quality", result.get('geocode_quality', 'N/A'))
            
            console.print(validation_table)
        else:
            console.print("❌ Address validation failed", style="red")
    
    def _search_addresses_interactive(self):
        """Interactive address search"""
        query = Prompt.ask("\nEnter search query (city, partial address, etc.)")
        max_results = IntPrompt.ask("Maximum results", default=5)
        
        console.print("🔍 Searching addresses...", style="yellow")
        results = self.mapquest_manager.search_addresses(query, max_results)
        
        if results:
            search_table = Table(title=f"Search Results for '{query}'")
            search_table.add_column("Index", style="cyan")
            search_table.add_column("Address", style="white")
            search_table.add_column("City", style="green")
            search_table.add_column("State", style="blue")
            
            for i, result in enumerate(results):
                search_table.add_row(
                    str(i + 1),
                    result['address_line1'],
                    result['city'],
                    result['state']
                )
            
            console.print(search_table)
        else:
            console.print("❌ No addresses found", style="red")
    def _get_address_near_location(self):
        """Get random address near a location"""
        origin = Prompt.ask("\nEnter origin address or city")
        radius = IntPrompt.ask("Search radius in miles", default=10)
        
        console.print(f"🎲 Finding random address near {origin}...", style="yellow")
        result = self.mapquest_manager.get_random_address_near_location(origin, radius)
        
        if result:
            self._display_address_result(result)
        else:
            console.print("❌ No address found near location", style="red")
    
    def _get_random_us_address(self):
        """Get random US address"""
        console.print("\n🎲 Getting random US address...", style="yellow")
        result = self.mapquest_manager.get_random_us_address()
        
        if result:
            self._display_address_result(result)
        else:
            console.print("❌ Failed to get random address", style="red")
    
    def _display_address_result(self, address_data):
        """Display address result in beautiful banner"""
        address_items = [
            ("Full Address", address_data['full_address']),
            ("Street", address_data['address_line1']),
            ("City", address_data['city']),
            ("State", address_data['state']),
            ("ZIP Code", address_data['zip_code'])
        ]
        
        if address_data.get('latitude') and address_data.get('longitude'):
            address_items.append(("Coordinates", f"{address_data['latitude']}, {address_data['longitude']}"))
        
        if address_data.get('distance_from_origin'):
            address_items.append(("Distance", f"{address_data['distance_from_origin']:.1f} miles"))
        
        address_items.append(("Source", address_data.get('source', 'Unknown')))
        
        address_banner = self._create_info_banner(
            "🗺️ Address Result",
            address_items,
            "blue"
        )
        
        console.print(address_banner)
    def _show_address_analytics(self):
        """Show address-related analytics with beautiful banners"""
        console.print("\n📊 Address Analytics", style="blue")
        console.print("=" * 60, style="blue")
        
        analytics = self.database.generate_analytics()
        address_analytics = analytics.get('address_analytics', {})
        
        if address_analytics:
            # Address sources
            if address_analytics.get('address_sources'):
                sources_items = []
                for source, count in address_analytics['address_sources'].items():
                    sources_items.append((source.title(), str(count)))
                
                sources_banner = self._create_info_banner(
                    "🏭 Address Sources",
                    sources_items,
                    "cyan"
                )
                console.print(sources_banner)
            
            # Geographic distribution
            geo_data = address_analytics.get('geographic_distribution', {})
            if geo_data:
                geo_banner = self._create_info_banner(
                    "🌍 Geographic Distribution",
                    [
                        ("Unique States", str(geo_data.get('unique_states', 0))),
                        ("Unique Cities", str(geo_data.get('unique_cities', 0))),
                        ("Validation Rate", f"{address_analytics.get('validation_rate', 0)}%")
                    ],
                    "green"
                )
                console.print(geo_banner)
                
                # Top states
                top_states = geo_data.get('top_states', [])[:5]
                if top_states:
                    states_items = []
                    for state, count in top_states:
                        states_items.append((state, str(count)))
                    
                    states_banner = self._create_info_banner(
                        "🏆 Top 5 States",
                        states_items,
                        "magenta"
                    )
                    console.print(states_banner)
        else:
            no_analytics_banner = self._create_status_banner(
                "📊 Address Analytics",
                "No Data Available",
                [
                    ("Reason", "No customers with address data found"),
                    ("Suggestion", "Create some customers first")
                ],
                "yellow"
            )
            console.print(no_analytics_banner)

    def _display_customer_info(self, customer_data):
        """Display customer information in clean format"""
        console.print()
        console.print("═" * 80, style="green")
        console.print("🎉 Customer Created Successfully!", style="bold green")
        console.print("═" * 80, style="green")
        console.print()
        
        # Prominently display email credentials
        email_password = customer_data.get('email_password', customer_data.get('password', 'N/A'))
        console.print("📧 EMAIL CREDENTIALS (COPY THESE NOW!)", style="bold yellow")
        console.print("─" * 50, style="yellow")
        console.print(f"📧 Email: {customer_data['email']}", style="bright_green")
        console.print(f"🔑 Password: {email_password}", style="bright_green")
        console.print("─" * 50, style="yellow")
        console.print()
        
        # Format phone number and copy to clipboard
        formatted_phone, clipboard_status = self._format_phone_for_user(customer_data.get('phone_number', ''))
        
        # Get the email password (prioritize email_password field)
        email_password = customer_data.get('email_password', customer_data.get('password', 'N/A'))
        
        # Personal Information Banner
        personal_banner = self._create_info_banner(
            "👤 Personal Information",
            [
                ("Name", customer_data['full_name']),
                ("Email", customer_data['email']),
                ("Email Password", email_password),
                ("Phone", f"{formatted_phone} ({clipboard_status})")
            ],
            "cyan"
        )
        
        # Address Information Banner
        address_items = [
            ("Full Address", customer_data['full_address']),
            ("Address Source", customer_data.get('address_source', 'unknown')),
            ("Validated", "✅ Yes" if customer_data.get('address_validated') else "❌ No")
        ]
        
        if customer_data.get('latitude') and customer_data.get('longitude'):
            address_items.append(("Coordinates", f"{customer_data['latitude']}, {customer_data['longitude']}"))
        
        address_banner = self._create_info_banner(
            "🏠 Address Information",
            address_items,
            "magenta"
        )
        console.print()
        
        # Verification Banner
        verification_banner = self._create_status_banner(
            "📱 SMS Verification",
            "Ready for Verification",
            [
                ("Verification ID", customer_data.get('verification_id', 'N/A')),
                ("Phone Number", customer_data.get('phone_number', 'N/A')),
                ("Status", "Awaiting SMS code")
            ],
            "yellow"
        )
        
        # Display all banners
        console.print(personal_banner)
        console.print(address_banner)
        console.print(verification_banner)
        
        console.print()
        console.print("═" * 80, style="green")
        console.print()
    
    def _wait_for_verification(self, customer_data):
        """Wait for SMS verification with improved UI and navigation options"""
        verification_id = customer_data.get('verification_id') or customer_data.get('primary_verification_id')
        
        # First check if verification is already cancelled/refunded
        verification_info = self.sms_manager.active_verifications.get(verification_id)
        if verification_info and verification_info.get('status') == 'cancelled':
            console.print("❌ Cannot wait for SMS - verification was already cancelled/refunded", style="red")
            console.print("💡 Would you like to assign a new number?", style="yellow")
            
            if enhanced_confirm("Assign new number?", default=True):
                self._assign_new_number(customer_data['customer_id'])
            return
        
        console.print("\n⏳ SMS Verification Monitor", style="bold cyan")
        console.print("═" * 50, style="cyan")
        console.print(f"📱 Phone: {customer_data.get('phone_number') or customer_data.get('primary_phone')}", style="blue")
        console.print(f"🆔 ID: {verification_id}", style="dim")
        console.print("\n💡 Options:", style="yellow")
        console.print("  • Press [Enter] to check once for SMS (with debug info)")
        console.print("  • Press [m] + Enter to return to main menu")
        console.print("  • Press [n] + Enter to assign new number")
        console.print("  • Press [w] + Enter to start continuous monitoring")
        console.print("  • Press [d] + Enter to enable detailed debug mode")
        console.print("\n" + "═" * 50, style="cyan")
        
        received_codes = []
        
        while True:
            try:
                user_input = input("\nAction [Enter/m/n/w/d]: ").strip().lower()
                
                if user_input == "m":
                    console.print("🔙 Returning to main menu", style="blue")
                    return
                elif user_input == "n":
                    console.print("🔄 Assigning new number...", style="cyan")
                    self._assign_new_number(customer_data['customer_id'])
                    return
                elif user_input == "w":
                    console.print("⏳ Starting continuous monitoring...", style="yellow")
                    console.print("💡 Press Ctrl+C to stop and return to options", style="dim")
                    self._continuous_sms_monitor(customer_data, received_codes)
                elif user_input == "d":
                    # Debug mode - show raw API responses
                    console.print("📜 Debug Mode: Showing raw API responses", style="cyan")
                    self._debug_sms_check(verification_id)
                elif user_input == "" or user_input == "enter":
                    # Single check
                    console.print("🔍 Checking for SMS code...", style="blue")
                    
                    # Check if verification is still active
                    verification_info = self.sms_manager.active_verifications.get(verification_id)
                    if verification_info and verification_info.get('status') == 'cancelled':
                        console.print("❌ Verification was cancelled/refunded - cannot receive SMS", style="red")
                        console.print("💡 Use 'n' to assign a new number", style="yellow")
                        continue
                    
                    # Use proper polling attempts with debug info (10 attempts = ~30 seconds)
                    code = self.sms_manager.get_verification_code(verification_id, max_attempts=10, silent=False)
                    
                    if code:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        if not any(existing['code'] == code for existing in received_codes):
                            received_codes.append({'code': code, 'timestamp': timestamp})
                            
                            # Log the SMS
                            self.database.log_sms_received(
                                customer_data['customer_id'],
                                customer_data.get('phone_number') or customer_data.get('primary_phone'),
                                code
                            )
                            
                            # Update verification status
                            self.database.update_customer_verification(
                                customer_data['customer_id'], True, code
                            )
                            
                            console.print(f"\n🎉 SMS Code Received!", style="bold green")
                            console.print(f"📱 Code: [bold green]{code}[/bold green]", style="white")
                            console.print(f"🕐 Time: {timestamp}", style="blue")
                            self._copy_to_clipboard_manual(code, "SMS code")
                        else:
                            console.print(f"📱 Code (already received): {code}", style="dim")
                    else:
                        # Check if verification was cancelled during the check
                        updated_verification_info = self.sms_manager.active_verifications.get(verification_id)
                        if updated_verification_info and updated_verification_info.get('status') == 'cancelled':
                            console.print("❌ Verification was cancelled during check", style="red")
                            console.print("💡 Use 'n' to assign a new number", style="yellow")
                        else:
                            console.print("⏳ No SMS received yet (verification still active)", style="yellow")
                else:
                    console.print("❌ Invalid option. Use Enter, m, n, w, or d", style="red")
            
            except KeyboardInterrupt:
                console.print("\n🔙 Returning to options menu", style="blue")
                continue
    
    def _continuous_sms_monitor(self, customer_data, received_codes):
        """Continuous SMS monitoring with clean, non-overwriting display"""
        verification_id = customer_data.get('verification_id') or customer_data.get('primary_verification_id')
        start_time = time.time()
        
        try:
            console.print("\n📡 Continuous Monitoring Active", style="bold green")
            last_status_line = None
            
            while True:
                elapsed = time.time() - start_time
                
                # Check if verification is still active
                verification_info = self.sms_manager.active_verifications.get(verification_id)
                if verification_info and verification_info.get('status') == 'cancelled':
                    console.print("\n❌ Verification was cancelled/refunded - stopping monitoring", style="red")
                    break
                
                # Check for SMS code (allow reasonable polling time - 10 attempts = ~30 seconds)
                code = self.sms_manager.get_verification_code(verification_id, max_attempts=10, silent=False)
                
                if code and not any(existing['code'] == code for existing in received_codes):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    received_codes.append({'code': code, 'timestamp': timestamp})
                    
                    # Log the SMS
                    self.database.log_sms_received(
                        customer_data['customer_id'],
                        customer_data.get('phone_number') or customer_data.get('primary_phone'),
                        code
                    )
                    
                    # Update verification status
                    self.database.update_customer_verification(
                        customer_data['customer_id'], True, code
                    )
                    
                    console.print(f"\n🎉 NEW SMS CODE: [bold green]{code}[/bold green] (at {timestamp})", style="white")
                    self._copy_to_clipboard_manual(code, "SMS code")
                    console.print("💡 Press Ctrl+C to stop monitoring", style="dim")
                elif not code:
                    # Check if verification was cancelled during the check
                    updated_verification_info = self.sms_manager.active_verifications.get(verification_id)
                    if updated_verification_info and updated_verification_info.get('status') == 'cancelled':
                        console.print("\n❌ Verification was cancelled during monitoring", style="red")
                        break
                
                # Update status line without scrolling
                current_status = f"⏱️  Monitoring... {elapsed:.0f}s elapsed | Codes: {len(received_codes)}"
                if current_status != last_status_line:
                    print(f"\r{current_status}", end="", flush=True)
                    last_status_line = current_status
                
                time.sleep(3)
                
                # Timeout after 10 minutes
                if elapsed > 600:
                    console.print("\n⏰ Monitoring timeout (10 minutes)", style="yellow")
                    break
        
        except KeyboardInterrupt:
            console.print("\n🛑 Monitoring stopped", style="yellow")
        
        # Show summary
        if received_codes:
            console.print(f"\n📋 Summary: {len(received_codes)} codes received", style="cyan")
            for i, code_data in enumerate(received_codes, 1):
                console.print(f"  {i}. {code_data['code']} (at {code_data['timestamp']})", style="white")
        
        console.print("\n🔙 Returning to options menu...", style="blue")
    
    def _debug_sms_check(self, verification_id):
        """Debug SMS check with detailed API response information"""
        console.print(f"\n🔍 Debug SMS Check for ID: {verification_id}", style="cyan")
        console.print("═" * 60, style="cyan")
        
        # Check verification status
        verification_info = self.sms_manager.active_verifications.get(verification_id)
        if verification_info:
            console.print(f"📊 Verification Status: {verification_info.get('status')}", style="blue")
            console.print(f"📱 Phone: {verification_info.get('phone_number')}", style="blue")
            console.print(f"🕰️ Created: {verification_info.get('created_at')}", style="blue")
            console.print(f"⏰ Timeout: {verification_info.get('timeout_at')}", style="blue")
        else:
            console.print("❌ Verification info not found", style="red")
            return
        
        # Make raw API request
        console.print(f"\n🔍 Making raw API request...", style="yellow")
        
        try:
            # Direct API call with full debugging
            response = self.sms_manager._make_request('getStatus', {'id': verification_id})
            
            console.print(f"\n📜 Raw API Response:", style="bold cyan")
            console.print(f"   Status: {response.get('status', 'None')}", style="white")
            console.print(f"   Data: {response.get('data', 'None')}", style="white")
            console.print(f"   Raw Response: {response.get('raw_response', 'None')}", style="white")
            
            # Check for different response formats
            raw_response = response.get('raw_response', '')
            if raw_response:
                console.print(f"\n🔍 Analyzing raw response: '{raw_response}'", style="cyan")
                
                # Check for different SMS code formats
                if ':' in raw_response:
                    parts = raw_response.split(':')
                    console.print(f"   Split by ':': {parts}", style="dim")
                    
                    if len(parts) >= 2:
                        potential_code = parts[1].strip()
                        if potential_code.isdigit():
                            console.print(f"   ✅ Found potential SMS code: {potential_code}", style="green")
                        else:
                            console.print(f"   ⚠️ Not a numeric code: {potential_code}", style="yellow")
                
                # Check for known status patterns
                known_statuses = ['STATUS_OK', 'STATUS_WAIT_CODE', 'STATUS_CANCEL', 'NO_ACTIVATION']
                if any(status in raw_response for status in known_statuses):
                    console.print(f"   📊 Known status detected", style="blue")
                else:
                    console.print(f"   ❓ Unknown response format", style="yellow")
            
        except Exception as e:
            console.print(f"\n❌ API Request Error: {e}", style="red")
        
        console.print("\n🔙 Debug complete. Press Enter to continue...", style="blue")
        input()
    def _assign_new_number(self, customer_id):
        """Assign new number to customer"""
        console.print(f"🔄 Assigning new number...", style="cyan")
        
        try:
            # Get new phone number
            phone_data = self.sms_manager.create_verification()
            if not phone_data:
                console.print("❌ Failed to get new phone number", style="red")
                return
            
            # Update customer record
            success = self.database.assign_new_number(customer_id, phone_data)
            
            if success:
                console.print(f"✅ New number assigned: {phone_data['phone_number']}", style="green")
                
                # Option to wait for verification
                if enhanced_confirm("Wait for SMS on new number?", default=True):
                    # Use the verification system
                    customer_data = self.database.get_customer_by_id(customer_id)
                    customer_data.update({
                        'phone_number': phone_data['phone_number'],
                        'verification_id': phone_data['verification_id']
                    })
                    self._wait_for_verification(customer_data)
            else:
                console.print("❌ Failed to assign new number", style="red")
        
        except Exception as e:
            console.print(f"❌ Error assigning number: {e}", style="red")
    
    def _select_customer(self, customers):
        """Helper to select customer from multiple results"""
        table = Table(title="Multiple Customers Found")
        table.add_column("Index", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Email", style="green")
        table.add_column("Password", style="red")
        table.add_column("Phone", style="yellow")
        table.add_column("City", style="blue")
        
        for i, customer in enumerate(customers):
            table.add_row(
                str(i), 
                customer.get('full_name', 'N/A'), 
                customer.get('email', 'N/A'), 
                customer.get('password', 'N/A'),
                customer.get('primary_phone', 'N/A'),
                customer.get('city', 'N/A')
            )
        
        console.print(table)
        console.print("💡 Enter 'c' to cancel", style="dim")
        
        while True:
            try:
                valid_choices = [str(i) for i in range(len(customers))] + ['c', 'C']
                selection = Prompt.ask(
                    "Select customer", 
                    choices=valid_choices,
                    show_choices=False
                )
                
                if selection.lower() == 'c':
                    console.print("🔙 Selection cancelled", style="blue")
                    return None
                
                index = int(selection)
                return customers[index]
                
            except (ValueError, IndexError):
                console.print("❌ Invalid selection. Please try again.", style="red")
    
    def _select_customer_interactive(self, recent_customers: List[Dict]) -> Optional[Dict]:
        """Enhanced customer selection using questionary for beautiful UX"""
        if not recent_customers:
            console.print("❌ No customers found", style="red")
            return None
            
        if not QUESTIONARY_AVAILABLE:
            # Fallback to Rich-based selection
            return self._select_customer(recent_customers)
        
        # Create choices for questionary
        choices = []
        for customer in recent_customers:
            # Format customer info beautifully
            name = customer.get('full_name', 'Unknown')
            email = customer.get('email', 'No email')
            phone = customer.get('primary_phone', 'No phone')
            city = customer.get('city', 'Unknown')
            state = customer.get('state', '')
            verified = "✅" if customer.get('verification_completed') else "📱"
            
            # Create display text with status indicator and location
            display_text = f"{verified} {name}"
            if city and city != 'Unknown':
                display_text += f" ({city}, {state})"
            if phone and phone != 'No phone':
                display_text += f" • {phone}"
            
            choices.append(Choice(
                title=display_text,
                value=customer
            ))
        
        # Add search and cancel options
        choices.extend([
            Choice("🔍 Search for different customer", value="search"),
            Choice("🔙 Cancel and return to main menu", value="cancel")
        ])
        
        try:
            # Use questionary for beautiful selection
            selection = questionary.select(
                "Select a customer:",
                choices=choices,
                style=questionary.Style([
                    ('question', 'bold cyan'),
                    ('pointer', 'cyan'),
                    ('highlighted', 'bold cyan'),
                    ('selected', 'bold green'),
                    ('separator', 'white'),
                    ('instruction', 'gray'),
                    ('text', 'white'),
                    ('disabled', 'gray'),
                ])
            ).ask()
            
            if selection == "search":
                return self._handle_customer_search()
            elif selection == "cancel":
                console.print("🔙 Returning to main menu", style="blue")
                return None
            else:
                return selection
                
        except KeyboardInterrupt:
            console.print("\n🔙 Selection cancelled", style="yellow")
            return None
    
    def _handle_customer_search(self) -> Optional[Dict]:
        """Handle manual customer search when user chooses search option"""
        try:
            if QUESTIONARY_AVAILABLE:
                search_term = questionary.text(
                    "Enter customer name, email, or phone to search:",
                    style=questionary.Style([
                        ('question', 'bold cyan'),
                        ('answer', 'bold white'),
                    ])
                ).ask()
                
                if not search_term:
                    return None
            else:
                search_term = Prompt.ask("Enter customer name, email, or phone to search (or 'cancel' to go back)")
                
            if search_term and search_term.lower() != 'cancel':
                customers = self.database.search_customers(search_term)
                if customers:
                    return self._select_customer_interactive(customers)
                else:
                    console.print("❌ No customers found matching that search", style="red")
                    if QUESTIONARY_AVAILABLE:
                        retry = questionary.confirm("Try searching again?").ask()
                        if retry:
                            return self._handle_customer_search()
                    return None
            else:
                return None
                
        except KeyboardInterrupt:
            console.print("\n🔙 Search cancelled", style="yellow")
            return None
    
    def _select_recent_address(self, limit: int = 10) -> Optional[Dict]:
        """Select from recently used addresses using enhanced questionnaire interface"""
        recent_addresses = self.database.get_recent_addresses(limit)
        
        if not recent_addresses:
            console.print("ℹ️ No recent addresses found", style="blue")
            return None
            
        if QUESTIONARY_AVAILABLE:
            try:
                # Create choices for questionary
                choices = []
                for addr in recent_addresses:
                    full_addr = addr.get('full_address', 'Unknown address')
                    city = addr.get('city', 'Unknown')
                    state = addr.get('state', 'Unknown')
                    source = addr.get('address_source', 'unknown')
                    
                    # Create display text with source indicator
                    source_icon = "🗺️" if 'mapquest' in source.lower() else "📍"
                    display_text = f"{source_icon} {full_addr}"
                    if city != 'Unknown':
                        display_text += f" ({city}, {state})"
                    
                    choices.append(Choice(
                        title=display_text,
                        value=addr
                    ))
                
                choices.append(Choice("➕ Enter new address", value="new"))
                
                selection = questionary.select(
                    "📍 Select a recent address or enter new:",
                    choices=choices
                ).ask()
                
                return selection if selection != "new" else None
                
            except (KeyboardInterrupt, Exception) as e:
                if isinstance(e, KeyboardInterrupt):
                    console.print("\n🔙 Address selection cancelled", style="yellow")
                    return None
                console.print(f"💡 Using traditional address selection ({type(e).__name__})", style="dim")
        
        # Fallback to Rich-based selection
        table = Table(title="Recent Addresses")
        table.add_column("Index", style="cyan")
        table.add_column("Address", style="white")
        table.add_column("City, State", style="green")
        
        for i, addr in enumerate(recent_addresses):
            table.add_row(
                str(i),
                addr.get('full_address', 'N/A'),
                f"{addr.get('city', 'Unknown')}, {addr.get('state', 'Unknown')}"
            )
        
        console.print(table)
        choice = Prompt.ask(
            "Select address (or 'n' for new address)",
            choices=[str(i) for i in range(len(recent_addresses))] + ['n'],
            default='n'
        )
        
        if choice == 'n':
            return None
        else:
            return recent_addresses[int(choice)]

    def _get_status_indicator(self, metric, value):
        """Get status indicator emoji for metrics"""
        if 'rate' in metric.lower() or 'percentage' in metric.lower():
            if isinstance(value, (int, float)):
                if value >= 90:
                    return "🟢"
                elif value >= 70:
                    return "🟡"
                else:
                    return "🔴"
        return "📊"


    def show_configuration_menu(self):
        """Configuration settings menu with questionary interface"""
        console.print("\n⚙️ Configuration Settings", style="bold cyan")
        
        while True:
            # Use questionary for modern interface
            if QUESTIONARY_AVAILABLE:
                try:
                    import sys
                    if sys.stdin.isatty() and sys.stdout.isatty():
                        choices = [
                            Choice("📱 DaisySMS API Settings", value="1"),
                            Choice("🗺️ MapQuest API Settings", value="2"),
                            Choice("📧 Mail.tm Settings", value="3"),
                            Choice("👥 Customer Generation Settings", value="4"),
                            Choice("👁️ View Current Configuration", value="5"),
                            Choice("🔙 Back to main menu", value="0")
                        ]
                        
                        choice = questionary.select(
                            "Select a configuration option:",
                            choices=choices,
                            use_shortcuts=True
                        ).ask()
                        
                        if not choice:
                            choice = "0"
                    else:
                        raise RuntimeError("Non-interactive terminal")
                        
                except (KeyboardInterrupt, Exception) as e:
                    if isinstance(e, KeyboardInterrupt):
                        choice = "0"
                    else:
                        # Fallback to enhanced_select
                        choice = enhanced_select(
                            "Select a configuration option:",
                            ["📱 DaisySMS", "🗺️ MapQuest", "📧 Mail.tm", "👥 Customer Gen", "👁️ View Config", "🔙 Back"],
                            default="🔙 Back"
                        )
                        choice_map = {
                            "📱 DaisySMS": "1", "🗺️ MapQuest": "2", "📧 Mail.tm": "3",
                            "👥 Customer Gen": "4", "👁️ View Config": "5", "🔙 Back": "0"
                        }
                        choice = choice_map.get(choice, "0")
            else:
                # Rich fallback
                choice = enhanced_select(
                    "Select a configuration option:",
                    ["📱 DaisySMS", "🗺️ MapQuest", "📧 Mail.tm", "👥 Customer Gen", "👁️ View Config", "🔙 Back"],
                    default="🔙 Back"
                )
                choice_map = {
                    "📱 DaisySMS": "1", "🗺️ MapQuest": "2", "📧 Mail.tm": "3",
                    "👥 Customer Gen": "4", "👁️ View Config": "5", "🔙 Back": "0"
                }
                choice = choice_map.get(choice, "0")
            
            if choice == "0":
                break
            elif choice == "1":
                self._configure_daisysms()
            elif choice == "2":
                self._configure_mapquest()
            elif choice == "3":
                self._configure_mailtm()
            elif choice == "4":
                self._configure_customer_generation()
            elif choice == "5":
                self._view_current_configuration()
    
    def _configure_daisysms(self):
        """Configure DaisySMS API settings"""
        console.print("\n📱 DaisySMS API Configuration", style="bold blue")
        
        current_key = self.config_manager.get_section('DAISYSMS').get('api_key', '')
        masked_key = f"{current_key[:8]}..." if len(current_key) > 8 else "Not set"
        
        console.print(f"Current API Key: {masked_key}")
        
        if enhanced_confirm("Update DaisySMS API Key?", default=False):
            new_key = Prompt.ask("Enter new DaisySMS API Key", password=True)
            
            # Update configuration
            self.config_manager.update_config('DAISYSMS', 'api_key', new_key)
            
            # Reinitialize SMS manager
            self.sms_manager = DaisySMSManager(self.config_manager.get_section('DAISYSMS'))
            
            console.print("✅ DaisySMS API Key updated", style="green")
            
            # Test the new key
            if enhanced_confirm("Test API key and check balance?", default=True):
                try:
                    balance = self.sms_manager.get_balance()
                    console.print(f"✅ API Key valid! Balance: ${balance:.2f}", style="green")
                except Exception as e:
                    console.print(f"❌ API Key test failed: {e}", style="red")
    
    def _configure_mapquest(self):
        """Configure MapQuest API settings"""
        console.print("\n🗺️ MapQuest API Configuration", style="bold blue")
        
        current_key = self.config_manager.get_section('MAPQUEST').get('api_key', '')
        masked_key = f"{current_key[:8]}..." if len(current_key) > 8 else "Not set"
        
        console.print(f"Current API Key: {masked_key}")
        
        if enhanced_confirm("Update MapQuest API Key?", default=False):
            new_key = Prompt.ask("Enter new MapQuest API Key", password=True)
            
            # Update configuration
            self.config_manager.update_config('MAPQUEST', 'api_key', new_key)
            
            # Reinitialize MapQuest manager
            self.mapquest_manager = MapQuestAddressManager(self.config_manager.get_section('MAPQUEST'))
            
            # Update database's MapQuest manager
            self.database.mapquest_manager = self.mapquest_manager
            
            console.print("✅ MapQuest API Key updated", style="green")
            
            # Test the new key
            if enhanced_confirm("Test API key?", default=True):
                if self.mapquest_manager.test_api_connection():
                    console.print("✅ MapQuest API Key is valid!", style="green")
                else:
                    console.print("❌ MapQuest API Key test failed", style="red")
    
    def _configure_mailtm(self):
        """Configure Mail.tm settings"""
        console.print("\n📧 Mail.tm Configuration", style="bold blue")
        
        current_password = self.config_manager.get_section('MAILTM').get('default_password', '')
        current_digits = self.config_manager.get_section('MAILTM').get('email_digits', '4')
        
        console.print(f"Current default password: {current_password if current_password else 'Not set'}")
        console.print(f"Current email digits: {current_digits}")
        
        if enhanced_confirm("Update default password for email accounts?", default=False):
            new_password = Prompt.ask("Enter new default password", password=True)
            self.config_manager.update_config('MAILTM', 'default_password', new_password)
            console.print("✅ Default password updated", style="green")
        
        if enhanced_confirm("Update email random digits setting?", default=False):
            new_digits = IntPrompt.ask("Number of random digits to append to emails", default=4, choices=["2","3","4","5","6"])
            self.config_manager.update_config('MAILTM', 'email_digits', str(new_digits))
            console.print("✅ Email digits setting updated", style="green")
        
        # Reinitialize mail manager
        self.mail_manager = MailTmManager(self.config_manager.get_section('MAILTM'))
    
    def _configure_customer_generation(self):
        """Configure customer generation settings"""
        console.print("\n👥 Customer Generation Configuration", style="bold blue")
        
        current_gender = self.config_manager.get_section('CUSTOMER_GENERATION').get('gender_preference', 'both')
        
        console.print(f"Current gender preference: {current_gender}")
        
        if enhanced_confirm("Update gender preference for customer names?", default=False):
            gender_choice = Prompt.ask(
                "Select gender preference",
                choices=["male", "female", "both"],
                default="both"
            )
            
            self.config_manager.update_config('CUSTOMER_GENERATION', 'gender_preference', gender_choice)
            console.print("✅ Gender preference updated", style="green")
            
            # Update database faker settings
            if hasattr(self.database, '_configure_faker_gender'):
                self.database._configure_faker_gender(gender_choice)
    
    def _view_current_configuration(self):
        """View current configuration settings"""
        console.print("\n📋 Current Configuration", style="bold blue")
        
        # DaisySMS settings
        daisysms_config = self.config_manager.get_section('DAISYSMS')
        api_key = daisysms_config.get('api_key', '')
        
        daisysms_banner = self._create_info_banner(
            "📱 DaisySMS Configuration",
            [
                ("API Key", f"{api_key[:8]}..." if len(api_key) > 8 else "❌ Not set"),
                ("Status", "✅ Configured" if api_key else "❌ Not configured")
            ],
            "blue"
        )
        
        # MapQuest settings
        mapquest_config = self.config_manager.get_section('MAPQUEST')
        mapquest_key = mapquest_config.get('api_key', '')
        
        mapquest_banner = self._create_info_banner(
            "🗺️ MapQuest Configuration",
            [
                ("API Key", f"{mapquest_key[:8]}..." if len(mapquest_key) > 8 else "❌ Not set"),
                ("Status", "✅ Configured" if mapquest_key else "❌ Not configured")
            ],
            "magenta"
        )
        
        # Mail.tm settings
        mailtm_config = self.config_manager.get_section('MAILTM')
        password = mailtm_config.get('default_password', '')
        digits = mailtm_config.get('email_digits', '4')
        
        mailtm_banner = self._create_info_banner(
            "📧 Mail.tm Configuration",
            [
                ("Default Password", password if password else "❌ Not set"),
                ("Email Random Digits", digits),
                ("Status", "✅ Configured" if password else "❌ Not configured")
            ],
            "green"
        )
        
        # Customer generation settings
        customer_config = self.config_manager.get_section('CUSTOMER_GENERATION')
        gender = customer_config.get('gender_preference', 'both')
        
        customer_banner = self._create_info_banner(
            "👥 Customer Generation",
            [
                ("Gender Preference", gender.title()),
                ("Status", "✅ Configured")
            ],
            "cyan"
        )
        
        # Display all configuration banners
        console.print(daisysms_banner)
        console.print(mapquest_banner)
        console.print(mailtm_banner)
        console.print(customer_banner)
        
        # Interactive configuration options
        console.print("\n⚙️ Quick Actions", style="bold cyan")
        console.print("═" * 50, style="cyan")
        
        if RICH_AVAILABLE:
            options_text = """1. Edit DaisySMS API Key
2. Edit MapQuest API Key  
3. Edit Mail.tm Password
4. Edit Email Random Digits
5. Edit Customer Gender Preference
6. Test API Connections
0. Back to Configuration Menu"""
            
            options_panel = Panel(
                options_text,
                title="Quick Configuration",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(options_panel)
        else:
            console.print("1. Edit DaisySMS API Key")
            console.print("2. Edit MapQuest API Key") 
            console.print("3. Edit Mail.tm Password")
            console.print("4. Edit Email Random Digits")
            console.print("5. Edit Customer Gender Preference")
            console.print("6. Test API Connections")
            console.print("0. Back to Configuration Menu")
        
        choice = Prompt.ask("\nSelect quick action", choices=["0","1","2","3","4","5","6"], default="0")
        
        if choice == "1":
            self._quick_edit_daisysms_api()
        elif choice == "2":
            self._quick_edit_mapquest_api()
        elif choice == "3":
            self._quick_edit_mailtm_password()
        elif choice == "4":
            self._quick_edit_email_digits()
        elif choice == "5":
            self._quick_edit_gender_preference()
        elif choice == "6":
            self._test_api_connections()
        
        # Return to view config if user made changes
        if choice in ["1", "2", "3", "4", "5"]:
            console.print("\n🔄 Configuration updated! Showing updated view...", style="green")
            time.sleep(1)
            self._view_current_configuration()
    
    def _quick_edit_daisysms_api(self):
        """Quick edit DaisySMS API key"""
        current_key = self.config_manager.get_section('DAISYSMS').get('api_key', '')
        console.print(f"\n📱 Edit DaisySMS API Key", style="bold blue")
        console.print(f"Current: {current_key[:8]}..." if len(current_key) > 8 else f"Current: {current_key}")
        
        new_key = Prompt.ask("Enter new DaisySMS API Key (or press Enter to keep current)", default=current_key)
        
        if new_key != current_key:
            self.config_manager.update_config('DAISYSMS', 'api_key', new_key)
            self.sms_manager = DaisySMSManager(self.config_manager.get_section('DAISYSMS'))
            console.print("✅ DaisySMS API Key updated successfully!", style="green")
            
            # Test the new key
            if enhanced_confirm("Test new API key?", default=True):
                try:
                    balance = self.sms_manager.get_balance()
                    console.print(f"✅ API Key valid! Balance: ${balance:.2f}", style="green")
                except Exception as e:
                    console.print(f"❌ API Key test failed: {str(e)[:50]}...", style="red")
        else:
            console.print("No changes made.", style="dim")
    
    def _quick_edit_mapquest_api(self):
        """Quick edit MapQuest API key"""
        current_key = self.config_manager.get_section('MAPQUEST').get('api_key', '')
        console.print(f"\n🗺️ Edit MapQuest API Key", style="bold blue")
        console.print(f"Current: {current_key[:8]}..." if len(current_key) > 8 else f"Current: {current_key}")
        
        new_key = Prompt.ask("Enter new MapQuest API Key (or press Enter to keep current)", default=current_key)
        
        if new_key != current_key:
            self.config_manager.update_config('MAPQUEST', 'api_key', new_key)
            self.mapquest_manager = MapQuestAddressManager(self.config_manager.get_section('MAPQUEST'))
            self.database.mapquest_manager = self.mapquest_manager
            console.print("✅ MapQuest API Key updated successfully!", style="green")
            
            # Test the new key
            if enhanced_confirm("Test new API key?", default=True):
                if self.mapquest_manager.test_api_connection():
                    console.print("✅ MapQuest API Key is valid!", style="green")
                else:
                    console.print("❌ MapQuest API Key test failed", style="red")
        else:
            console.print("No changes made.", style="dim")
    
    def _quick_edit_mailtm_password(self):
        """Quick edit Mail.tm password"""
        current_password = self.config_manager.get_section('MAILTM').get('default_password', '')
        console.print(f"\n📧 Edit Mail.tm Default Password", style="bold blue")
        console.print(f"Current: {current_password}")
        
        new_password = Prompt.ask("Enter new default password (or press Enter to keep current)", default=current_password)
        
        if new_password != current_password:
            # Update configuration
            self.config_manager.update_config('MAILTM', 'default_password', new_password)
            
            # Update the Mail.tm manager password directly
            try:
                self.mail_manager.update_password(new_password)
                console.print("✅ Mail.tm password updated successfully!", style="green")
                console.print(f"✅ New password: {new_password}", style="green")
                self.logger.info(f"Mail.tm password updated to: {new_password}")
            except Exception as e:
                console.print(f"❌ Error updating Mail.tm manager password: {e}", style="red")
                self.logger.error(f"Error updating Mail.tm manager password: {e}")
        else:
            console.print("No changes made.", style="dim")
    
    def _quick_edit_email_digits(self):
        """Quick edit email random digits"""
        current_digits = self.config_manager.get_section('MAILTM').get('email_digits', '4')
        console.print(f"\n📧 Edit Email Random Digits", style="bold blue")
        console.print(f"Current: {current_digits} digits")
        
        new_digits = IntPrompt.ask(
            "Number of random digits to append to emails", 
            default=int(current_digits), 
            choices=["2","3","4","5","6"]
        )
        
        if str(new_digits) != current_digits:
            self.config_manager.update_config('MAILTM', 'email_digits', str(new_digits))
            self.mail_manager = MailTmManager(self.config_manager.get_section('MAILTM'))
            console.print("✅ Email digits setting updated successfully!", style="green")
        else:
            console.print("No changes made.", style="dim")
    
    def _quick_edit_gender_preference(self):
        """Quick edit customer gender preference"""
        current_gender = self.config_manager.get_section('CUSTOMER_GENERATION').get('gender_preference', 'both')
        console.print(f"\n👥 Edit Customer Gender Preference", style="bold blue")
        console.print(f"Current: {current_gender.title()}")
        
        new_gender = Prompt.ask(
            "Select gender preference",
            choices=["male", "female", "both"],
            default=current_gender
        )
        
        if new_gender != current_gender:
            self.config_manager.update_config('CUSTOMER_GENERATION', 'gender_preference', new_gender)
            console.print("✅ Gender preference updated successfully!", style="green")
            
            # Update database faker settings
            if hasattr(self.database, '_configure_faker_gender'):
                self.database._configure_faker_gender(new_gender)
        else:
            console.print("No changes made.", style="dim")
    
    def _test_api_connections(self):
        """Test all API connections"""
        console.print("\n🔍 Testing API Connections...", style="bold yellow")
        console.print("=" * 50, style="yellow")
        
        # Test DaisySMS
        console.print("\n📱 Testing DaisySMS...", style="blue")
        try:
            balance = self.sms_manager.get_balance()
            console.print(f"✅ DaisySMS: Connected (Balance: ${balance:.2f})", style="green")
        except Exception as e:
            console.print(f"❌ DaisySMS: Failed ({str(e)[:50]}...)", style="red")
        
        # Test MapQuest
        console.print("\n🗺️ Testing MapQuest...", style="blue")
        if self.mapquest_manager.test_api_connection():
            console.print("✅ MapQuest: Connected", style="green")
        else:
            console.print("❌ MapQuest: Failed", style="red")
        
        # Test Mail.tm (basic domain availability check)
        console.print("\n📧 Testing Mail.tm...", style="blue")
        try:
            domains = self.mail_manager.get_available_domains()
            if domains:
                console.print(f"✅ Mail.tm: Connected ({len(domains)} domains available)", style="green")
            else:
                console.print("⚠️ Mail.tm: Connected but no domains available", style="yellow")
        except Exception as e:
            console.print(f"❌ Mail.tm: Failed ({str(e)[:50]}...)", style="red")
        
        console.print(f"\n📊 Connection Test Complete", style="bold cyan")
        input("\nPress Enter to continue...")


def test_questionary():
    """Test questionary functionality"""
    try:
        import questionary
        from questionary import Choice
        
        print("🧪 Testing Questionary Arrow-Key Interface")
        print("=" * 50)
        
        # Check terminal compatibility
        import sys
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print("❌ Non-interactive terminal detected")
            return
        
        choices = [
            Choice("🌸 Test Option 1", value="1"),
            Choice("📱 Test Option 2", value="2"),
            Choice("🚪 Exit Test", value="0")
        ]
        
        print("💡 Use arrow keys to navigate, Enter to select")
        print()
        
        selection = questionary.select(
            "Select a test option:",
            choices=choices,
            use_shortcuts=True
        ).ask()
        
        if selection:
            print(f"\n✅ Selection successful: {selection}")
        else:
            print("\n❌ No selection made")
            
    except Exception as e:
        print(f"❌ Questionary test failed: {type(e).__name__}: {e}")


def main():
    """Application entry point"""
    # Quick test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test-questionary":
        test_questionary()
        return 0
    
    app = CustomerDaisyApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()