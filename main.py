#!/usr/bin/env python3
"""
Ajo - Bitcoin-based Group Savings App for Uganda
Bitnob Hackathon Entry

Main application orchestrator that coordinates all modules:
- Database operations for local savings storage
- Bitcoin wallet management
- Bitnob API integration
- User interface
- Offline transaction queue management
"""

import os
import sys
import logging
import threading
import time
from datetime import datetime
from pathlib import Path

# Import our custom modules
from database import AjoDatabase
from wallet import BitcoinWallet
from api import BitnobAPI
from ui import AjoUI

class AjoApp:
    """Main application class that coordinates all Ajo functionality"""
    
    def __init__(self):
        """Initialize the Ajo application with all components"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Create necessary directories
        self.create_directories()
        
        # Initialize components
        self.database = AjoDatabase()
        self.wallet = BitcoinWallet()
        self.api = BitnobAPI()
        self.ui = None
        
        # Offline transaction queue
        self.pending_transactions = []
        self.sync_thread = None
        self.is_syncing = False
        
        self.logger.info("Ajo Bitcoin Savings App initialized successfully")
    
    def setup_logging(self):
        """Configure logging for the application"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"ajo_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def create_directories(self):
        """Create necessary application directories"""
        directories = ["logs", "wallets", "backups"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def start_ui(self):
        """Launch the user interface"""
        try:
            self.ui = AjoUI(self)
            self.ui.run()
        except Exception as e:
            self.logger.error(f"Failed to start UI: {e}")
            print(f"Error starting UI: {e}")
    
    def add_contribution(self, member_name, amount, contribution_type="bitcoin"):
        """Add a new contribution to the savings group"""
        try:
            # Generate Bitcoin address if needed
            if contribution_type == "bitcoin":
                address = self.wallet.generate_address()
            else:
                address = None
            
            # Store in database
            contribution_id = self.database.add_contribution(
                member_name=member_name,
                amount=amount,
                contribution_type=contribution_type,
                bitcoin_address=address
            )
            
            # Add to pending transactions for API sync
            self.pending_transactions.append({
                'id': contribution_id,
                'type': 'contribution',
                'member_name': member_name,
                'amount': amount,
                'contribution_type': contribution_type,
                'bitcoin_address': address,
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"Added contribution: {member_name} - {amount} {contribution_type}")
            return contribution_id
            
        except Exception as e:
            self.logger.error(f"Failed to add contribution: {e}")
            raise
    
    def get_savings_summary(self):
        """Get current savings group summary"""
        try:
            return self.database.get_savings_summary()
        except Exception as e:
            self.logger.error(f"Failed to get savings summary: {e}")
            return None
    
    def sync_with_bitnob(self):
        """Sync pending transactions with Bitnob API"""
        if self.is_syncing:
            return
        
        self.is_syncing = True
        try:
            if not self.api.is_online():
                self.logger.info("No internet connection, skipping sync")
                return
            
            # Process pending transactions
            for transaction in self.pending_transactions[:]:
                try:
                    if transaction['type'] == 'contribution':
                        success = self.api.record_contribution(
                            member_name=transaction['member_name'],
                            amount=transaction['amount'],
                            contribution_type=transaction['contribution_type'],
                            bitcoin_address=transaction['bitcoin_address']
                        )
                        
                        if success:
                            # Mark as synced in database
                            self.database.mark_contribution_synced(transaction['id'])
                            self.pending_transactions.remove(transaction)
                            self.logger.info(f"Synced transaction: {transaction['id']}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to sync transaction {transaction['id']}: {e}")
            
            # Update local data from Bitnob
            self.update_local_data()
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
        finally:
            self.is_syncing = False
    
    def update_local_data(self):
        """Update local data from Bitnob API"""
        try:
            # Get latest exchange rates
            rates = self.api.get_exchange_rates()
            if rates:
                self.database.update_exchange_rates(rates)
            
            # Get user balance if authenticated
            balance = self.api.get_user_balance()
            if balance:
                self.database.update_user_balance(balance)
                
        except Exception as e:
            self.logger.error(f"Failed to update local data: {e}")
    
    def start_background_sync(self):
        """Start background sync thread"""
        def sync_loop():
            while True:
                try:
                    self.sync_with_bitnob()
                    time.sleep(300)  # Sync every 5 minutes
                except Exception as e:
                    self.logger.error(f"Background sync error: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        self.sync_thread = threading.Thread(target=sync_loop, daemon=True)
        self.sync_thread.start()
        self.logger.info("Background sync started")
    
    def process_mobile_money_payout(self, member_name, amount, phone_number):
        """Process mobile money payout via Bitnob API"""
        try:
            if not self.api.is_online():
                # Queue for later processing
                self.pending_transactions.append({
                    'type': 'payout',
                    'member_name': member_name,
                    'amount': amount,
                    'phone_number': phone_number,
                    'timestamp': datetime.now().isoformat()
                })
                return False, "Queued for processing when online"
            
            success = self.api.process_mobile_money_payout(
                amount=amount,
                phone_number=phone_number,
                description=f"Ajo payout for {member_name}"
            )
            
            if success:
                self.database.record_payout(member_name, amount, phone_number)
                return True, "Payout processed successfully"
            else:
                return False, "Payout failed"
                
        except Exception as e:
            self.logger.error(f"Payout processing failed: {e}")
            return False, f"Error: {str(e)}"
    
    def export_savings_report(self, filename=None):
        """Export savings report to CSV"""
        try:
            if not filename:
                filename = f"ajo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            report_data = self.database.export_savings_report()
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                f.write("Member Name,Amount,Contribution Type,Date,Bitcoin Address\n")
                for row in report_data:
                    f.write(f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4] or ''}\n")
            
            self.logger.info(f"Report exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to export report: {e}")
            return None

def main():
    """Main entry point for the Ajo application"""
    print("🚀 Starting Ajo Bitcoin Savings App...")
    print("💰 Empowering Uganda through Bitcoin-based group savings")
    print("=" * 60)
    
    try:
        # Initialize the application
        app = AjoApp()
        
        # Start background sync
        app.start_background_sync()
        
        # Launch the user interface
        app.start_ui()
        
    except KeyboardInterrupt:
        print("\n👋 Ajo app closed by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.error(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 