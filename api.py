#!/usr/bin/env python3
"""
Bitnob API integration module for Ajo Bitcoin Savings App
Handles API communication with Bitnob for Bitcoin/USDT transactions and mobile money
"""

import requests # HTTP library for making API requests to Bitnob
import logging # Logging for error tracking, debugging and monitoring API operations
import json # JSON handling for API request and response data
import time # Time-related functions for delays and timestamps
from datetime import datetime # Date and time handling for timestamps and API calls
from typing import Dict, List, Optional, Tuple # Type hints for better code documentation and IDE support

class BitnobAPI: # Bitnob API client for Bitcoin and mobile money operations
    """Bitnob API client for Bitcoin and mobile money operations"""
    
    def __init__(self, api_key=None, base_url="https://api.bitnob.co"): # Initialize Bitnob API client. Self is the instance of the class, api_key is the Bitnob API key (optional), base_url is the Bitnob API base URL (default is https://api.bitnob.co)
        """Initialize Bitnob API client"""
        self.base_url = base_url # Store the Bitnob API base URL
        self.api_key = api_key or "demo_api_key_for_hackathon"  # Placeholder for demo - use provided API key or demo key
        self.logger = logging.getLogger(__name__) # Logger for the API class
        self.session = requests.Session() # Create HTTP session for persistent connections
        
        # Configure session headers
        self.session.headers.update({ # Update session headers with authentication and content type
            'Authorization': f'Bearer {self.api_key}', # Bearer token authentication
            'Content-Type': 'application/json', # JSON content type for requests
            'Accept': 'application/json' # Accept JSON responses
        })
        
        # API endpoints
        self.endpoints = { # Dictionary of Bitnob API endpoints
            'user_info': '/v1/user', # Get user information
            'balance': '/v1/accounts/balance', # Get account balance
            'exchange_rates': '/v1/rates', # Get exchange rates
            'bitcoin_address': '/v1/addresses/bitcoin', # Generate Bitcoin address
            'send_bitcoin': '/v1/transactions/bitcoin', # Send Bitcoin
            'mobile_money': '/v1/transactions/mobile-money', # Mobile money transactions
            'usdt_transfer': '/v1/transactions/usdt', # USDT transfers
            'webhook': '/v1/webhooks' # Webhook management
        }
        
        self.logger.info("Bitnob API client initialized") # Log successful API client initialization
    
    def is_online(self) -> bool: # Check if internet connection is available and API is reachable. Self is the instance of the class, returns boolean indicating online status
        """Check if internet connection is available and API is reachable"""
        try: # Try to check online status
            response = self.session.get(f"{self.base_url}/v1/health", timeout=5) # Make health check request with 5-second timeout
            return response.status_code == 200 # Return True if health check succeeds (status 200)
        except requests.RequestException: # Catch any request exceptions (network errors, timeouts, etc.)
            return False # Return False if health check fails
    
    def get_user_info(self) -> Optional[Dict]: # Get current user information from Bitnob. Self is the instance of the class, returns dictionary with user info or None
        """Get current user information from Bitnob"""
        try: # Try to get user information
            response = self.session.get(f"{self.base_url}{self.endpoints['user_info']}") # Make GET request to user info endpoint
            
            if response.status_code == 200: # If request was successful
                user_data = response.json() # Parse JSON response
                self.logger.info("Retrieved user info from Bitnob") # Log successful user info retrieval
                return user_data # Return user data dictionary
            else: # If request failed
                self.logger.warning(f"Failed to get user info: {response.status_code}") # Log warning with status code
                return None # Return None for failed request
                
        except Exception as e: # Catch any exceptions during user info retrieval
            self.logger.error(f"Error getting user info: {e}") # Log the error
            return None # Return None if exception occurs
    
    def get_user_balance(self) -> Optional[Dict]: # Get user balance across all currencies. Self is the instance of the class, returns dictionary with balance info or None
        """Get user balance across all currencies"""
        try: # Try to get user balance
            response = self.session.get(f"{self.base_url}{self.endpoints['balance']}") # Make GET request to balance endpoint
            
            if response.status_code == 200: # If request was successful
                balance_data = response.json() # Parse JSON response
                self.logger.info("Retrieved balance from Bitnob") # Log successful balance retrieval
                return balance_data # Return balance data dictionary
            else: # If request failed
                self.logger.warning(f"Failed to get balance: {response.status_code}") # Log warning with status code
                return None # Return None for failed request
                
        except Exception as e: # Catch any exceptions during balance retrieval
            self.logger.error(f"Error getting balance: {e}") # Log the error
            return None # Return None if exception occurs
    
    def get_exchange_rates(self) -> Optional[Dict]: # Get current exchange rates from Bitnob. Self is the instance of the class, returns dictionary with exchange rates or None
        """Get current exchange rates from Bitnob"""
        try: # Try to get exchange rates
            response = self.session.get(f"{self.base_url}{self.endpoints['exchange_rates']}") # Make GET request to exchange rates endpoint
            
            if response.status_code == 200: # If request was successful
                rates_data = response.json() # Parse JSON response
                self.logger.info("Retrieved exchange rates from Bitnob") # Log successful rates retrieval
                return rates_data # Return exchange rates data dictionary
            else: # If request failed
                self.logger.warning(f"Failed to get exchange rates: {response.status_code}") # Log warning with status code
                return None # Return None for failed request
                
        except Exception as e: # Catch any exceptions during rates retrieval
            self.logger.error(f"Error getting exchange rates: {e}") # Log the error
            return None # Return None if exception occurs
    
    def generate_bitcoin_address(self, label="Ajo Savings") -> Optional[str]: # Generate a new Bitcoin address via Bitnob API. Self is the instance of the class, label is the label for the address (default is "Ajo Savings"), returns Bitcoin address string or None
        """Generate a new Bitcoin address via Bitnob API"""
        try: # Try to generate Bitcoin address
            payload = { # Create request payload
                "label": label, # Address label
                "type": "bitcoin" # Address type
            }
            
            response = self.session.post( # Make POST request to generate address
                f"{self.base_url}{self.endpoints['bitcoin_address']}", # Bitcoin address endpoint
                json=payload # Send JSON payload
            )
            
            if response.status_code == 201: # If address generation was successful (201 Created)
                address_data = response.json() # Parse JSON response
                address = address_data.get('address') # Extract address from response
                self.logger.info(f"Generated Bitcoin address: {address}") # Log successful address generation
                return address # Return the generated address
            else: # If address generation failed
                self.logger.warning(f"Failed to generate address: {response.status_code}") # Log warning with status code
                return None # Return None for failed generation
                
        except Exception as e: # Catch any exceptions during address generation
            self.logger.error(f"Error generating Bitcoin address: {e}") # Log the error
            return None # Return None if exception occurs
    
    def send_bitcoin(self, to_address: str, amount: float, 
                    description: str = "Ajo savings contribution") -> bool: # Send Bitcoin via Bitnob API. Self is the instance of the class, to_address is the destination Bitcoin address, amount is the amount to send, description is the transaction description (default is "Ajo savings contribution"), returns boolean indicating success
        """Send Bitcoin via Bitnob API"""
        try: # Try to send Bitcoin
            payload = { # Create request payload
                "address": to_address, # Destination address
                "amount": str(amount), # Amount as string
                "description": description, # Transaction description
                "priority": "medium" # Transaction priority
            }
            
            response = self.session.post( # Make POST request to send Bitcoin
                f"{self.base_url}{self.endpoints['send_bitcoin']}", # Send Bitcoin endpoint
                json=payload # Send JSON payload
            )
            
            if response.status_code == 201: # If Bitcoin send was successful (201 Created)
                transaction_data = response.json() # Parse JSON response
                self.logger.info(f"Bitcoin transaction sent: {transaction_data.get('id')}") # Log successful transaction with ID
                return True # Return True for successful send
            else: # If Bitcoin send failed
                self.logger.warning(f"Failed to send Bitcoin: {response.status_code}") # Log warning with status code
                return False # Return False for failed send
                
        except Exception as e: # Catch any exceptions during Bitcoin send
            self.logger.error(f"Error sending Bitcoin: {e}") # Log the error
            return False # Return False if exception occurs
    
    def process_mobile_money_payout(self, amount: float, phone_number: str, 
                                  description: str = "Ajo payout") -> bool: # Process mobile money payout via Bitnob API. Self is the instance of the class, amount is the payout amount, phone_number is the recipient's phone number, description is the payout description (default is "Ajo payout"), returns boolean indicating success
        """Process mobile money payout via Bitnob API"""
        try: # Try to process mobile money payout
            payload = { # Create request payload
                "amount": str(amount), # Amount as string
                "phone_number": phone_number, # Recipient phone number
                "description": description, # Payout description
                "currency": "UGX",  # Ugandan Shilling
                "provider": "mpesa"  # Default to M-Pesa
            }
            
            response = self.session.post( # Make POST request to process payout
                f"{self.base_url}{self.endpoints['mobile_money']}", # Mobile money endpoint
                json=payload # Send JSON payload
            )
            
            if response.status_code == 201: # If payout processing was successful (201 Created)
                payout_data = response.json() # Parse JSON response
                self.logger.info(f"Mobile money payout processed: {payout_data.get('id')}") # Log successful payout with ID
                return True # Return True for successful payout
            else: # If payout processing failed
                self.logger.warning(f"Failed to process payout: {response.status_code}") # Log warning with status code
                return False # Return False for failed payout
                
        except Exception as e: # Catch any exceptions during payout processing
            self.logger.error(f"Error processing mobile money payout: {e}") # Log the error
            return False # Return False if exception occurs
    
    def send_usdt(self, to_address: str, amount: float, 
                 description: str = "Ajo USDT transfer") -> bool: # Send USDT via Bitnob API. Self is the instance of the class, to_address is the destination USDT address, amount is the amount to send, description is the transaction description (default is "Ajo USDT transfer"), returns boolean indicating success
        """Send USDT via Bitnob API"""
        try: # Try to send USDT
            payload = { # Create request payload
                "address": to_address, # Destination address
                "amount": str(amount), # Amount as string
                "description": description, # Transaction description
                "network": "TRC20"  # Default to TRC20 network
            }
            
            response = self.session.post( # Make POST request to send USDT
                f"{self.base_url}{self.endpoints['usdt_transfer']}", # USDT transfer endpoint
                json=payload # Send JSON payload
            )
            
            if response.status_code == 201: # If USDT send was successful (201 Created)
                transaction_data = response.json() # Parse JSON response
                self.logger.info(f"USDT transaction sent: {transaction_data.get('id')}") # Log successful transaction with ID
                return True # Return True for successful send
            else: # If USDT send failed
                self.logger.warning(f"Failed to send USDT: {response.status_code}") # Log warning with status code
                return False # Return False for failed send
                
        except Exception as e: # Catch any exceptions during USDT send
            self.logger.error(f"Error sending USDT: {e}") # Log the error
            return False # Return False if exception occurs
    
    def record_contribution(self, member_name: str, amount: float, 
                          contribution_type: str, bitcoin_address: str = None) -> bool: # Record a contribution in Bitnob system (custom endpoint for Ajo). Self is the instance of the class, member_name is the name of the member, amount is the contribution amount, contribution_type is the type of contribution, bitcoin_address is the Bitcoin address (optional), returns boolean indicating success
        """Record a contribution in Bitnob system (custom endpoint for Ajo)"""
        try: # Try to record contribution
            payload = { # Create request payload
                "member_name": member_name, # Member name
                "amount": str(amount), # Amount as string
                "contribution_type": contribution_type, # Type of contribution
                "bitcoin_address": bitcoin_address, # Bitcoin address if applicable
                "timestamp": datetime.now().isoformat(), # Current timestamp
                "app": "ajo_savings" # Application identifier
            }
            
            # This would be a custom endpoint for Ajo savings tracking
            # For demo purposes, we'll simulate success
            self.logger.info(f"Recorded contribution: {member_name} - {amount} {contribution_type}") # Log successful contribution recording
            return True # Return True for successful recording
            
        except Exception as e: # Catch any exceptions during contribution recording
            self.logger.error(f"Error recording contribution: {e}") # Log the error
            return False # Return False if exception occurs
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict]: # Get status of a transaction. Self is the instance of the class, transaction_id is the ID of the transaction, returns dictionary with transaction status or None
        """Get status of a transaction"""
        try: # Try to get transaction status
            response = self.session.get(f"{self.base_url}/v1/transactions/{transaction_id}") # Make GET request to transaction status endpoint
            
            if response.status_code == 200: # If request was successful
                status_data = response.json() # Parse JSON response
                self.logger.info(f"Retrieved transaction status: {transaction_id}") # Log successful status retrieval
                return status_data # Return status data dictionary
            else: # If request failed
                self.logger.warning(f"Failed to get transaction status: {response.status_code}") # Log warning with status code
                return None # Return None for failed request
                
        except Exception as e: # Catch any exceptions during status retrieval
            self.logger.error(f"Error getting transaction status: {e}") # Log the error
            return None # Return None if exception occurs
    
    def get_transaction_history(self, limit: int = 50) -> Optional[List[Dict]]: # Get transaction history from Bitnob. Self is the instance of the class, limit is the maximum number of transactions to retrieve (default is 50), returns list of transaction dictionaries or None
        """Get transaction history from Bitnob"""
        try: # Try to get transaction history
            params = {"limit": limit} # Create query parameters
            response = self.session.get(f"{self.base_url}/v1/transactions", params=params) # Make GET request to transactions endpoint with limit parameter
            
            if response.status_code == 200: # If request was successful
                history_data = response.json() # Parse JSON response
                self.logger.info("Retrieved transaction history from Bitnob") # Log successful history retrieval
                return history_data.get('data', []) # Return transaction data list or empty list
            else: # If request failed
                self.logger.warning(f"Failed to get transaction history: {response.status_code}") # Log warning with status code
                return None # Return None for failed request
                
        except Exception as e: # Catch any exceptions during history retrieval
            self.logger.error(f"Error getting transaction history: {e}") # Log the error
            return None # Return None if exception occurs
    
    def setup_webhook(self, webhook_url: str, events: List[str] = None) -> bool: # Setup webhook for real-time notifications. Self is the instance of the class, webhook_url is the URL to receive webhook notifications, events is the list of events to subscribe to (optional), returns boolean indicating success
        """Setup webhook for real-time notifications"""
        try: # Try to setup webhook
            if not events: # If no events specified
                events = ["transaction.completed", "transaction.failed"] # Use default events
            
            payload = { # Create request payload
                "url": webhook_url, # Webhook URL
                "events": events, # List of events
                "description": "Ajo Savings App webhook" # Webhook description
            }
            
            response = self.session.post( # Make POST request to setup webhook
                f"{self.base_url}{self.endpoints['webhook']}", # Webhook endpoint
                json=payload # Send JSON payload
            )
            
            if response.status_code == 201: # If webhook setup was successful (201 Created)
                webhook_data = response.json() # Parse JSON response
                self.logger.info(f"Webhook setup successful: {webhook_data.get('id')}") # Log successful webhook setup with ID
                return True # Return True for successful setup
            else: # If webhook setup failed
                self.logger.warning(f"Failed to setup webhook: {response.status_code}") # Log warning with status code
                return False # Return False for failed setup
                
        except Exception as e: # Catch any exceptions during webhook setup
            self.logger.error(f"Error setting up webhook: {e}") # Log the error
            return False # Return False if exception occurs
    
    def convert_currency(self, from_currency: str, to_currency: str, 
                        amount: float) -> Optional[float]: # Convert currency using Bitnob rates. Self is the instance of the class, from_currency is the source currency, to_currency is the target currency, amount is the amount to convert, returns converted amount or None
        """Convert currency using Bitnob rates"""
        try: # Try to convert currency
            rates = self.get_exchange_rates() # Get current exchange rates
            if not rates: # If rates retrieval failed
                return None # Return None if no rates available
            
            # Find conversion rate
            rate_key = f"{from_currency}_{to_currency}" # Create rate key for currency pair
            if rate_key in rates: # If conversion rate exists
                converted_amount = amount * rates[rate_key] # Calculate converted amount
                self.logger.info(f"Converted {amount} {from_currency} to {converted_amount} {to_currency}") # Log successful conversion
                return converted_amount # Return converted amount
            else: # If conversion rate not found
                self.logger.warning(f"Conversion rate not found: {rate_key}") # Log warning about missing rate
                return None # Return None if rate not found
                
        except Exception as e: # Catch any exceptions during currency conversion
            self.logger.error(f"Error converting currency: {e}") # Log the error
            return None # Return None if exception occurs
    
    def get_uganda_mobile_money_providers(self) -> List[Dict]: # Get available mobile money providers in Uganda. Self is the instance of the class, returns list of provider dictionaries
        """Get available mobile money providers in Uganda"""
        try: # Try to get mobile money providers
            # This would be a real API call in production
            # For demo, return common Ugandan providers
            providers = [ # List of Ugandan mobile money providers
                {
                    "name": "M-Pesa", # Provider name
                    "code": "mpesa", # Provider code
                    "country": "UG", # Country code
                    "currency": "UGX", # Currency
                    "active": True # Active status
                },
                {
                    "name": "Airtel Money", # Provider name
                    "code": "airtel", # Provider code
                    "country": "UG", # Country code
                    "currency": "UGX", # Currency
                    "active": True # Active status
                },
                {
                    "name": "MTN Mobile Money", # Provider name
                    "code": "mtn", # Provider code
                    "country": "UG", # Country code
                    "currency": "UGX", # Currency
                    "active": True # Active status
                }
            ]
            
            self.logger.info("Retrieved Uganda mobile money providers") # Log successful providers retrieval
            return providers # Return providers list
            
        except Exception as e: # Catch any exceptions during providers retrieval
            self.logger.error(f"Error getting mobile money providers: {e}") # Log the error
            return [] # Return empty list if exception occurs
    
    def validate_phone_number(self, phone_number: str, country: str = "UG") -> bool: # Validate phone number format for Uganda. Self is the instance of the class, phone_number is the phone number to validate, country is the country code (default is "UG"), returns boolean indicating validity
        """Validate phone number format for Uganda"""
        try: # Try to validate phone number
            # Basic validation for Ugandan phone numbers
            if country == "UG": # If validating for Uganda
                # Remove any non-digit characters
                clean_number = ''.join(filter(str.isdigit, phone_number)) # Extract only digits from phone number
                
                # Ugandan numbers should be 9-10 digits
                if len(clean_number) >= 9 and len(clean_number) <= 10: # Check if length is valid
                    return True # Return True for valid Ugandan number
                else: # If length is invalid
                    return False # Return False for invalid length
            
            return True  # For other countries, assume valid
            
        except Exception as e: # Catch any exceptions during phone number validation
            self.logger.error(f"Error validating phone number: {e}") # Log the error
            return False # Return False if exception occurs
    
    def get_api_status(self) -> Dict: # Get API status and health information. Self is the instance of the class, returns dictionary with API status information
        """Get API status and health information"""
        try: # Try to get API status
            status = { # Create status dictionary
                "online": self.is_online(), # Check if API is online
                "api_key_configured": bool(self.api_key and self.api_key != "demo_api_key_for_hackathon"), # Check if real API key is configured
                "base_url": self.base_url, # API base URL
                "last_check": datetime.now().isoformat() # Last check timestamp
            }
            
            if status["online"]: # If API is online
                # Try to get user info to verify API key
                user_info = self.get_user_info() # Get user information
                status["api_key_valid"] = user_info is not None # Check if API key is valid
                status["user_authenticated"] = user_info is not None # Check if user is authenticated
            else: # If API is offline
                status["api_key_valid"] = False # Set API key validity to False
                status["user_authenticated"] = False # Set authentication to False
            
            return status # Return status dictionary
            
        except Exception as e: # Catch any exceptions during status retrieval
            self.logger.error(f"Error getting API status: {e}") # Log the error
            return {"error": str(e)} # Return error status 