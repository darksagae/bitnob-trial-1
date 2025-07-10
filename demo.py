#!/usr/bin/env python3
"""
Demo script for Ajo Bitcoin Savings App
Creates sample data and demonstrates all features for hackathon presentation
"""

import sys # System-specific parameters and functions for exit codes and command line arguments
import time # Time-related functions for delays and timestamps
import logging # Logging for error tracking, debugging and monitoring demo operations
from datetime import datetime, timedelta # Date and time handling for timestamps and date calculations
from pathlib import Path # Object-oriented filesystem paths for cross-platform directory operations

# Import our modules
from main import AjoApp # Main application class for coordinating all functionality
from database import AjoDatabase # Database operations for local savings storage
from wallet import BitcoinWallet # Bitcoin wallet management for address generation
from api import BitnobAPI # Bitnob API integration for online operations

def setup_demo_logging(): # Setup logging for demo. No parameters, configures logging for demo operations
    """Setup logging for demo"""
    logging.basicConfig( # Configure basic logging settings
        level=logging.INFO, # Set logging level to INFO for detailed logging
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Format for log messages with timestamp, module name, level, and message
        handlers=[ # List of logging handlers
            logging.StreamHandler(sys.stdout) # Console handler for immediate output
        ]
    )

def create_sample_data(app): # Create sample data for demonstration. App is the instance of AjoApp
    """Create sample data for demonstration"""
    print("🎯 Creating sample data for demonstration...") # Print status message
    
    # Sample members
    members = [ # List of sample member dictionaries
        {"name": "Sarah Nakimera", "phone": "+256701234567", "email": "sarah@example.com"}, # Sample member 1
        {"name": "John Muwonge", "phone": "+256702345678", "email": "john@example.com"}, # Sample member 2
        {"name": "Grace Nalukenge", "phone": "+256703456789", "email": "grace@example.com"}, # Sample member 3
        {"name": "David Ssewanyana", "phone": "+256704567890", "email": "david@example.com"}, # Sample member 4
        {"name": "Mary Namukasa", "phone": "+256705678901", "email": "mary@example.com"} # Sample member 5
    ]
    
    # Add members
    for member in members: # Iterate through each sample member
        app.database.add_member( # Add member to database
            name=member["name"], # Member name
            phone_number=member["phone"], # Member phone number
            email=member["email"] # Member email
        )
        print(f"✅ Added member: {member['name']}") # Print success message
    
    # Sample contributions
    contributions = [ # List of sample contribution dictionaries
        {"member": "Sarah Nakimera", "amount": 0.001, "type": "bitcoin", "notes": "Weekly savings"}, # Bitcoin contribution
        {"member": "John Muwonge", "amount": 50000, "type": "ugx", "notes": "Monthly contribution"}, # UGX contribution
        {"member": "Grace Nalukenge", "amount": 100, "type": "usdt", "notes": "Emergency fund"}, # USDT contribution
        {"member": "David Ssewanyana", "amount": 0.002, "type": "bitcoin", "notes": "Investment"}, # Bitcoin contribution
        {"member": "Mary Namukasa", "amount": 75000, "type": "ugx", "notes": "Business savings"}, # UGX contribution
        {"member": "Sarah Nakimera", "amount": 0.0005, "type": "bitcoin", "notes": "Extra savings"}, # Bitcoin contribution
        {"member": "John Muwonge", "amount": 25000, "type": "ugx", "notes": "Weekly contribution"}, # UGX contribution
        {"member": "Grace Nalukenge", "amount": 50, "type": "usdt", "notes": "Regular savings"}, # USDT contribution
        {"member": "David Ssewanyana", "amount": 100000, "type": "ugx", "notes": "Major contribution"}, # UGX contribution
        {"member": "Mary Namukasa", "amount": 0.0015, "type": "bitcoin", "notes": "Long-term savings"} # Bitcoin contribution
    ]
    
    # Add contributions with different dates
    base_date = datetime.now() - timedelta(days=30) # Set base date to 30 days ago
    for i, contrib in enumerate(contributions): # Iterate through each contribution with index
        # Create contribution with app
        contribution_id = app.add_contribution( # Add contribution using app
            member_name=contrib["member"], # Member name
            amount=contrib["amount"], # Contribution amount
            contribution_type=contrib["type"], # Contribution type
            notes=contrib["notes"] # Contribution notes
        )
        
        # Update creation date to simulate historical data
        if contribution_id: # If contribution was successfully added
            with app.database.db_path as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                contrib_date = base_date + timedelta(days=i*3) # Calculate contribution date (every 3 days)
                cursor.execute('''
                    UPDATE contributions 
                    SET created_at = ? 
                    WHERE id = ?
                ''', (contrib_date.isoformat(), contribution_id)) # Update creation date
                conn.commit() # Commit the transaction
        
        print(f"✅ Added contribution: {contrib['member']} - {contrib['amount']} {contrib['type']}") # Print success message
    
    # Sample payouts
    payouts = [ # List of sample payout dictionaries
        {"member": "Sarah Nakimera", "amount": 25000, "phone": "+256701234567"}, # Sample payout 1
        {"member": "John Muwonge", "amount": 50000, "phone": "+256702345678"}, # Sample payout 2
        {"member": "Grace Nalukenge", "amount": 75000, "phone": "+256703456789"} # Sample payout 3
    ]
    
    for payout in payouts: # Iterate through each sample payout
        app.database.record_payout( # Record payout in database
            member_name=payout["member"], # Member name
            amount=payout["amount"], # Payout amount
            phone_number=payout["phone"] # Recipient phone number
        )
        print(f"✅ Added payout: {payout['member']} - {payout['amount']} UGX") # Print success message
    
    print("🎉 Sample data created successfully!") # Print completion message

