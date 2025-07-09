#!/usr/bin/env python3
"""
Bitnob API integration module for Ajo Bitcoin Savings App
Handles API communication with Bitnob for Bitcoin/USDT transactions and mobile money
"""

import requests
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class BitnobAPI:
    """Bitnob API client for Bitcoin and mobile money operations"""
    
    def __init__(self, api_key=None, base_url="https://api.bitnob.co"):
        """Initialize Bitnob API client"""
        self.base_url = base_url
        self.api_key = api_key or "demo_api_key_for_hackathon"  # Placeholder for demo
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Configure session headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # API endpoints
        self.endpoints = {
            'user_info': '/v1/user',
            'balance': '/v1/accounts/balance',
            'exchange_rates': '/v1/rates',
            'bitcoin_address': '/v1/addresses/bitcoin',
            'send_bitcoin': '/v1/transactions/bitcoin',
            'mobile_money': '/v1/transactions/mobile-money',
            'usdt_transfer': '/v1/transactions/usdt',
            'webhook': '/v1/webhooks'
        }
        
        self.logger.info("Bitnob API client initialized")
    
    def is_online(self) -> bool:
        """Check if internet connection is available and API is reachable"""
        try:
            response = self.session.get(f"{self.base_url}/v1/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_user_info(self) -> Optional[Dict]:
        """Get current user information from Bitnob"""
        try:
            response = self.session.get(f"{self.base_url}{self.endpoints['user_info']}")
            
            if response.status_code == 200:
                user_data = response.json()
                self.logger.info("Retrieved user info from Bitnob")
                return user_data
            else:
                self.logger.warning(f"Failed to get user info: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting user info: {e}")
            return None
    
    def get_user_balance(self) -> Optional[Dict]:
        """Get user balance across all currencies"""
        try:
            response = self.session.get(f"{self.base_url}{self.endpoints['balance']}")
            
            if response.status_code == 200:
                balance_data = response.json()
                self.logger.info("Retrieved balance from Bitnob")
                return balance_data
            else:
                self.logger.warning(f"Failed to get balance: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            return None
    
    def get_exchange_rates(self) -> Optional[Dict]:
        """Get current exchange rates from Bitnob"""
        try:
            response = self.session.get(f"{self.base_url}{self.endpoints['exchange_rates']}")
            
            if response.status_code == 200:
                rates_data = response.json()
                self.logger.info("Retrieved exchange rates from Bitnob")
                return rates_data
            else:
                self.logger.warning(f"Failed to get exchange rates: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting exchange rates: {e}")
            return None
    
    def generate_bitcoin_address(self, label="Ajo Savings") -> Optional[str]:
        """Generate a new Bitcoin address via Bitnob API"""
        try:
            payload = {
                "label": label,
                "type": "bitcoin"
            }
            
            response = self.session.post(
                f"{self.base_url}{self.endpoints['bitcoin_address']}", 
                json=payload
            )
            
            if response.status_code == 201:
                address_data = response.json()
                address = address_data.get('address')
                self.logger.info(f"Generated Bitcoin address: {address}")
                return address
            else:
                self.logger.warning(f"Failed to generate address: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating Bitcoin address: {e}")
            return None
    
    def send_bitcoin(self, to_address: str, amount: float, 
                    description: str = "Ajo savings contribution") -> bool:
        """Send Bitcoin via Bitnob API"""
        try:
            payload = {
                "address": to_address,
                "amount": str(amount),
                "description": description,
                "priority": "medium"
            }
            
            response = self.session.post(
                f"{self.base_url}{self.endpoints['send_bitcoin']}", 
                json=payload
            )
            
            if response.status_code == 201:
                transaction_data = response.json()
                self.logger.info(f"Bitcoin transaction sent: {transaction_data.get('id')}")
                return True
            else:
                self.logger.warning(f"Failed to send Bitcoin: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending Bitcoin: {e}")
            return False
    
    def process_mobile_money_payout(self, amount: float, phone_number: str, 
                                  description: str = "Ajo payout") -> bool:
        """Process mobile money payout via Bitnob API"""
        try:
            payload = {
                "amount": str(amount),
                "phone_number": phone_number,
                "description": description,
                "currency": "UGX",  # Ugandan Shilling
                "provider": "mpesa"  # Default to M-Pesa
            }
            
            response = self.session.post(
                f"{self.base_url}{self.endpoints['mobile_money']}", 
                json=payload
            )
            
            if response.status_code == 201:
                payout_data = response.json()
                self.logger.info(f"Mobile money payout processed: {payout_data.get('id')}")
                return True
            else:
                self.logger.warning(f"Failed to process payout: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing mobile money payout: {e}")
            return False
    
    def send_usdt(self, to_address: str, amount: float, 
                 description: str = "Ajo USDT transfer") -> bool:
        """Send USDT via Bitnob API"""
        try:
            payload = {
                "address": to_address,
                "amount": str(amount),
                "description": description,
                "network": "TRC20"  # Default to TRC20 network
            }
            
            response = self.session.post(
                f"{self.base_url}{self.endpoints['usdt_transfer']}", 
                json=payload
            )
            
            if response.status_code == 201:
                transaction_data = response.json()
                self.logger.info(f"USDT transaction sent: {transaction_data.get('id')}")
                return True
            else:
                self.logger.warning(f"Failed to send USDT: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending USDT: {e}")
            return False
    
    def record_contribution(self, member_name: str, amount: float, 
                          contribution_type: str, bitcoin_address: str = None) -> bool:
        """Record a contribution in Bitnob system (custom endpoint for Ajo)"""
        try:
            payload = {
                "member_name": member_name,
                "amount": str(amount),
                "contribution_type": contribution_type,
                "bitcoin_address": bitcoin_address,
                "timestamp": datetime.now().isoformat(),
                "app": "ajo_savings"
            }
            
            # This would be a custom endpoint for Ajo savings tracking
            # For demo purposes, we'll simulate success
            self.logger.info(f"Recorded contribution: {member_name} - {amount} {contribution_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording contribution: {e}")
            return False
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict]:
        """Get status of a transaction"""
        try:
            response = self.session.get(f"{self.base_url}/v1/transactions/{transaction_id}")
            
            if response.status_code == 200:
                status_data = response.json()
                self.logger.info(f"Retrieved transaction status: {transaction_id}")
                return status_data
            else:
                self.logger.warning(f"Failed to get transaction status: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting transaction status: {e}")
            return None
    
    def get_transaction_history(self, limit: int = 50) -> Optional[List[Dict]]:
        """Get transaction history from Bitnob"""
        try:
            params = {"limit": limit}
            response = self.session.get(f"{self.base_url}/v1/transactions", params=params)
            
            if response.status_code == 200:
                history_data = response.json()
                self.logger.info("Retrieved transaction history from Bitnob")
                return history_data.get('data', [])
            else:
                self.logger.warning(f"Failed to get transaction history: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting transaction history: {e}")
            return None
    
    def setup_webhook(self, webhook_url: str, events: List[str] = None) -> bool:
        """Setup webhook for real-time notifications"""
        try:
            if not events:
                events = ["transaction.completed", "transaction.failed"]
            
            payload = {
                "url": webhook_url,
                "events": events,
                "description": "Ajo Savings App webhook"
            }
            
            response = self.session.post(
                f"{self.base_url}{self.endpoints['webhook']}", 
                json=payload
            )
            
            if response.status_code == 201:
                webhook_data = response.json()
                self.logger.info(f"Webhook setup successful: {webhook_data.get('id')}")
                return True
            else:
                self.logger.warning(f"Failed to setup webhook: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting up webhook: {e}")
            return False
    
    def convert_currency(self, from_currency: str, to_currency: str, 
                        amount: float) -> Optional[float]:
        """Convert currency using Bitnob rates"""
        try:
            rates = self.get_exchange_rates()
            if not rates:
                return None
            
            # Find conversion rate
            rate_key = f"{from_currency}_{to_currency}"
            if rate_key in rates:
                converted_amount = amount * rates[rate_key]
                self.logger.info(f"Converted {amount} {from_currency} to {converted_amount} {to_currency}")
                return converted_amount
            else:
                self.logger.warning(f"Conversion rate not found: {rate_key}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error converting currency: {e}")
            return None
    
    def get_uganda_mobile_money_providers(self) -> List[Dict]:
        """Get available mobile money providers in Uganda"""
        try:
            # This would be a real API call in production
            # For demo, return common Ugandan providers
            providers = [
                {
                    "name": "M-Pesa",
                    "code": "mpesa",
                    "country": "UG",
                    "currency": "UGX",
                    "active": True
                },
                {
                    "name": "Airtel Money",
                    "code": "airtel",
                    "country": "UG", 
                    "currency": "UGX",
                    "active": True
                },
                {
                    "name": "MTN Mobile Money",
                    "code": "mtn",
                    "country": "UG",
                    "currency": "UGX", 
                    "active": True
                }
            ]
            
            self.logger.info("Retrieved Uganda mobile money providers")
            return providers
            
        except Exception as e:
            self.logger.error(f"Error getting mobile money providers: {e}")
            return []
    
    def validate_phone_number(self, phone_number: str, country: str = "UG") -> bool:
        """Validate phone number format for Uganda"""
        try:
            # Basic validation for Ugandan phone numbers
            if country == "UG":
                # Remove any non-digit characters
                clean_number = ''.join(filter(str.isdigit, phone_number))
                
                # Ugandan numbers should be 9-10 digits
                if len(clean_number) >= 9 and len(clean_number) <= 10:
                    return True
                else:
                    return False
            
            return True  # For other countries, assume valid
            
        except Exception as e:
            self.logger.error(f"Error validating phone number: {e}")
            return False
    
    def get_api_status(self) -> Dict:
        """Get API status and health information"""
        try:
            status = {
                "online": self.is_online(),
                "api_key_configured": bool(self.api_key and self.api_key != "demo_api_key_for_hackathon"),
                "base_url": self.base_url,
                "last_check": datetime.now().isoformat()
            }
            
            if status["online"]:
                # Try to get user info to verify API key
                user_info = self.get_user_info()
                status["api_key_valid"] = user_info is not None
                status["user_authenticated"] = user_info is not None
            else:
                status["api_key_valid"] = False
                status["user_authenticated"] = False
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting API status: {e}")
            return {"error": str(e)} 