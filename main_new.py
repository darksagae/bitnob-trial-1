#!/usr/bin/env python3
"""
Main entry point for Ajo Bitcoin Savings App
Role-based UI initialization with separate AdminUI and UserUI
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Optional
import config
from database_new import Database
from api_new import BitnobAPI
from ui_new import LoginUI, AdminUI, UserUI

# Setup logging
def setup_logging():
    """Setup application logging"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

class AjoApp:
    """Main application class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.database = None
        self.api = None
        self.current_user = None
        
        # Setup directories
        self.setup_directories()
        
        # Initialize components
        self.initialize_database()
        self.initialize_api()
        
        # Setup demo data if needed
        if config.DEMO_MODE:
            self.setup_demo_data()
        
        self.logger.info("Ajo app initialized successfully")
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            'logs',
            'backups',
            'exports',
            'temp',
            'assets'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")
    
    def initialize_database(self):
        """Initialize database connection"""
        try:
            self.database = Database()
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def initialize_api(self):
        """Initialize API client"""
        try:
            self.api = BitnobAPI()
            self.logger.info("API client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize API client: {e}")
            raise
    
    def setup_demo_data(self):
        """Setup demo data for testing"""
        try:
            # Create demo admin user
            admin_id = self.database.create_user(
                username="admin",
                password="admin123",
                role="admin",
                full_name="System Administrator",
                phone_number="+256700000000",
                email="admin@ajo.com"
            )
            
            # Create demo regular user
            user_id = self.database.create_user(
                username="user",
                password="user123",
                role="user",
                full_name="Demo User",
                phone_number="+256700000001",
                email="user@ajo.com"
            )
            
            # Create demo group
            group_id = self.database.create_group(
                name="Demo Savings Group",
                description="A demo group for testing the Ajo app",
                admin_user_id=admin_id
            )
            
            # Add user to group
            if group_id and user_id:
                self.database.add_user_to_group(user_id, group_id)
            
            # Add some demo contributions
            if group_id and user_id:
                self.database.add_contribution(
                    user_id=user_id,
                    group_id=group_id,
                    amount=50000.0,  # 50,000 UGX
                    payment_method="mobile_money",
                    payment_reference="+256700000001"
                )
                
                self.database.add_contribution(
                    user_id=user_id,
                    group_id=group_id,
                    amount=100000.0,  # 100,000 UGX
                    payment_method="bitcoin",
                    payment_reference="demo_btc_tx"
                )
            
            # Add demo payout
            if group_id and user_id:
                self.database.add_payout(
                    group_id=group_id,
                    user_id=user_id,
                    amount=25000.0,  # 25,000 UGX
                    payment_method="mobile_money",
                    payment_reference="+256700000001"
                )
            
            self.logger.info("Demo data setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup demo data: {e}")
    
    def on_login_success(self, user_data: Dict):
        """Handle successful login"""
        self.current_user = user_data
        self.logger.info(f"User logged in: {user_data['username']} ({user_data['role']})")
        
        # Launch appropriate UI based on user role
        if user_data['role'] == 'admin':
            self.launch_admin_ui()
        else:
            self.launch_user_ui()
    
    def launch_admin_ui(self):
        """Launch admin interface"""
        try:
            admin_ui = AdminUI(self.database, self.api, self.current_user)
            admin_ui.run()
        except Exception as e:
            self.logger.error(f"Failed to launch admin UI: {e}")
            self.show_error("Failed to launch admin interface", str(e))
    
    def launch_user_ui(self):
        """Launch user interface"""
        try:
            user_ui = UserUI(self.database, self.api, self.current_user)
            user_ui.run()
        except Exception as e:
            self.logger.error(f"Failed to launch user UI: {e}")
            self.show_error("Failed to launch user interface", str(e))
    
    def show_error(self, title: str, message: str):
        """Show error message"""
        import tkinter.messagebox as messagebox
        messagebox.showerror(title, message)
    
    def run(self):
        """Start the application"""
        try:
            # Show login window
            login_ui = LoginUI(self.database, self.on_login_success)
            login_ui.run()
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            self.show_error("Application Error", f"Failed to start application: {str(e)}")

def main():
    """Main entry point"""
    try:
        # Setup logging
        setup_logging()
        
        # Create and run app
        app = AjoApp()
        app.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 