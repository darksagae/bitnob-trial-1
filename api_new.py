#!/usr/bin/env python3
"""
API module for Ajo Bitcoin Savings App
Bitnob API integration for mobile money and crypto payments in Uganda
"""

import requests
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import config

logger = logging.getLogger(__name__)

class BitnobAPI:
    """Bitnob API client for mobile money and crypto payments"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.BITNOB_API_KEY
        self.base_url = config.BITNOB_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.is_online = False
        logger.info("Bitnob API client initialized")
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            if config.API_MOCK_MODE:
                self.is_online = True
                logger.info("API connection test (mock mode): Success")
                return True
            
            response = self.session.get(f"{self.base_url}/v1/account/balance", timeout=10)
            if response.status_code == 200:
                self.is_online = True
                logger.info("API connection test: Success")
                return True
            else:
                self.is_online = False
                logger.warning(f"API connection test failed: {response.status_code}")
                return False
        except Exception as e:
            self.is_online = False
            logger.error(f"API connection test error: {e}")
            return False
    
    def get_account_balance(self) -> Dict:
        """Get account balance"""
        try:
            if config.API_MOCK_MODE:
                return {
                    'success': True,
                    'data': {
                        'balance': 1000000.00,  # 1M UGX mock balance
                        'currency': 'UGX'
                    }
                }
            
            response = self.session.get(f"{self.base_url}/v1/account/balance", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get balance: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_mobile_money_payment(self, phone_number: str, amount: float, 
                                  provider: str, reference: str) -> Dict:
        """Create mobile money payment"""
        try:
            if config.API_MOCK_MODE:
                return {
                    'success': True,
                    'data': {
                        'id': f'mock_{reference}',
                        'status': 'pending',
                        'reference': reference,
                        'amount': amount,
                        'phone_number': phone_number,
                        'provider': provider
                    }
                }
            
            payload = {
                'phone_number': phone_number,
                'amount': str(amount),
                'provider': provider,
                'reference': reference,
                'currency': 'UGX'
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/transfers/sendmobilemoney",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Mobile money payment failed: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            logger.error(f"Error creating mobile money payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_bitcoin_payment(self, amount: float, reference: str) -> Dict:
        """Create Bitcoin payment request"""
        try:
            if config.API_MOCK_MODE:
                return {
                    'success': True,
                    'data': {
                        'id': f'btc_{reference}',
                        'status': 'pending',
                        'reference': reference,
                        'amount': amount,
                        'bitcoin_address': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
                        'exchange_rate': 45000000  # 45M UGX per BTC
                    }
                }
            
            payload = {
                'amount': str(amount),
                'reference': reference,
                'currency': 'UGX'
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/transfers/sendbitcoin",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Bitcoin payment failed: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            logger.error(f"Error creating Bitcoin payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_usdt_payment(self, amount: float, reference: str) -> Dict:
        """Create USDT payment request"""
        try:
            if config.API_MOCK_MODE:
                return {
                    'success': True,
                    'data': {
                        'id': f'usdt_{reference}',
                        'status': 'pending',
                        'reference': reference,
                        'amount': amount,
                        'usdt_address': 'TRC20_ADDRESS_HERE',
                        'exchange_rate': 3800  # 3800 UGX per USDT
                    }
                }
            
            payload = {
                'amount': str(amount),
                'reference': reference,
                'currency': 'UGX',
                'network': 'TRC20'
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/transfers/sendusdt",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"USDT payment failed: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            logger.error(f"Error creating USDT payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_transaction_status(self, transaction_id: str) -> Dict:
        """Check transaction status"""
        try:
            if config.API_MOCK_MODE:
                return {
                    'success': True,
                    'data': {
                        'id': transaction_id,
                        'status': 'completed',
                        'confirmed_at': datetime.now().isoformat()
                    }
                }
            
            response = self.session.get(
                f"{self.base_url}/v1/transfers/{transaction_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Status check failed: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            logger.error(f"Error checking transaction status: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_transaction_history(self, limit: int = 50) -> Dict:
        """Get transaction history"""
        try:
            if config.API_MOCK_MODE:
                return {
                    'success': True,
                    'data': [
                        {
                            'id': 'mock_1',
                            'type': 'mobile_money',
                            'amount': 50000,
                            'status': 'completed',
                            'created_at': datetime.now().isoformat()
                        }
                    ]
                }
            
            response = self.session.get(
                f"{self.base_url}/v1/transfers?limit={limit}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"History fetch failed: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return {'success': False, 'error': str(e)}
    
    def transfer_commission(self, amount: float, payment_method: str, 
                          recipient_info: str) -> Dict:
        """Transfer commission to admin wallet"""
        try:
            if config.API_MOCK_MODE:
                return {
                    'success': True,
                    'data': {
                        'id': f'comm_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'status': 'completed',
                        'amount': amount,
                        'method': payment_method
                    }
                }
            
            if payment_method == 'mobile_money':
                return self.create_mobile_money_payment(
                    phone_number=recipient_info,
                    amount=amount,
                    provider='mtn',  # Default to MTN
                    reference=f'COMM_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                )
            elif payment_method == 'bitcoin':
                return self.create_bitcoin_payment(
                    amount=amount,
                    reference=f'COMM_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                )
            elif payment_method == 'usdt':
                return self.create_usdt_payment(
                    amount=amount,
                    reference=f'COMM_{datetime.now().strftime("%Y%m%d%H%M%S")}'
                )
            else:
                return {'success': False, 'error': 'Unsupported payment method'}
        except Exception as e:
            logger.error(f"Error transferring commission: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_exchange_rates(self) -> Dict:
        """Get current exchange rates"""
        try:
            if config.API_MOCK_MODE:
                return {
                    'success': True,
                    'data': {
                        'BTC_UGX': 45000000,
                        'USDT_UGX': 3800,
                        'USD_UGX': 3800
                    }
                }
            
            response = self.session.get(
                f"{self.base_url}/v1/rates",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Exchange rates fetch failed: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            logger.error(f"Error getting exchange rates: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_phone_number(self, phone_number: str, provider: str) -> bool:
        """Validate phone number format for provider"""
        try:
            if config.API_MOCK_MODE:
                return True
            
            # Basic validation for Uganda phone numbers
            phone_clean = phone_number.replace('+', '').replace(' ', '')
            
            if provider == 'mtn':
                # MTN Uganda: +256 7XX XXX XXX
                return phone_clean.startswith('2567') and len(phone_clean) == 12
            elif provider == 'airtel':
                # Airtel Uganda: +256 7XX XXX XXX
                return phone_clean.startswith('2567') and len(phone_clean) == 12
            elif provider == 'mpesa':
                # M-Pesa Uganda: +256 7XX XXX XXX
                return phone_clean.startswith('2567') and len(phone_clean) == 12
            else:
                return False
        except Exception as e:
            logger.error(f"Error validating phone number: {e}")
            return False
    
    def get_payment_methods(self) -> List[Dict]:
        """Get available payment methods"""
        return [
            {
                'id': 'mobile_money',
                'name': 'Mobile Money',
                'providers': ['mtn', 'airtel', 'mpesa'],
                'description': 'Send money via mobile money'
            },
            {
                'id': 'bitcoin',
                'name': 'Bitcoin',
                'providers': ['bitcoin'],
                'description': 'Send Bitcoin'
            },
            {
                'id': 'usdt',
                'name': 'USDT (TRC20)',
                'providers': ['usdt'],
                'description': 'Send USDT via TRC20 network'
            }
        ]
    
    def get_api_status(self) -> Dict:
        """Get API status information"""
        return {
            'online': self.is_online,
            'api_key_configured': bool(self.api_key and self.api_key != config.BITNOB_API_KEY),
            'base_url': self.base_url,
            'mock_mode': config.API_MOCK_MODE
        } 