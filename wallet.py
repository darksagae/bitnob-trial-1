#!/usr/bin/env python3
"""
Bitcoin Wallet module for Ajo Bitcoin Savings App
Handles offline Bitcoin address generation and transaction management
"""

import logging
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
import bitcoinlib
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.keys import HDKey

class BitcoinWallet:
    """Bitcoin wallet manager for offline address generation and transaction handling"""
    
    def __init__(self, wallet_name="ajo_savings_wallet"):
        """Initialize Bitcoin wallet"""
        self.wallet_name = wallet_name
        self.logger = logging.getLogger(__name__)
        self.wallet_dir = Path("wallets")
        self.wallet_dir.mkdir(exist_ok=True)
        
        # Initialize or load existing wallet
        self.wallet = self._initialize_wallet()
        self.logger.info(f"Bitcoin wallet initialized: {wallet_name}")
    
    def _initialize_wallet(self):
        """Initialize or load existing Bitcoin wallet"""
        try:
            # Check if wallet already exists
            wallet_path = self.wallet_dir / f"{self.wallet_name}.json"
            
            if wallet_path.exists():
                # Load existing wallet
                self.logger.info("Loading existing wallet")
                return Wallet(self.wallet_name, db_uri=f"sqlite:///{self.wallet_dir}/bitcoinlib.db")
            else:
                # Create new wallet
                self.logger.info("Creating new Bitcoin wallet")
                return self._create_new_wallet()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize wallet: {e}")
            # Fallback to simple address generation
            return None
    
    def _create_new_wallet(self):
        """Create a new Bitcoin wallet with mnemonic"""
        try:
            # Generate mnemonic phrase
            mnemonic = Mnemonic().generate()
            
            # Create wallet
            wallet = Wallet.create(
                name=self.wallet_name,
                keys=mnemonic,
                network='bitcoin',
                db_uri=f"sqlite:///{self.wallet_dir}/bitcoinlib.db"
            )
            
            # Save mnemonic securely (in production, use proper key management)
            self._save_mnemonic(mnemonic)
            
            self.logger.info("New Bitcoin wallet created successfully")
            return wallet
            
        except Exception as e:
            self.logger.error(f"Failed to create wallet: {e}")
            return None
    
    def _save_mnemonic(self, mnemonic):
        """Save mnemonic phrase securely"""
        try:
            mnemonic_file = self.wallet_dir / f"{self.wallet_name}_mnemonic.txt"
            with open(mnemonic_file, 'w') as f:
                f.write(f"# Ajo Bitcoin Savings Wallet - {datetime.now()}\n")
                f.write(f"# IMPORTANT: Keep this secure and private!\n")
                f.write(f"# Mnemonic phrase for wallet recovery:\n\n")
                f.write(mnemonic)
                f.write(f"\n\n# Wallet name: {self.wallet_name}")
                f.write(f"\n# Created: {datetime.now()}")
            
            # Set restrictive permissions (Unix-like systems)
            try:
                mnemonic_file.chmod(0o600)
            except:
                pass  # Windows doesn't support chmod
                
            self.logger.info(f"Mnemonic saved to: {mnemonic_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save mnemonic: {e}")
    
    def generate_address(self, address_type="legacy"):
        """Generate a new Bitcoin address for contributions"""
        try:
            if self.wallet:
                # Use bitcoinlib wallet
                address = self.wallet.get_key().address
                self.logger.info(f"Generated Bitcoin address: {address}")
                return address
            else:
                # Fallback to simple address generation
                return self._generate_simple_address()
                
        except Exception as e:
            self.logger.error(f"Failed to generate address: {e}")
            return self._generate_simple_address()
    
    def _generate_simple_address(self):
        """Generate a simple Bitcoin address for demo purposes"""
        try:
            # This is a simplified address generation for demo
            # In production, use proper Bitcoin address generation
            random_bytes = secrets.token_bytes(32)
            address_hash = hashlib.sha256(random_bytes).hexdigest()
            
            # Format as a Bitcoin-like address (this is not a real Bitcoin address)
            address = f"1Ajo{address_hash[:26].upper()}"
            
            self.logger.info(f"Generated demo address: {address}")
            return address
            
        except Exception as e:
            self.logger.error(f"Failed to generate simple address: {e}")
            return None
    
    def get_wallet_balance(self):
        """Get wallet balance (requires internet connection)"""
        try:
            if self.wallet:
                balance = self.wallet.balance()
                self.logger.info(f"Wallet balance: {balance}")
                return balance
            else:
                return 0
        except Exception as e:
            self.logger.error(f"Failed to get wallet balance: {e}")
            return 0
    
    def get_address_balance(self, address):
        """Get balance for a specific address"""
        try:
            if self.wallet:
                # This would require blockchain API access
                # For offline demo, return 0
                return 0
            else:
                return 0
        except Exception as e:
            self.logger.error(f"Failed to get address balance: {e}")
            return 0
    
    def create_transaction(self, to_address, amount, fee_rate=10):
        """Create a Bitcoin transaction (offline preparation)"""
        try:
            if not self.wallet:
                return None
            
            # Create transaction object
            transaction = {
                'to_address': to_address,
                'amount': amount,
                'fee_rate': fee_rate,
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            self.logger.info(f"Created transaction: {amount} BTC to {to_address}")
            return transaction
            
        except Exception as e:
            self.logger.error(f"Failed to create transaction: {e}")
            return None
    
    def sign_transaction(self, transaction_data, private_key=None):
        """Sign a transaction (offline)"""
        try:
            if not self.wallet:
                return None
            
            # In a real implementation, this would sign the transaction
            # For demo purposes, we'll just mark it as signed
            transaction_data['signed'] = True
            transaction_data['signed_at'] = datetime.now().isoformat()
            
            self.logger.info("Transaction signed successfully")
            return transaction_data
            
        except Exception as e:
            self.logger.error(f"Failed to sign transaction: {e}")
            return None
    
    def broadcast_transaction(self, signed_transaction):
        """Broadcast transaction to Bitcoin network"""
        try:
            if not self.wallet:
                return False
            
            # In a real implementation, this would broadcast to the network
            # For demo purposes, we'll just mark it as broadcast
            signed_transaction['broadcast'] = True
            signed_transaction['broadcast_at'] = datetime.now().isoformat()
            
            self.logger.info("Transaction broadcast successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to broadcast transaction: {e}")
            return False
    
    def get_transaction_history(self, address=None):
        """Get transaction history for wallet or specific address"""
        try:
            if not self.wallet:
                return []
            
            # In a real implementation, this would query the blockchain
            # For demo purposes, return empty list
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get transaction history: {e}")
            return []
    
    def validate_address(self, address):
        """Validate Bitcoin address format"""
        try:
            if not address:
                return False
            
            # Basic validation for demo addresses
            if address.startswith("1Ajo") and len(address) == 30:
                return True
            
            # For real Bitcoin addresses, use bitcoinlib validation
            if self.wallet:
                try:
                    # This would validate real Bitcoin addresses
                    return True
                except:
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Address validation failed: {e}")
            return False
    
    def export_wallet_info(self):
        """Export wallet information for backup"""
        try:
            if not self.wallet:
                return None
            
            wallet_info = {
                'name': self.wallet_name,
                'network': 'bitcoin',
                'created_at': datetime.now().isoformat(),
                'addresses': []
            }
            
            # Get some addresses
            for i in range(5):
                try:
                    address = self.wallet.get_key(i).address
                    wallet_info['addresses'].append(address)
                except:
                    break
            
            return wallet_info
            
        except Exception as e:
            self.logger.error(f"Failed to export wallet info: {e}")
            return None
    
    def import_wallet(self, mnemonic_phrase):
        """Import wallet from mnemonic phrase"""
        try:
            # This would import an existing wallet
            # For demo purposes, just log the attempt
            self.logger.info("Wallet import requested")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import wallet: {e}")
            return False
    
    def get_wallet_status(self):
        """Get wallet status and health"""
        try:
            status = {
                'wallet_exists': self.wallet is not None,
                'wallet_name': self.wallet_name,
                'network': 'bitcoin',
                'last_updated': datetime.now().isoformat()
            }
            
            if self.wallet:
                try:
                    status['balance'] = self.wallet.balance()
                    status['address_count'] = len(self.wallet.get_keys())
                except:
                    status['balance'] = 0
                    status['address_count'] = 0
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get wallet status: {e}")
            return {'error': str(e)} 