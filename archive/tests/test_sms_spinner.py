#!/usr/bin/env python3
"""
Test SMS Verification Spinner
==============================
Test the live SMS verification spinner functionality
"""

import time
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console()

def test_sms_spinner():
    """Test the SMS verification spinner"""
    console.print("🧪 Testing SMS Verification Spinner", style="bold cyan")
    console.print("This will simulate the SMS verification process", style="blue")
    console.print("Press Ctrl+C to stop the test", style="dim")
    
    received_codes = []
    
    try:
        with Live(console=console, refresh_per_second=2) as live:
            start_time = time.time()
            attempt = 0
            
            for i in range(20):  # Simulate 20 attempts
                attempt += 1
                elapsed = time.time() - start_time
                
                # Create status display
                status_text = Text()
                status_text.append("🔄 Checking for SMS codes...\n", style="cyan")
                status_text.append(f"⏱️  Elapsed: {elapsed:.0f}s | Attempt: {attempt}\n", style="dim")
                status_text.append(f"📱 Phone: +1234567890\n", style="blue")
                
                if received_codes:
                    status_text.append(f"✅ Codes received: {len(received_codes)}\n", style="green")
                    for idx, code_data in enumerate(received_codes, 1):
                        status_text.append(f"   Code {idx}: {code_data['code']} (at {code_data['timestamp']})\n", style="white")
                else:
                    status_text.append("⏳ No codes received yet...\n", style="yellow")
                
                live.update(status_text)
                
                # Simulate receiving a code after 10 seconds
                if elapsed > 10 and not received_codes:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    code_data = {
                        'code': '123456',
                        'timestamp': timestamp,
                        'received_at': datetime.now().isoformat()
                    }
                    received_codes.append(code_data)
                    
                    # Show success message
                    live.stop()
                    console.print(f"\n🎉 Test SMS Code Received!", style="bold green")
                    console.print(f"📱 Code: [bold green]{code_data['code']}[/bold green]", style="white")
                    console.print(f"🕐 Time: {timestamp}", style="blue")
                    break
                
                time.sleep(1)
    
    except KeyboardInterrupt:
        console.print("\n🛑 Test stopped by user", style="yellow")
    
    console.print("\n✅ SMS Spinner test completed!", style="green")

if __name__ == "__main__":
    test_sms_spinner() 