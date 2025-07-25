#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DaisySMS Integration Module
==========================
Complete DaisySMS API integration for phone verification services.
Based on official API documentation: https://daisysms.com/docs/api
"""

import requests
import time
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from rich.console import Console

console = Console()

class DaisySMSManager:
    """DaisySMS API Manager for phone verification services with caching"""
    
    def __init__(self, config: Dict[str, str]):
        """Initialize DaisySMS manager with configuration"""
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', 'https://daisysms.com/stubs/handler_api.php')
        self.service_code = config.get('service_code', 'ds')  # Default to Discord
        self.max_price = float(config.get('max_price', '0.50'))
        self.verification_timeout = int(config.get('verification_timeout', '180'))
        self.polling_interval = int(config.get('polling_interval', '3'))
        
        self.session = requests.Session()
        self.session.timeout = 30
        self.active_verifications = {}
        
        # Caching for performance
        self._balance_cache = None
        self._balance_cache_time = None
        self._cache_ttl = 60  # Cache balance for 60 seconds
        
        # Add headers for requests
        self.session.headers.update({
            'User-Agent': 'CustomerDaisy/1.0.0',
            'Accept': 'text/plain, */*'
        })
    
    def _make_request(self, action: str, params: Dict = None) -> Dict:
        """Make API request to DaisySMS following official API format"""
        request_params = {
            'api_key': self.api_key,
            'action': action
        }
        
        if params:
            request_params.update(params)
        
        try:
            response = self.session.get(self.base_url, params=request_params)
            response.raise_for_status()
            
            # DaisySMS returns text responses, not JSON
            text_response = response.text.strip()
            
            # Check for X-Text header if text=1 was used
            full_message_text = response.headers.get('X-Text', '')
            
            # Log the full response details for debugging
            result_dict = {
                'raw_response': text_response,
                'full_message_text': full_message_text,
                'headers': dict(response.headers)
            }
            
            # Parse response based on format from API docs
            if ':' in text_response:
                parts = text_response.split(':', 1)
                status = parts[0]
                data = parts[1] if len(parts) > 1 else None
                
                # Handle multi-part responses like ACCESS_NUMBER:999999:13476711222
                if status == 'ACCESS_NUMBER' and data and ':' in data:
                    data_parts = data.split(':')
                    result_dict.update({
                        'status': status,
                        'id': data_parts[0],
                        'number': data_parts[1] if len(data_parts) > 1 else None
                    })
                    return result_dict
                
                # Handle SMS code responses that might be in different formats
                # DaisySMS might return codes like "STATUS_OK:123456" or "OK:123456"
                # Also handle alternative formats like "READY:123456" or "ACCESS_ACTIVATION:123456"
                if data and data.split(':')[0].isdigit():
                    # Extract the numeric code (first part after colon)
                    code_part = data.split(':')[0]
                    if len(code_part) >= 4:  # Valid SMS codes are usually 4+ digits
                        result_dict.update({
                            'status': 'STATUS_OK',
                            'data': code_part
                        })
                        return result_dict
                
                result_dict.update({
                    'status': status,
                    'data': data
                })
                return result_dict
            
            # Single value responses (like balance or simple status)
            # Check if this might be a direct SMS code (numeric, 4+ digits)
            if text_response.isdigit() and len(text_response) >= 4:
                result_dict.update({
                    'status': 'STATUS_OK',
                    'data': text_response
                })
                return result_dict
            
            # If we have full message text in header, try to extract code from it
            if full_message_text:
                # Look for numeric codes in the message text (4-8 digits)
                import re
                code_matches = re.findall(r'\b\d{4,8}\b', full_message_text)
                if code_matches:
                    # Use the first code found
                    result_dict.update({
                        'status': 'STATUS_OK',
                        'data': code_matches[0],
                        'extracted_from': 'X-Text header'
                    })
                    return result_dict
            
            result_dict.update({
                'status': text_response,
                'data': None
            })
            return result_dict
            
        except requests.RequestException as e:
            console.print(f"❌ API request failed: {e}", style="red")
            return {'status': 'error', 'message': str(e)}
        except Exception as e:
            console.print(f"❌ Request error: {e}", style="red")
            return {'status': 'error', 'message': str(e)}
    
    def get_balance(self) -> float:
        """Get account balance with caching"""
        # Check cache first
        if (self._balance_cache is not None and 
            self._balance_cache_time is not None and
            time.time() - self._balance_cache_time < self._cache_ttl):
            return self._balance_cache
        
        response = self._make_request('getBalance')
        
        if response.get('status') == 'ACCESS_BALANCE':
            try:
                balance = float(response.get('data', '0'))
                # Cache the result
                self._balance_cache = balance
                self._balance_cache_time = time.time()
                return balance
            except (ValueError, TypeError):
                console.print(f"❌ Invalid balance format: {response.get('data')}", style="red")
                return 0.0
        elif response.get('status') == 'BAD_KEY':
            console.print("❌ Invalid API key", style="red")
            return 0.0
        else:
            console.print(f"❌ Failed to get balance: {response.get('raw_response', 'Unknown error')}", style="red")
            return 0.0
    
    def get_pricing_info(self, service: str = None, country: int = 0) -> Dict:
        """Get pricing information for services"""
        service_code = service or self.service_code
        
        # Get the actual service info from our services list
        services = self.get_services_list()
        service_info = next((s for s in services if s['code'] == service_code), None)
        
        if service_info:
            actual_price = service_info['price']
            service_name = service_info['name']
        else:
            actual_price = 0.05  # Default price
            service_name = "Unknown Service"
        
        # Try to get real pricing from API (this would be complex to parse)
        response = self._make_request('getPricesVerification')
        
        return {
            'service': service_code,
            'service_name': service_name,
            'country': country,
            'price': actual_price,
            'max_price': self.max_price,
            'count': 100,  # Assume availability
            'available': True
        }
    
    def rent_number(self, service: str = None, country: int = 0, max_price: float = None) -> Optional[Dict[str, str]]:
        """Rent a phone number for verification following official API"""
        service_code = service or self.service_code
        max_price = max_price or self.max_price
        
        # Check balance first
        balance = self.get_balance()
        if balance < max_price:
            console.print(f"❌ Insufficient balance: ${balance:.2f} < ${max_price:.2f}", style="red")
            return None
        
        # Prepare request parameters
        params = {
            'service': service_code,
            'max_price': max_price
        }
        
        # Add country if specified (0 = USA)
        if country != 0:
            params['country'] = country
        
        console.print(f"🔄 Renting number for service '{service_code}' with max price ${max_price:.2f}...", style="blue")
        
        # Rent the number
        response = self._make_request('getNumber', params)
        
        if response.get('status') == 'ACCESS_NUMBER':
            # Extract ID and number from response
            verification_id = response.get('id')
            phone_number = response.get('number')
            
            if verification_id and phone_number:
                # Store verification info
                verification_info = {
                    'verification_id': verification_id,
                    'phone_number': phone_number,
                    'service': service_code,
                    'country': country,
                    'max_price': max_price,
                    'status': 'rented',
                    'created_at': datetime.now(),
                    'timeout_at': datetime.now() + timedelta(seconds=self.verification_timeout)
                }
                
                self.active_verifications[verification_id] = verification_info
                
                console.print(f"✅ Number rented: {phone_number} (ID: {verification_id})", style="green")
                return verification_info
            else:
                console.print(f"❌ Invalid response format: {response.get('raw_response')}", style="red")
                return None
        
        elif response.get('status') == 'MAX_PRICE_EXCEEDED':
            console.print(f"❌ Max price exceeded for service '{service_code}'", style="red")
            return None
        
        elif response.get('status') == 'NO_NUMBERS':
            console.print(f"❌ No numbers available for service '{service_code}'", style="red")
            return None
        
        elif response.get('status') == 'TOO_MANY_ACTIVE_RENTALS':
            console.print("❌ Too many active rentals (max 20)", style="red")
            return None
        
        elif response.get('status') == 'NO_MONEY':
            console.print("❌ Insufficient balance", style="red")
            return None
        
        else:
            error_msg = response.get('raw_response', 'Unknown error')
            console.print(f"❌ Failed to rent number: {error_msg}", style="red")
            return None
    
    def get_sms_code(self, verification_id: str, max_attempts: int = 40, silent: bool = False) -> Optional[str]:
        """Get SMS verification code with polling following official API"""
        if verification_id not in self.active_verifications:
            if not silent:
                console.print(f"❌ Unknown verification ID: {verification_id}", style="red")
            return None
        
        verification_info = self.active_verifications[verification_id]
        
        # Check if verification is already cancelled or completed
        if verification_info.get('status') == 'cancelled':
            if not silent:
                console.print(f"❌ Verification already cancelled: {verification_id}", style="red")
            return None
        
        if verification_info.get('status') == 'completed':
            # Return existing SMS code if already received
            existing_code = verification_info.get('sms_code')
            if existing_code:
                if not silent:
                    console.print(f"✅ SMS code (already received): {existing_code}", style="green")
                return existing_code
        
        if not silent:
            console.print(f"🔍 Polling for SMS code (ID: {verification_id})...", style="blue")
        
        for attempt in range(max_attempts):
            # Check timeout (only if timeout_at is set properly)
            timeout_at = verification_info.get('timeout_at')
            if timeout_at and datetime.now() > timeout_at:
                if not silent:
                    console.print(f"⏰ Verification timeout for ID: {verification_id}", style="yellow")
                self.cancel_verification(verification_id)
                return None
            
            # Request SMS status with text parameter to get full message
            response = self._make_request('getStatus', {'id': verification_id, 'text': '1'})
            
            # Debug: Show detailed response info if not silent
            if not silent:
                console.print(f"📜 API Response: {response.get('raw_response', 'No raw response')}", style="dim")
                if response.get('full_message_text'):
                    console.print(f"📄 Full Message: {response.get('full_message_text')}", style="cyan")
                if response.get('extracted_from'):
                    console.print(f"🔍 Code extracted from: {response.get('extracted_from')}", style="yellow")
            
            if response.get('status') == 'STATUS_OK':
                # SMS code received
                sms_code = response.get('data')
                if sms_code:
                    verification_info['status'] = 'completed'
                    verification_info['sms_code'] = sms_code
                    verification_info['completed_at'] = datetime.now()
                    
                    if not silent:
                        console.print(f"✅ SMS code received: {sms_code}", style="green")
                    
                    # Mark as done to free up the rental
                    self.mark_verification_done(verification_id, silent=silent)
                    
                    return sms_code
            
            elif response.get('status') == 'STATUS_WAIT_CODE':
                # Still waiting for SMS (correct status from API docs)
                if not silent and attempt % 10 == 0:  # Show progress every 10 attempts
                    console.print(f"⏳ Waiting for SMS... (attempt {attempt + 1}/{max_attempts})", style="blue")
                time.sleep(self.polling_interval)
                continue
            
            elif response.get('status') == 'STATUS_CANCEL':
                # Verification cancelled
                if not silent:
                    console.print(f"❌ Verification cancelled: {verification_id}", style="red")
                verification_info['status'] = 'cancelled'
                return None
            
            elif response.get('status') == 'NO_ACTIVATION':
                # Wrong ID or already processed
                if not silent:
                    console.print(f"❌ Invalid activation ID: {verification_id}", style="red")
                return None
            
            else:
                # Other status or error - show more detail
                error_msg = response.get('raw_response', 'Unknown status')
                parsed_status = response.get('status', 'Unknown')
                parsed_data = response.get('data', 'None')
                
                if not silent and attempt % 10 == 0:  # Show errors every 10 attempts
                    console.print(f"⚠️ Status: {parsed_status} | Data: {parsed_data} | Raw: {error_msg}", style="yellow")
                
                # Check if this might be a different SMS code format
                if ':' in error_msg:
                    # This might be an SMS code in different format
                    if not silent:
                        console.print(f"🔍 Possible SMS code in different format: {error_msg}", style="cyan")
                    
                    # Try to extract code from raw response
                    parts = error_msg.split(':')
                    if len(parts) >= 2:
                        potential_code = parts[1].split(':')[0].strip()  # Get first part after colon
                        if potential_code.isdigit() and len(potential_code) >= 4:
                            verification_info['status'] = 'completed'
                            verification_info['sms_code'] = potential_code
                            verification_info['completed_at'] = datetime.now()
                            
                            if not silent:
                                console.print(f"✅ SMS code extracted: {potential_code}", style="green")
                            
                            # Mark as done to free up the rental
                            self.mark_verification_done(verification_id, silent=silent)
                            
                            return potential_code
                
                # Also check if the status itself might be a code (direct numeric response)
                elif parsed_status.isdigit() and len(parsed_status) >= 4:
                    verification_info['status'] = 'completed'
                    verification_info['sms_code'] = parsed_status
                    verification_info['completed_at'] = datetime.now()
                    
                    if not silent:
                        console.print(f"✅ SMS code from status: {parsed_status}", style="green")
                    
                    # Mark as done to free up the rental
                    self.mark_verification_done(verification_id, silent=silent)
                    
                    return parsed_status
                
                time.sleep(self.polling_interval)
        
        # Max attempts reached - only cancel if this was a serious attempt (not a single check)
        if verification_info.get('status') != 'cancelled':
            if max_attempts > 1:  # Only cancel if this was a multi-attempt operation
                if not silent:
                    console.print(f"❌ Max attempts reached for verification ID: {verification_id}", style="red")
                self.cancel_verification(verification_id)
            else:
                if not silent:
                    console.print(f"⏳ No SMS received on single check for ID: {verification_id}", style="yellow")
        
        return None
    
    def mark_verification_done(self, verification_id: str, silent: bool = False) -> bool:
        """Mark rental as done (status 6) to free up the number"""
        response = self._make_request('setStatus', {
            'id': verification_id,
            'status': '6'  # Done status
        })
        
        if response.get('status') == 'ACCESS_ACTIVATION':
            if not silent:
                console.print(f"✅ Verification marked as done: {verification_id}", style="green")
            return True
        else:
            if not silent:
                console.print(f"⚠️ Could not mark as done: {response.get('raw_response')}", style="yellow")
            return False
    
    def cancel_verification(self, verification_id: str) -> bool:
        """Cancel a verification and get refund (status 8)"""
        if verification_id not in self.active_verifications:
            console.print(f"❌ Unknown verification ID: {verification_id}", style="red")
            return False
        
        # Check if already cancelled
        if self.active_verifications[verification_id].get('status') == 'cancelled':
            console.print(f"⚠️ Verification already cancelled: {verification_id}", style="yellow")
            return True
        
        response = self._make_request('setStatus', {
            'id': verification_id,
            'status': '8'  # Cancel status
        })
        
        if response.get('status') == 'ACCESS_CANCEL':
            self.active_verifications[verification_id]['status'] = 'cancelled'
            self.active_verifications[verification_id]['cancelled_at'] = datetime.now()
            console.print(f"✅ Verification cancelled and refunded: {verification_id}", style="green")
            return True
        elif response.get('status') == 'ACCESS_READY':
            console.print(f"⚠️ Verification already processed: {verification_id}", style="yellow")
            return False
        else:
            error_msg = response.get('raw_response', 'Unknown error')
            console.print(f"❌ Failed to cancel verification: {error_msg}", style="red")
            return False
    
    def keep_number(self, verification_id: str) -> bool:
        """Keep a number without receiving a message (pay as if received)"""
        response = self._make_request('keep', {'id': verification_id})
        
        if response.get('status') == 'OK':
            console.print(f"✅ Number kept: {verification_id}", style="green")
            return True
        else:
            console.print(f"❌ Failed to keep number: {response.get('raw_response')}", style="red")
            return False
    
    def create_verification(self, service: str = None, country: int = 0) -> Optional[Dict[str, str]]:
        """Complete workflow: rent number and prepare for SMS"""
        verification = self.rent_number(service, country)
        if verification:
            console.print(f"📱 Phone number ready: {verification['phone_number']}", style="green")
            console.print(f"🆔 Verification ID: {verification['verification_id']}", style="blue")
            return verification
        return None
    
    def get_verification_code(self, verification_id: str, max_attempts: int = 40, silent: bool = False) -> Optional[str]:
        """Get SMS verification code for existing verification"""
        # Check if verification exists and is not cancelled
        if verification_id not in self.active_verifications:
            if not silent:
                console.print(f"❌ Unknown verification ID: {verification_id}", style="red")
            return None
        
        verification_info = self.active_verifications[verification_id]
        if verification_info.get('status') == 'cancelled':
            if not silent:
                console.print(f"❌ Cannot get SMS code - verification was cancelled: {verification_id}", style="red")
            return None
        
        return self.get_sms_code(verification_id, max_attempts, silent)
    
    def cleanup_expired_verifications(self):
        """Clean up expired verifications"""
        current_time = datetime.now()
        expired_ids = []
        
        for vid, info in self.active_verifications.items():
            if current_time > info['timeout_at'] and info['status'] not in ['completed', 'cancelled']:
                expired_ids.append(vid)
        
        for vid in expired_ids:
            console.print(f"🧹 Cleaning up expired verification: {vid}", style="yellow")
            self.cancel_verification(vid)
    
    def get_status_summary(self) -> Dict:
        """Get summary of current status"""
        balance = self.get_balance()
        active_count = len([v for v in self.active_verifications.values() if v['status'] == 'rented'])
        completed_count = len([v for v in self.active_verifications.values() if v['status'] == 'completed'])
        
        return {
            "balance": balance,
            "active_verifications": active_count,
            "completed_verifications": completed_count,
            "total_verifications": len(self.active_verifications),
            "last_verification": max([v['created_at'] for v in 
                self.active_verifications.values()], default=None),
            "api_key_status": "active" if self.api_key else "missing"
        }

    def test_api_connection(self) -> bool:
        """Test DaisySMS API connection and credentials"""
        try:
            balance = self.get_balance()
            if balance >= 0:
                console.print(f"✅ API connection successful - Balance: ${balance:.2f}", style="green")
                return True
            else:
                console.print("❌ API connection failed - Invalid response", style="red")
                return False
        except Exception as e:
            console.print(f"❌ API connection failed: {e}", style="red")
            return False

    def get_services_list(self) -> List[Dict]:
        """Get list of available services (based on real DaisySMS API data)"""
        # Services based on actual DaisySMS API response
        return [
            {'code': 'ac', 'name': 'DoorDash', 'price': 0.05},  # CORRECT: ac = DoorDash  
            {'code': 'ub', 'name': 'Uber', 'price': 0.08},
            {'code': 'tu', 'name': 'Lyft', 'price': 0.08},
            {'code': 'ds', 'name': 'Discord', 'price': 0.05},
            {'code': 'go', 'name': 'Google', 'price': 0.08},
            {'code': 'tg', 'name': 'Telegram', 'price': 0.03},
            {'code': 'wa', 'name': 'WhatsApp', 'price': 0.12},
            {'code': 'fb', 'name': 'Facebook', 'price': 0.10},
            {'code': 'ig', 'name': 'Instagram', 'price': 0.08},
            {'code': 'tw', 'name': 'Twitter', 'price': 0.15},
            {'code': 'li', 'name': 'LinkedIn', 'price': 0.20}
        ]

    def get_available_services(self) -> Dict:
        """Get available services as a dictionary (alias for compatibility)"""
        services_list = self.get_services_list()
        return {service['code']: service for service in services_list}
