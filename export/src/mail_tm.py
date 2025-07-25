#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mail.tm Manager - Temporary Email Service Integration
====================================================
Handles Mail.tm API interactions for temporary email creation.
"""

import requests
import random
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

try:
    from rich.console import Console
    console = Console()
except ImportError:
    class Console:
        def print(self, *args, **kwargs): print(*args)
    console = Console()

class MailTmManager:
    """Mail.tm API integration for temporary email accounts"""
    
    def __init__(self, config: Dict):
        """Initialize Mail.tm manager with configuration"""
        self.base_url = config.get('base_url', 'https://api.mail.tm')
        self.password = config.get('default_password', 'Astral007$')  # Use configured default password
        self.domain_cache_duration = int(config.get('domain_cache_duration', 3600))
        
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Cache for available domains
        self._domain_cache = None
        self._domain_cache_time = None
        
        console.print(f"📧 Mail.tm Manager initialized with password: {self.password}", style="green")
    
    def update_password(self, new_password: str):
        """Update the default password for new account creation"""
        old_password = self.password
        self.password = new_password
        console.print(f"📧 Mail.tm password updated from '{old_password}' to '{new_password}'", style="blue")
        self.logger.info(f"Mail.tm password updated from '{old_password}' to '{new_password}'")
    
    def get_available_domains(self) -> list:
        """Get all available Mail.tm domains"""
        try:
            # Fetch available domains
            response = self.session.get(f"{self.base_url}/domains")
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            domains_data = response.json()
            
            if not domains_data.get("hydra:member"):
                return []
            
            # Return all available domains
            return [domain["domain"] for domain in domains_data["hydra:member"]]
        
        except requests.RequestException as e:
            raise Exception(f"Network error getting domains: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid domain response format: {e}")

    def get_available_domain(self) -> str:
        """Get an available Mail.tm domain with caching"""
        try:
            # Check if we have a valid cached domain
            if (self._domain_cache and self._domain_cache_time and 
                datetime.now() - self._domain_cache_time < timedelta(seconds=self.domain_cache_duration)):
                return self._domain_cache
            
            # Fetch available domains
            response = self.session.get(f"{self.base_url}/domains")
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            domains_data = response.json()
            
            if not domains_data.get("hydra:member"):
                raise Exception("No available domains found")
            
            # Get the first available domain
            domain = domains_data["hydra:member"][0]["domain"]
            
            # Cache the domain
            self._domain_cache = domain
            self._domain_cache_time = datetime.now()
            
            self.logger.debug(f"Using Mail.tm domain: {domain}")
            return domain
        
        except requests.RequestException as e:
            raise Exception(f"Network error getting domains: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid domain response format: {e}")
    
    def generate_username(self, first_name: str, last_name: str) -> str:
        """Generate a unique username based on name"""
        # Create base username: first initial + last name
        base_username = f"{first_name[0].lower()}{last_name.lower()}"
        
        # Add random number for uniqueness
        random_suffix = random.randint(100, 999)
        
        # Clean the username (remove non-alphanumeric characters)
        clean_username = ''.join(c for c in base_username if c.isalnum())
        
        return f"{clean_username}{random_suffix}"
    
    def create_account(self, first_name: str, last_name: str) -> Dict[str, str]:
        """Create a new Mail.tm account"""
        try:
            # Generate email components
            username = self.generate_username(first_name, last_name)
            domain = self.get_available_domain()
            email = f"{username}@{domain}"
            
            console.print(f"📧 Creating email: {email}", style="blue")
            
            # Create account data
            account_data = {
                "address": email,
                "password": self.password
            }
            
            # Make account creation request
            response = self.session.post(
                f"{self.base_url}/accounts",
                json=account_data,
                headers={'Content-Type': 'application/json'}
            )
            
            self.logger.debug(f"Account creation: {response.status_code} - {email}")
            
            if response.status_code == 201:
                # Success
                account_info = response.json()
                
                result = {
                    "email": email,
                    "email_password": self.password,
                    "mail_tm_id": account_info.get("id"),
                    "created_at": datetime.now().isoformat()
                }
                
                console.print(f"✅ Email account created: {email}", style="green")
                return result
            
            elif response.status_code == 422:
                # Email already exists - try with different username
                console.print(f"⚠️ Email exists, trying with different username...", style="yellow")
                
                # Generate new username with timestamp
                timestamp_username = f"{username}{int(datetime.now().timestamp()) % 10000}"
                new_email = f"{timestamp_username}@{domain}"
                
                account_data["address"] = new_email
                
                retry_response = self.session.post(
                    f"{self.base_url}/accounts",
                    json=account_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if retry_response.status_code == 201:
                    account_info = retry_response.json()
                    result = {
                        "email": new_email,
                        "email_password": self.password,
                        "mail_tm_id": account_info.get("id"),
                        "created_at": datetime.now().isoformat()
                    }
                    console.print(f"✅ Email account created (retry): {new_email}", style="green")
                    return result
                else:
                    raise Exception(f"Retry failed: {retry_response.status_code} - {retry_response.text}")
            
            else:
                raise Exception(f"Account creation failed: {response.status_code} - {response.text}")
        
        except requests.RequestException as e:
            raise Exception(f"Network error creating account: {e}")
    
    def get_account_token(self, email: str, password: str) -> str:
        """Get authentication token for an email account"""
        try:
            login_data = {
                "address": email,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/token",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("token")
            else:
                raise Exception(f"Token request failed: {response.status_code} - {response.text}")
        
        except requests.RequestException as e:
            raise Exception(f"Network error getting token: {e}")
    
    def get_messages(self, email: str, password: str) -> list:
        """Get messages for an email account"""
        try:
            # Get authentication token
            token = self.get_account_token(email, password)
            
            if not token:
                raise Exception("Failed to get authentication token")
            
            # Get messages
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(
                f"{self.base_url}/messages",
                headers=headers
            )
            
            if response.status_code == 200:
                messages_data = response.json()
                return messages_data.get("hydra:member", [])
            else:
                raise Exception(f"Messages request failed: {response.status_code} - {response.text}")
        
        except requests.RequestException as e:
            raise Exception(f"Network error getting messages: {e}")
    
    def get_message_content(self, email: str, password: str, message_id: str) -> Dict:
        """Get the content of a specific message"""
        try:
            token = self.get_account_token(email, password)
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(
                f"{self.base_url}/messages/{message_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Message content request failed: {response.status_code}")
        
        except requests.RequestException as e:
            raise Exception(f"Network error getting message content: {e}")
    
    def delete_account(self, email: str, password: str) -> bool:
        """Delete a Mail.tm account"""
        try:
            token = self.get_account_token(email, password)
            
            # Get account ID first
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            account_response = self.session.get(
                f"{self.base_url}/me",
                headers=headers
            )
            
            if account_response.status_code != 200:
                raise Exception(f"Failed to get account info: {account_response.status_code}")
            
            account_data = account_response.json()
            account_id = account_data.get("id")
            
            # Delete the account
            delete_response = self.session.delete(
                f"{self.base_url}/accounts/{account_id}",
                headers=headers
            )
            
            if delete_response.status_code == 204:
                console.print(f"✅ Account deleted: {email}", style="green")
                return True
            else:
                console.print(f"❌ Delete failed: {delete_response.status_code}", style="red")
                return False
        
        except Exception as e:
            console.print(f"❌ Error deleting account: {e}", style="red")
            return False
    
    def test_service(self) -> bool:
        """Test Mail.tm service availability"""
        try:
            # Test domain endpoint
            response = self.session.get(f"{self.base_url}/domains")
            
            if response.status_code == 200:
                domains = response.json()
                if domains.get("hydra:member"):
                    console.print("✅ Mail.tm service is available", style="green")
                    console.print(f"Available domains: {len(domains['hydra:member'])}", style="blue")
                    return True
                else:
                    console.print("⚠️ Mail.tm service has no available domains", style="yellow")
                    return False
            else:
                console.print(f"❌ Mail.tm service error: {response.status_code}", style="red")
                return False
        
        except Exception as e:
            console.print(f"❌ Mail.tm service test failed: {e}", style="red")
            return False
    
    def get_service_stats(self) -> Dict:
        """Get Mail.tm service statistics"""
        try:
            response = self.session.get(f"{self.base_url}/domains")
            
            if response.status_code == 200:
                domains_data = response.json()
                domains = domains_data.get("hydra:member", [])
                
                return {
                    "available_domains": len(domains),
                    "cached_domain": self._domain_cache,
                    "cache_age_seconds": (datetime.now() - self._domain_cache_time).total_seconds() 
                                       if self._domain_cache_time else None,
                    "service_status": "available" if domains else "no_domains"
                }
            else:
                return {
                    "available_domains": 0,
                    "service_status": "error",
                    "error_code": response.status_code
                }
        
        except Exception as e:
            return {
                "available_domains": 0,
                "service_status": "network_error",
                "error": str(e)
            }
