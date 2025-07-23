#!/usr/bin/env python3
"""
Test script to simulate the exact SMS code clipboard scenario reported by user
"""

import sys
import time
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the rich console and related modules from main
try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import clipboard functionality
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

console = Console(force_terminal=True, width=120) if RICH_AVAILABLE else None

def _copy_to_clipboard_manual_test(text: str, description: str = "text"):
    """Test version of the improved clipboard copy function"""
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
                    if console:
                        console.print(f"✅ {description} copied to clipboard: {text}", style="green")
                    else:
                        print(f"✅ {description} copied to clipboard: {text}")
                    return True
                elif attempt < max_retries - 1:
                    time.sleep(0.2)  # Wait longer before retry
                    pyperclip.copy(text)  # Retry copy
                
            if console:
                console.print(f"❌ Clipboard copy verification failed for {description} after {max_retries} attempts", style="red")
                console.print(f"Expected: {text}", style="dim")
                console.print(f"Got: {test_paste}", style="dim")
            else:
                print(f"❌ Clipboard copy verification failed for {description} after {max_retries} attempts")
                
        except Exception as e:
            if console:
                console.print(f"❌ Clipboard error for {description}: {str(e)}", style="red")
            else:
                print(f"❌ Clipboard error for {description}: {str(e)}")
            
            # Try Windows-specific fallback
            try:
                import subprocess
                import platform
                if platform.system() == "Windows":
                    # Use Windows clip command as fallback
                    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, text=True)
                    process.communicate(input=text)
                    if process.returncode == 0:
                        if console:
                            console.print(f"✅ {description} copied to clipboard using Windows clip: {text}", style="green")
                        else:
                            print(f"✅ {description} copied to clipboard using Windows clip: {text}")
                        return True
            except Exception as fallback_e:
                if console:
                    console.print(f"❌ Windows clip fallback also failed: {fallback_e}", style="red")
                else:
                    print(f"❌ Windows clip fallback also failed: {fallback_e}")
    else:
        if console:
            console.print(f"❌ Clipboard not available - manual copy: {text}", style="yellow")
        else:
            print(f"❌ Clipboard not available - manual copy: {text}")
    
    return False

def simulate_sms_code_scenario():
    """Simulate the exact SMS code scenario from the user's report"""
    print("🔍 Simulating: Checking DaisySMS API...")
    
    # The SMS code from user's report
    code = "890402"
    
    if RICH_AVAILABLE and console:
        # Create the same panel structure as in the app
        same_code_panel = Panel.fit(
            f"📱 Code: {code}\n\n"
            f"ℹ️ This is the same code as your last check\n"
            f"💡 Code has been copied to clipboard again",
            title="📱 Same SMS Code",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print(same_code_panel)
        
        # Try to copy to clipboard using improved method
        _copy_to_clipboard_manual_test(code, "SMS code")
        
    else:
        print("📱 Same SMS Code")
        print("─" * 50)
        print(f"📱 Code: {code}")
        print()
        print("ℹ️ This is the same code as your last check")
        print("💡 Code has been copied to clipboard again")
        print("─" * 50)
        
        # Try to copy to clipboard using improved method
        _copy_to_clipboard_manual_test(code, "SMS code")
    
    # Give user a chance to manually test
    print("\n" + "=" * 60)
    print("🧪 MANUAL VERIFICATION TEST")
    print("=" * 60)
    print("Please test the clipboard now:")
    print("1. Open any text editor (Notepad, VS Code, etc.)")
    print("2. Press Ctrl+V to paste")
    print(f"3. You should see: {code}")
    print("4. Press Enter here when you've tested...")
    
    try:
        input()  # Wait for user input
        print("Thank you for testing!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    return True

def main():
    """Main test function"""
    print("🧪 SMS Code Clipboard Test")
    print("=" * 50)
    print(f"Rich available: {RICH_AVAILABLE}")
    print(f"Clipboard available: {CLIPBOARD_AVAILABLE}")
    print()
    
    if not CLIPBOARD_AVAILABLE:
        print("❌ Cannot run test - pyperclip not available")
        return False
    
    # Run the simulation
    result = simulate_sms_code_scenario()
    
    print("\n" + "=" * 50)
    if result:
        print("✅ Test completed. Please verify clipboard manually above.")
    else:
        print("❌ Test failed.")
    print("=" * 50)
    
    return result

if __name__ == "__main__":
    main()