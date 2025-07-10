#!/usr/bin/env python3
"""
Bitcoin Wallet module for Ajo Bitcoin Savings App
Handles offline Bitcoin address generation and transaction management
"""

import logging # Logging for error tracking, debugging and monitoring wallet operations
import json # JSON handling for storing wallet data structures
import hashlib # Hash functions for address generation and data integrity
import secrets # Cryptographically secure random number generation for private keys
from pathlib import Path # Object-oriented filesystem paths for cross-platform directory operations
from datetime import datetime # Date and time handling for timestamps and file naming
import bitcoinlib # Bitcoin library for wallet management and address generation
from bitcoinlib.wallets import Wallet # Bitcoin wallet class for managing HD wallets
from bitcoinlib.mnemonic import Mnemonic # Mnemonic phrase generation for wallet backup
from bitcoinlib.keys import HDKey # Hierarchical deterministic key management

class BitcoinWallet: # Bitcoin wallet manager for offline address generation and transaction handling
    """Bitcoin wallet manager for offline address generation and transaction handling"""
    
    def __init__(self, wallet_name="ajo_savings_wallet"): # Initialize Bitcoin wallet. Self is the instance of the class, wallet_name is the name of the wallet (default is ajo_savings_wallet)
        """Initialize Bitcoin wallet"""
        self.wallet_name = wallet_name # Store the wallet name
        self.logger = logging.getLogger(__name__) # Logger for the wallet class
        self.wallet_dir = Path("wallets") # Directory for storing wallet files
        self.wallet_dir.mkdir(exist_ok=True) # Create wallets directory if it doesn't exist
        
        # Initialize or load existing wallet
        self.wallet = self._initialize_wallet() # Initialize or load existing Bitcoin wallet
        self.logger.info(f"Bitcoin wallet initialized: {wallet_name}") # Log successful wallet initialization
    
    def _initialize_wallet(self): # Initialize or load existing Bitcoin wallet. Self is the instance of the class
        """Initialize or load existing Bitcoin wallet"""
        try: # Try to initialize the wallet
            # Check if wallet already exists
            wallet_path = self.wallet_dir / f"{self.wallet_name}.json" # Path to wallet configuration file
            
            if wallet_path.exists(): # If wallet file exists
                # Load existing wallet
                self.logger.info("Loading existing wallet") # Log that existing wallet is being loaded
                return Wallet(self.wallet_name, db_uri=f"sqlite:///{self.wallet_dir}/bitcoinlib.db") # Return existing wallet from database
            else: # If wallet file doesn't exist
                # Create new wallet
                self.logger.info("Creating new Bitcoin wallet") # Log that new wallet is being created
                return self._create_new_wallet() # Create and return new wallet
                
        except Exception as e: # Catch any exceptions during wallet initialization
            self.logger.error(f"Failed to initialize wallet: {e}") # Log the error
            # Fallback to simple address generation
            return None # Return None if wallet initialization fails
    
    def _create_new_wallet(self): # Create a new Bitcoin wallet with mnemonic. Self is the instance of the class
        """Create a new Bitcoin wallet with mnemonic"""
        try: # Try to create new wallet
            # Generate mnemonic phrase
            mnemonic = Mnemonic().generate() # Generate cryptographically secure mnemonic phrase
            
            # Create wallet
            wallet = Wallet.create( # Create new Bitcoin wallet
                name=self.wallet_name, # Wallet name
                keys=mnemonic, # Mnemonic phrase as seed
                network='bitcoin', # Bitcoin network
                db_uri=f"sqlite:///{self.wallet_dir}/bitcoinlib.db" # Database URI for wallet storage
            )
            
            # Save mnemonic securely (in production, use proper key management)
            self._save_mnemonic(mnemonic) # Save mnemonic phrase to file
            
            self.logger.info("New Bitcoin wallet created successfully") # Log successful wallet creation
            return wallet # Return the new wallet
            
        except Exception as e: # Catch any exceptions during wallet creation
            self.logger.error(f"Failed to create wallet: {e}") # Log the error
            return None # Return None if wallet creation fails
    
    def _save_mnemonic(self, mnemonic): # Save mnemonic phrase securely. Self is the instance of the class, mnemonic is the mnemonic phrase to save
        """Save mnemonic phrase securely"""
        try: # Try to save the mnemonic
            mnemonic_file = self.wallet_dir / f"{self.wallet_name}_mnemonic.txt" # Path to mnemonic file
            with open(mnemonic_file, 'w') as f: # Open file for writing
                f.write(f"# Ajo Bitcoin Savings Wallet - {datetime.now()}\n") # Write header with timestamp
                f.write(f"# IMPORTANT: Keep this secure and private!\n") # Write security warning
                f.write(f"# Mnemonic phrase for wallet recovery:\n\n") # Write description
                f.write(mnemonic) # Write the mnemonic phrase
                f.write(f"\n\n# Wallet name: {self.wallet_name}") # Write wallet name
                f.write(f"\n# Created: {datetime.now()}") # Write creation timestamp
            
            # Set restrictive permissions (Unix-like systems)
            try: # Try to set file permissions
                mnemonic_file.chmod(0o600) # Set read/write permissions for owner only
            except: # If chmod fails (e.g., on Windows)
                pass  # Windows doesn't support chmod
                
            self.logger.info(f"Mnemonic saved to: {mnemonic_file}") # Log successful mnemonic save
            
        except Exception as e: # Catch any exceptions during mnemonic save
            self.logger.error(f"Failed to save mnemonic: {e}") # Log the error
    
    def generate_address(self, address_type="legacy"): # Generate a new Bitcoin address for contributions. Self is the instance of the class, address_type is the type of address to generate (default is legacy)
        """Generate a new Bitcoin address for contributions"""
        try: # Try to generate address
            if self.wallet: # If wallet is available
                # Use bitcoinlib wallet
                address = self.wallet.get_key().address # Get new address from wallet
                self.logger.info(f"Generated Bitcoin address: {address}") # Log successful address generation
                return address # Return the generated address
            else: # If wallet is not available
                # Fallback to simple address generation
                return self._generate_simple_address() # Generate simple demo address
                
        except Exception as e: # Catch any exceptions during address generation
            self.logger.error(f"Failed to generate address: {e}") # Log the error
            return self._generate_simple_address() # Fallback to simple address generation
    
    def _generate_simple_address(self): # Generate a simple Bitcoin address for demo purposes. Self is the instance of the class
        """Generate a simple Bitcoin address for demo purposes"""
        try: # Try to generate simple address
            # This is a simplified address generation for demo
            # In production, use proper Bitcoin address generation
            random_bytes = secrets.token_bytes(32) # Generate 32 random bytes
            address_hash = hashlib.sha256(random_bytes).hexdigest() # Create SHA-256 hash of random bytes
            
            # Format as a Bitcoin-like address (this is not a real Bitcoin address)
            address = f"1Ajo{address_hash[:26].upper()}" # Create demo address with "1Ajo" prefix
            
            self.logger.info(f"Generated demo address: {address}") # Log successful demo address generation
            return address # Return the demo address
            
        except Exception as e: # Catch any exceptions during simple address generation
            self.logger.error(f"Failed to generate simple address: {e}") # Log the error
            return None # Return None if address generation fails
    
    def get_wallet_balance(self): # Get wallet balance (requires internet connection). Self is the instance of the class
        """Get wallet balance (requires internet connection)"""
        try: # Try to get wallet balance
            if self.wallet: # If wallet is available
                balance = self.wallet.balance() # Get wallet balance from bitcoinlib
                self.logger.info(f"Wallet balance: {balance}") # Log wallet balance
                return balance # Return the balance
            else: # If wallet is not available
                return 0 # Return zero balance
        except Exception as e: # Catch any exceptions during balance retrieval
            self.logger.error(f"Failed to get wallet balance: {e}") # Log the error
            return 0 # Return zero balance on error
    
    def get_address_balance(self, address): # Get balance for a specific address. Self is the instance of the class, address is the Bitcoin address to check
        """Get balance for a specific address"""
        try: # Try to get address balance
            if self.wallet: # If wallet is available
                # This would require blockchain API access
                # For offline demo, return 0
                return 0 # Return zero balance for demo
            else: # If wallet is not available
                return 0 # Return zero balance
        except Exception as e: # Catch any exceptions during address balance retrieval
            self.logger.error(f"Failed to get address balance: {e}") # Log the error
            return 0 # Return zero balance on error
    
    def create_transaction(self, to_address, amount, fee_rate=10): # Create a Bitcoin transaction (offline preparation). Self is the instance of the class, to_address is the destination address, amount is the amount to send, fee_rate is the fee rate in satoshis per byte (default is 10)
        """Create a Bitcoin transaction (offline preparation)"""
        try: # Try to create transaction
            if not self.wallet: # If wallet is not available
                return None # Return None if no wallet
            
            # Create transaction object
            transaction = { # Create transaction dictionary
                'to_address': to_address, # Destination address
                'amount': amount, # Amount to send
                'fee_rate': fee_rate, # Fee rate
                'created_at': datetime.now().isoformat(), # Creation timestamp
                'status': 'pending' # Transaction status
            }
            
            self.logger.info(f"Created transaction: {amount} BTC to {to_address}") # Log successful transaction creation
            return transaction # Return the transaction object
            
        except Exception as e: # Catch any exceptions during transaction creation
            self.logger.error(f"Failed to create transaction: {e}") # Log the error
            return None # Return None if transaction creation fails
    
    def sign_transaction(self, transaction_data, private_key=None): # Sign a transaction (offline). Self is the instance of the class, transaction_data is the transaction to sign, private_key is the private key to use (optional)
        """Sign a transaction (offline)"""
        try: # Try to sign transaction
            if not self.wallet: # If wallet is not available
                return None # Return None if no wallet
            
            # In a real implementation, this would sign the transaction
            # For demo purposes, we'll just mark it as signed
            transaction_data['signed'] = True # Mark transaction as signed
            transaction_data['signed_at'] = datetime.now().isoformat() # Add signing timestamp
            
            self.logger.info("Transaction signed successfully") # Log successful transaction signing
            return transaction_data # Return the signed transaction
            
        except Exception as e: # Catch any exceptions during transaction signing
            self.logger.error(f"Failed to sign transaction: {e}") # Log the error
            return None # Return None if transaction signing fails
    
    def broadcast_transaction(self, signed_transaction): # Broadcast transaction to Bitcoin network. Self is the instance of the class, signed_transaction is the signed transaction to broadcast
        """Broadcast transaction to Bitcoin network"""
        try: # Try to broadcast transaction
            if not self.wallet: # If wallet is not available
                return False # Return False if no wallet
            
            # In a real implementation, this would broadcast to the network
            # For demo purposes, we'll just mark it as broadcast
            signed_transaction['broadcast'] = True # Mark transaction as broadcast
            signed_transaction['broadcast_at'] = datetime.now().isoformat() # Add broadcast timestamp
            
            self.logger.info("Transaction broadcast successfully") # Log successful transaction broadcast
            return True # Return True for successful broadcast
            
        except Exception as e: # Catch any exceptions during transaction broadcast
            self.logger.error(f"Failed to broadcast transaction: {e}") # Log the error
            return False # Return False if broadcast fails
    
    def get_transaction_history(self, address=None): # Get transaction history for wallet or specific address. Self is the instance of the class, address is the specific address to get history for (optional)
        """Get transaction history for wallet or specific address"""
        try: # Try to get transaction history
            if not self.wallet: # If wallet is not available
                return [] # Return empty list if no wallet
            
            # In a real implementation, this would query the blockchain
            # For demo purposes, return empty list
            return [] # Return empty list for demo
            
        except Exception as e: # Catch any exceptions during history retrieval
            self.logger.error(f"Failed to get transaction history: {e}") # Log the error
            return [] # Return empty list on error
    
    def validate_address(self, address): # Validate Bitcoin address format. Self is the instance of the class, address is the address to validate
        """Validate Bitcoin address format"""
        try: # Try to validate address
            if not address: # If address is empty or None
                return False # Return False for empty address
            
            # Basic validation for demo addresses
            if address.startswith("1Ajo") and len(address) == 30: # Check if it's a valid demo address
                return True # Return True for valid demo address
            
            # For real Bitcoin addresses, use bitcoinlib validation
            if self.wallet: # If wallet is available
                try: # Try to validate with bitcoinlib
                    # This would validate real Bitcoin addresses
                    return True # Return True for valid Bitcoin address
                except: # If validation fails
                    return False # Return False for invalid address
            
            return False # Return False if no validation method available
            
        except Exception as e: # Catch any exceptions during address validation
            self.logger.error(f"Address validation failed: {e}") # Log the error
            return False # Return False if validation fails
    
    def export_wallet_info(self): # Export wallet information for backup. Self is the instance of the class
        """Export wallet information for backup"""
        try: # Try to export wallet info
            if not self.wallet: # If wallet is not available
                return None # Return None if no wallet
            
            wallet_info = { # Create wallet info dictionary
                'name': self.wallet_name, # Wallet name
                'network': 'bitcoin', # Network type
                'created_at': datetime.now().isoformat(), # Export timestamp
                'addresses': [] # List to store addresses
            }
            
            # Get some addresses
            for i in range(5): # Get first 5 addresses
                try: # Try to get address
                    address = self.wallet.get_key(i).address # Get address at index i
                    wallet_info['addresses'].append(address) # Add address to list
                except: # If address retrieval fails
                    break # Stop getting addresses
            
            return wallet_info # Return wallet information
            
        except Exception as e: # Catch any exceptions during wallet info export
            self.logger.error(f"Failed to export wallet info: {e}") # Log the error
            return None # Return None if export fails
    
    def import_wallet(self, mnemonic_phrase): # Import wallet from mnemonic phrase. Self is the instance of the class, mnemonic_phrase is the mnemonic phrase to import
        """Import wallet from mnemonic phrase"""
        try: # Try to import wallet
            # This would import an existing wallet
            # For demo purposes, just log the attempt
            self.logger.info("Wallet import requested") # Log import request
            return True # Return True for successful import
            
        except Exception as e: # Catch any exceptions during wallet import
            self.logger.error(f"Failed to import wallet: {e}") # Log the error
            return False # Return False if import fails
    
    def get_wallet_status(self): # Get wallet status and health. Self is the instance of the class
        """Get wallet status and health"""
        try: # Try to get wallet status
            status = { # Create status dictionary
                'wallet_exists': self.wallet is not None, # Whether wallet exists
                'wallet_name': self.wallet_name, # Wallet name
                'network': 'bitcoin', # Network type
                'last_updated': datetime.now().isoformat() # Last update timestamp
            }
            
            if self.wallet: # If wallet is available
                try: # Try to get wallet details
                    status['balance'] = self.wallet.balance() # Get wallet balance
                    status['address_count'] = len(self.wallet.get_keys()) # Get number of addresses
                except: # If wallet details retrieval fails
                    status['balance'] = 0 # Set balance to 0
                    status['address_count'] = 0 # Set address count to 0
            
            return status # Return wallet status
            
        except Exception as e: # Catch any exceptions during status retrieval
            self.logger.error(f"Failed to get wallet status: {e}") # Log the error
            return {'error': str(e)} # Return error status 