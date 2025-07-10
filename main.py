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

import os # Operating system interface for file and directory operations
import sys # System-specific parameters and functions for exit codes and command line arguments
import logging # Logging for error tracking, debugging and monitoring application events
import threading # Threading for background operations and parallel processing like syncing and background tasks without freezing the UI
import time # Time-related functions for delays and timestamps
from datetime import datetime # Date and time handling for transaction timestamps and file naming
from pathlib import Path # Object-oriented filesystem paths for cross-platform directory operations

# Import our custom modules
from database import AjoDatabase # Database operations for local savings storage and member management
from wallet import BitcoinWallet # Bitcoin wallet management for address generation and transaction handling
from api import BitnobAPI # Bitnob API integration for online sync and mobile money operations
from ui import UserUI, AdminUI # User interface for desktop application

class AjoApp: # Main application class that coordinates all Ajo functionality
    """Main application class that coordinates all Ajo functionality"""
    
    def __init__(self): # Initialize the Ajo application with all components. Self is the instance of the class
        """Initialize the Ajo application with all components"""
        self.setup_logging() # Configure logging for the application with file and console handlers
        self.logger = logging.getLogger(__name__) # Logger for the main application class
        
        # Create necessary directories for logs, wallets, and backups
        self.create_directories() # Create logs, wallets, and backups directories if they don't exist
        
        # Initialize components
        self.database = AjoDatabase() # Database instance for local data storage and retrieval
        self.wallet = BitcoinWallet(self.database) # Bitcoin wallet instance for address generation and transaction management
        self.api = BitnobAPI(self.database) # Bitnob API instance for online operations and mobile money integration
        self.ui = None # User interface instance, initialized later when UI is started
        
        # Offline transaction queue for storing pending transactions when offline
        self.pending_transactions = [] # List to store transactions that need to be synced when online
        self.sync_thread = None # Background thread for periodic syncing with Bitnob API
        self.is_syncing = False # Flag to prevent multiple simultaneous sync operations
        
        self.logger.info("Ajo Bitcoin Savings App initialized successfully") # Log successful initialization
    
    def setup_logging(self): # Configure logging for the application. Self is the instance of the class
        """Configure logging for the application"""
        log_dir = Path("logs") # Create logs directory path
        log_dir.mkdir(exist_ok=True) # Create logs directory if it doesn't exist
        
        logging.basicConfig( # Configure basic logging settings
            level=logging.INFO, # Set logging level to INFO for detailed logging
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Format for log messages with timestamp, module name, level, and message
            handlers=[ # List of logging handlers
                logging.FileHandler(log_dir / f"ajo_{datetime.now().strftime('%Y%m%d')}.log"), # File handler for daily log files
                logging.StreamHandler(sys.stdout) # Console handler for immediate output
            ]
        )
    
    def create_directories(self): # Create necessary application directories. Self is the instance of the class
        """Create necessary application directories"""
        directories = ["logs", "wallets", "backups"] # List of directories needed for the application
        for directory in directories: # Iterate through each directory
            Path(directory).mkdir(exist_ok=True) # Create directory if it doesn't exist, ignore if it does
    
    def start_ui(self): # Launch the user interface. Self is the instance of the class
        """Launch the user interface"""
        try: # Try to start the user interface
            self.ui = UserUI(self) # Create user interface instance with reference to this app
            self.ui.run() # Start the UI main loop
        except Exception as e: # Catch any exceptions during UI startup
            self.logger.error(f"Failed to start UI: {e}") # Log the error
            print(f"Error starting UI: {e}") # Print error message to console
    
    def add_contribution(self, member_name, amount, contribution_type="bitcoin"): # Add a new contribution to the savings group. Self is the instance of the class, member_name is the name of the member, amount is the contribution amount, contribution_type is the type of contribution (default is bitcoin)
        """Add a new contribution to the savings group"""
        try: # Try to add the contribution
            # Generate Bitcoin address if needed
            if contribution_type == "bitcoin": # If contribution type is bitcoin
                address = self.wallet.generate_address() # Generate a new Bitcoin address for the contribution
            else: # If contribution type is not bitcoin
                address = None # No Bitcoin address needed
            
            # Store in database
            contribution_id = self.database.add_contribution( # Add contribution to database and get the contribution ID
                member_name=member_name, # Member name for the contribution
                amount=amount, # Amount of the contribution
                contribution_type=contribution_type, # Type of contribution (bitcoin, usdt, ugx)
                bitcoin_address=address # Bitcoin address if applicable
            )
            
            # Add to pending transactions for API sync
            self.pending_transactions.append({ # Add transaction to pending queue for later sync
                'id': contribution_id, # Contribution ID from database
                'type': 'contribution', # Type of transaction
                'member_name': member_name, # Member name
                'amount': amount, # Contribution amount
                'contribution_type': contribution_type, # Type of contribution
                'bitcoin_address': address, # Bitcoin address if applicable
                'timestamp': datetime.now().isoformat() # Current timestamp in ISO format
            })
            
            self.logger.info(f"Added contribution: {member_name} - {amount} {contribution_type}") # Log successful contribution addition
            return contribution_id # Return the contribution ID
            
        except Exception as e: # Catch any exceptions during contribution addition
            self.logger.error(f"Failed to add contribution: {e}") # Log the error
            raise # Re-raise the exception for handling by caller
    
    def get_savings_summary(self): # Get current savings group summary. Self is the instance of the class
        """Get current savings group summary"""
        try: # Try to get savings summary
            return self.database.get_savings_summary() # Return savings summary from database
        except Exception as e: # Catch any exceptions during summary retrieval
            self.logger.error(f"Failed to get savings summary: {e}") # Log the error
            return None # Return None if summary retrieval fails
    
    def sync_with_bitnob(self): # Sync pending transactions with Bitnob API. Self is the instance of the class
        """Sync pending transactions with Bitnob API"""
        if self.is_syncing: # If already syncing, don't start another sync
            return # Exit early to prevent multiple simultaneous syncs
        
        self.is_syncing = True # Set syncing flag to prevent multiple syncs
        try: # Try to sync with Bitnob
            if not self.api.is_online(): # Check if internet connection is available
                self.logger.info("No internet connection, skipping sync") # Log that sync is skipped due to no internet
                return # Exit early if no internet connection
            
            # Process pending transactions
            for transaction in self.pending_transactions[:]: # Iterate through a copy of pending transactions list
                try: # Try to process each transaction
                    if transaction['type'] == 'contribution': # If transaction is a contribution
                        success = self.api.record_contribution( # Record contribution with Bitnob API
                            member_name=transaction['member_name'], # Member name from transaction
                            amount=transaction['amount'], # Amount from transaction
                            contribution_type=transaction['contribution_type'], # Contribution type from transaction
                            bitcoin_address=transaction['bitcoin_address'] # Bitcoin address from transaction
                        )
                        
                        if success: # If API call was successful
                            # Mark as synced in database
                            self.database.mark_contribution_synced(transaction['id']) # Mark contribution as synced in database
                            self.pending_transactions.remove(transaction) # Remove transaction from pending queue
                            self.logger.info(f"Synced transaction: {transaction['id']}") # Log successful sync
                    
                except Exception as e: # Catch any exceptions during transaction processing
                    self.logger.error(f"Failed to sync transaction {transaction['id']}: {e}") # Log the error
            
            # Update local data from Bitnob
            self.update_local_data() # Update local data with latest information from Bitnob
            
        except Exception as e: # Catch any exceptions during sync process
            self.logger.error(f"Sync failed: {e}") # Log the error
        finally: # Always execute this block
            self.is_syncing = False # Reset syncing flag
    
    def update_local_data(self): # Update local data from Bitnob API. Self is the instance of the class
        """Update local data from Bitnob API"""
        try: # Try to update local data
            # Get latest exchange rates
            rates = self.api.get_exchange_rates() # Get current exchange rates from Bitnob API
            if rates: # If rates were successfully retrieved
                self.database.update_exchange_rates(rates) # Update exchange rates in local database
            
            # Get user balance if authenticated
            balance = self.api.get_user_balance() # Get user balance from Bitnob API
            if balance: # If balance was successfully retrieved
                self.database.update_user_balance(balance) # Update user balance in local database
                
        except Exception as e: # Catch any exceptions during data update
            self.logger.error(f"Failed to update local data: {e}") # Log the error
    
    def start_background_sync(self): # Start background sync thread. Self is the instance of the class
        """Start background sync thread"""
        def sync_loop(): # Inner function for the sync loop
            while True: # Infinite loop for continuous syncing
                try: # Try to sync
                    self.sync_with_bitnob() # Perform sync with Bitnob
                    time.sleep(300)  # Sync every 5 minutes (300 seconds)
                except Exception as e: # Catch any exceptions during sync
                    self.logger.error(f"Background sync error: {e}") # Log the error
                    time.sleep(60)  # Wait 1 minute on error before retrying
        
        self.sync_thread = threading.Thread(target=sync_loop, daemon=True) # Create background thread with daemon=True so it stops when main program exits
        self.sync_thread.start() # Start the background sync thread
        self.logger.info("Background sync started") # Log that background sync has started
    
    def process_mobile_money_payout(self, member_name, amount, phone_number): # Process mobile money payout via Bitnob API. Self is the instance of the class, member_name is the name of the member, amount is the payout amount, phone_number is the recipient's phone number
        """Process mobile money payout via Bitnob API"""
        try: # Try to process the payout
            if not self.api.is_online(): # Check if internet connection is available
                # Queue for later processing
                self.pending_transactions.append({ # Add payout to pending transactions queue
                    'type': 'payout', # Type of transaction
                    'member_name': member_name, # Member name
                    'amount': amount, # Payout amount
                    'phone_number': phone_number, # Recipient phone number
                    'timestamp': datetime.now().isoformat() # Current timestamp
                })
                return False, "Queued for processing when online" # Return failure status with message
            
            success = self.api.process_mobile_money_payout( # Process payout with Bitnob API
                amount=amount, # Payout amount
                phone_number=phone_number, # Recipient phone number
                description=f"Ajo payout for {member_name}" # Description for the payout
            )
            
            if success: # If payout was successful
                self.database.record_payout(member_name, amount, phone_number) # Record payout in local database
                return True, "Payout processed successfully" # Return success status with message
            else: # If payout failed
                return False, "Payout failed" # Return failure status with message
                
        except Exception as e: # Catch any exceptions during payout processing
            self.logger.error(f"Payout processing failed: {e}") # Log the error
            return False, f"Error: {str(e)}" # Return failure status with error message
    
    def export_savings_report(self, filename=None): # Export savings report to CSV. Self is the instance of the class, filename is the output filename (optional)
        """Export savings report to CSV"""
        try: # Try to export the report
            if not filename: # If no filename provided
                filename = f"ajo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv" # Generate filename with current timestamp
            
            report_data = self.database.export_savings_report() # Get report data from database
            
            with open(filename, 'w', newline='', encoding='utf-8') as f: # Open file for writing with UTF-8 encoding
                f.write("Member Name,Amount,Contribution Type,Date,Bitcoin Address\n") # Write CSV header
                for row in report_data: # Iterate through each row of data
                    f.write(f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4] or ''}\n") # Write CSV row with empty string for None values
            
            self.logger.info(f"Report exported to {filename}") # Log successful export
            return filename # Return the filename
            
        except Exception as e: # Catch any exceptions during report export
            self.logger.error(f"Failed to export report: {e}") # Log the error
            return None # Return None if export failed