def demonstrate_features(app): # Demonstrate key features of the app. App is the instance of AjoApp
    """Demonstrate key features of the app"""
    print("\n🚀 Demonstrating Ajo Bitcoin Savings App Features...") # Print demonstration header
    
    # 1. Bitcoin Address Generation
    print("\n1️⃣ Bitcoin Address Generation:") # Print feature header
    address = app.wallet.generate_address() # Generate new Bitcoin address
    print(f"   Generated Bitcoin address: {address}") # Print generated address
    
    # 2. Database Encryption
    print("\n2️⃣ Database Encryption:") # Print feature header
    test_notes = "This is a secret note that will be encrypted" # Test data for encryption
    encrypted = app.database._encrypt_data(test_notes) # Encrypt test data
    decrypted = app.database._decrypt_data(encrypted) # Decrypt test data
    print(f"   Original: {test_notes}") # Print original data
    print(f"   Encrypted: {encrypted[:50]}...") # Print first 50 characters of encrypted data
    print(f"   Decrypted: {decrypted}") # Print decrypted data
    
    # 3. Savings Summary
    print("\n3️⃣ Savings Summary:") # Print feature header
    summary = app.get_savings_summary() # Get savings summary
    if summary: # If summary was retrieved successfully
        total_data = summary.get('total_contributions', [0, 0]) # Get total contributions data
        print(f"   Total contributions: {total_data[1]} transactions") # Print transaction count
        print(f"   Total amount: {total_data[0]:.2f}") # Print total amount
        
        member_data = summary.get('member_contributions', []) # Get member contributions data
        print(f"   Active members: {len(member_data)}") # Print member count
        
        for member in member_data[:3]:  # Show first 3 members
            print(f"   - {member[0]}: {member[1]:.2f}") # Print member name and amount
    
    # 4. API Status
    print("\n4️⃣ API Integration Status:") # Print feature header
    api_status = app.api.get_api_status() # Get API status
    print(f"   Online: {api_status.get('online', False)}") # Print online status
    print(f"   API Key configured: {api_status.get('api_key_configured', False)}") # Print API key status
    
    # 5. Wallet Status
    print("\n5️⃣ Bitcoin Wallet Status:") # Print feature header
    wallet_status = app.wallet.get_wallet_status() # Get wallet status
    print(f"   Wallet exists: {wallet_status.get('wallet_exists', False)}") # Print wallet existence
    print(f"   Network: {wallet_status.get('network', 'Unknown')}") # Print network type
    
    # 6. Offline Transaction Queue
    print("\n6️⃣ Offline Transaction Queue:") # Print feature header
    print(f"   Pending transactions: {len(app.pending_transactions)}") # Print pending transaction count
    for i, tx in enumerate(app.pending_transactions[:3]):  # Show first 3 transactions
        print(f"   - {tx['type']}: {tx['member_name']} - {tx['amount']} {tx['contribution_type']}") # Print transaction details

def run_interactive_demo(): # Run interactive demo with user input. No parameters, provides interactive demo interface
    """Run interactive demo with user input"""
    print("\n🎮 Interactive Demo Mode") # Print demo mode header
    print("=" * 50) # Print separator line
    
    # Initialize app
    app = AjoApp() # Create main application instance
    
    while True: # Infinite loop for interactive menu
        print("\nChoose an option:") # Print menu header
        print("1. Add new contribution") # Menu option 1
        print("2. View savings summary") # Menu option 2
        print("3. Generate Bitcoin address") # Menu option 3
        print("4. Process mobile money payout") # Menu option 4
        print("5. Export savings report") # Menu option 5
        print("6. Show all features") # Menu option 6
        print("7. Exit demo") # Menu option 7
        
        choice = input("\nEnter your choice (1-7): ").strip() # Get user input and remove whitespace
        
        if choice == "1": # If user chose option 1
            member = input("Enter member name: ").strip() # Get member name
            amount = input("Enter amount: ").strip() # Get amount
            contrib_type = input("Enter type (bitcoin/usdt/ugx): ").strip() # Get contribution type
            
            try: # Try to add contribution
                amount_val = float(amount) # Convert amount to float
                contribution_id = app.add_contribution(member, amount_val, contrib_type) # Add contribution
                if contribution_id: # If contribution was added successfully
                    print(f"✅ Contribution added! ID: {contribution_id}") # Print success message
                else: # If contribution failed
                    print("❌ Failed to add contribution") # Print error message
            except ValueError: # If amount conversion failed
                print("❌ Invalid amount") # Print error message
        
        elif choice == "2": # If user chose option 2
            summary = app.get_savings_summary() # Get savings summary
            if summary: # If summary was retrieved successfully
                total_data = summary.get('total_contributions', [0, 0]) # Get total contributions data
                print(f"\n💰 Total Savings: {total_data[0]:.2f}") # Print total savings
                print(f"📊 Total Transactions: {total_data[1]}") # Print transaction count
                
                member_data = summary.get('member_contributions', []) # Get member contributions data
                print(f"👥 Active Members: {len(member_data)}") # Print member count
                
                print("\nTop Contributors:") # Print header
                for member in member_data[:5]: # Show top 5 contributors
                    print(f"   {member[0]}: {member[1]:.2f}") # Print member name and amount
        
        elif choice == "3": # If user chose option 3
            address = app.wallet.generate_address() # Generate Bitcoin address
            print(f"\n🔑 Generated Bitcoin Address: {address}") # Print generated address
        
        elif choice == "4": # If user chose option 4
            member = input("Enter member name: ").strip() # Get member name
            amount = input("Enter amount (UGX): ").strip() # Get amount
            phone = input("Enter phone number: ").strip() # Get phone number
            
            try: # Try to process payout
                amount_val = float(amount) # Convert amount to float
                success, message = app.process_mobile_money_payout(member, amount_val, phone) # Process payout
                if success: # If payout was successful
                    print(f"✅ Payout processed: {message}") # Print success message
                else: # If payout failed
                    print(f"⚠️ Payout status: {message}") # Print status message
            except ValueError: # If amount conversion failed
                print("❌ Invalid amount") # Print error message
        
        elif choice == "5": # If user chose option 5
            filename = app.export_savings_report() # Export savings report
            if filename: # If export was successful
                print(f"✅ Report exported to: {filename}") # Print success message
            else: # If export failed
                print("❌ Failed to export report") # Print error message
        
        elif choice == "6": # If user chose option 6
            demonstrate_features(app) # Demonstrate all features
        
        elif choice == "7": # If user chose option 7
            print("👋 Thanks for trying Ajo Bitcoin Savings App!") # Print goodbye message
            break # Exit the loop
        
        else: # If user entered invalid choice
            print("❌ Invalid choice. Please try again.") # Print error message

def main(): # Main demo function. No parameters, main entry point for demo
    """Main demo function"""
    print("💰 Ajo Bitcoin Savings App - Demo Mode") # Print demo header
    print("=" * 60) # Print separator line
    print("🎯 Bitnob Uganda Hackathon Entry") # Print hackathon info
    print("🌍 Empowering Uganda through Bitcoin-based group savings") # Print tagline
    print("=" * 60) # Print separator line
    
    setup_demo_logging() # Setup logging for demo
    
    # Check if user wants to create sample data
    create_data = input("\nDo you want to create sample data? (y/n): ").strip().lower() # Get user preference
    
    if create_data == 'y': # If user wants to create sample data
        print("\n📊 Creating sample data...") # Print status message
        app = AjoApp() # Create main application instance
        create_sample_data(app) # Create sample data
        demonstrate_features(app) # Demonstrate features
        
        # Ask if user wants to run interactive demo
        interactive = input("\nDo you want to run interactive demo? (y/n): ").strip().lower() # Get user preference
        if interactive == 'y': # If user wants interactive demo
            run_interactive_demo() # Run interactive demo
        else: # If user doesn't want interactive demo
            print("\n🎉 Demo completed! Run 'python main.py' to start the full application.") # Print completion message
    
    else: # If user doesn't want to create sample data
        print("\n🎮 Starting interactive demo without sample data...") # Print status message
        run_interactive_demo() # Run interactive demo

if __name__ == "__main__": # Check if this script is run directly
    main() # Call the main function 