def main(): # Main entry point for the Ajo application
    """Main entry point for the Ajo application"""
    print("🚀 Starting Ajo Bitcoin Savings App...") # Print startup message
    print("💰 Empowering Uganda through Bitcoin-based group savings") # Print tagline
    print("=" * 60) # Print separator line
    
    try: # Try to start the application
        # Initialize logging
        logging.basicConfig(
            filename='logs/app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize core app components
        database = AjoDatabase()
        api = BitnobAPI(database)
        wallet = BitcoinWallet()
        
        # Dummy login prompt (replace with your actual login logic)
        print("Welcome to Ajo Bitcoin Group Savings App!")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        # Check role (replace with your actual authentication/role logic)
        # For demo: if username is 'admin', treat as admin
        if username.lower() == 'admin':
            print("Launching Admin Interface...")
            app = type('App', (), {'database': database, 'api': api, 'wallet': wallet})()
            AdminUI(app).run()
        else:
            print("Launching User Interface...")
            app = type('App', (), {'database': database, 'api': api, 'wallet': wallet})()
            UserUI(app).run()
        
    except KeyboardInterrupt: # Handle user interruption (Ctrl+C)
        print("\n👋 Ajo app closed by user") # Print goodbye message
    except Exception as e: # Catch any other exceptions
        print(f"❌ Fatal error: {e}") # Print error message
        logging.error(f"Application failed to start: {e}") # Log the fatal error
        sys.exit(1) # Exit with error code 1

if __name__ == "__main__": # Check if this script is run directly
    main() # Call the main function 