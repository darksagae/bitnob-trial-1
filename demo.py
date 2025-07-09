#!/usr/bin/env python3
"""
Demo script for Ajo Bitcoin Savings App
Creates sample data and demonstrates all features for hackathon presentation
"""

import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Import our modules
from main import AjoApp
from database import AjoDatabase
from wallet import BitcoinWallet
from api import BitnobAPI

def setup_demo_logging():
    """Setup logging for demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def create_sample_data(app):
    """Create sample data for demonstration"""
    print("🎯 Creating sample data for demonstration...")
    
    # Sample members
    members = [
        {"name": "Sarah Nakimera", "phone": "+256701234567", "email": "sarah@example.com"},
        {"name": "John Muwonge", "phone": "+256702345678", "email": "john@example.com"},
        {"name": "Grace Nalukenge", "phone": "+256703456789", "email": "grace@example.com"},
        {"name": "David Ssewanyana", "phone": "+256704567890", "email": "david@example.com"},
        {"name": "Mary Namukasa", "phone": "+256705678901", "email": "mary@example.com"}
    ]
    
    # Add members
    for member in members:
        app.database.add_member(
            name=member["name"],
            phone_number=member["phone"],
            email=member["email"]
        )
        print(f"✅ Added member: {member['name']}")
    
    # Sample contributions
    contributions = [
        {"member": "Sarah Nakimera", "amount": 0.001, "type": "bitcoin", "notes": "Weekly savings"},
        {"member": "John Muwonge", "amount": 50000, "type": "ugx", "notes": "Monthly contribution"},
        {"member": "Grace Nalukenge", "amount": 100, "type": "usdt", "notes": "Emergency fund"},
        {"member": "David Ssewanyana", "amount": 0.002, "type": "bitcoin", "notes": "Investment"},
        {"member": "Mary Namukasa", "amount": 75000, "type": "ugx", "notes": "Business savings"},
        {"member": "Sarah Nakimera", "amount": 0.0005, "type": "bitcoin", "notes": "Extra savings"},
        {"member": "John Muwonge", "amount": 25000, "type": "ugx", "notes": "Weekly contribution"},
        {"member": "Grace Nalukenge", "amount": 50, "type": "usdt", "notes": "Regular savings"},
        {"member": "David Ssewanyana", "amount": 100000, "type": "ugx", "notes": "Major contribution"},
        {"member": "Mary Namukasa", "amount": 0.0015, "type": "bitcoin", "notes": "Long-term savings"}
    ]
    
    # Add contributions with different dates
    base_date = datetime.now() - timedelta(days=30)
    for i, contrib in enumerate(contributions):
        # Create contribution with app
        contribution_id = app.add_contribution(
            member_name=contrib["member"],
            amount=contrib["amount"],
            contribution_type=contrib["type"],
            notes=contrib["notes"]
        )
        
        # Update creation date to simulate historical data
        if contribution_id:
            with app.database.db_path as conn:
                cursor = conn.cursor()
                contrib_date = base_date + timedelta(days=i*3)
                cursor.execute('''
                    UPDATE contributions 
                    SET created_at = ? 
                    WHERE id = ?
                ''', (contrib_date.isoformat(), contribution_id))
                conn.commit()
        
        print(f"✅ Added contribution: {contrib['member']} - {contrib['amount']} {contrib['type']}")
    
    # Sample payouts
    payouts = [
        {"member": "Sarah Nakimera", "amount": 25000, "phone": "+256701234567"},
        {"member": "John Muwonge", "amount": 50000, "phone": "+256702345678"},
        {"member": "Grace Nalukenge", "amount": 75000, "phone": "+256703456789"}
    ]
    
    for payout in payouts:
        app.database.record_payout(
            member_name=payout["member"],
            amount=payout["amount"],
            phone_number=payout["phone"]
        )
        print(f"✅ Added payout: {payout['member']} - {payout['amount']} UGX")
    
    print("🎉 Sample data created successfully!")

def demonstrate_features(app):
    """Demonstrate key features of the app"""
    print("\n🚀 Demonstrating Ajo Bitcoin Savings App Features...")
    
    # 1. Bitcoin Address Generation
    print("\n1️⃣ Bitcoin Address Generation:")
    address = app.wallet.generate_address()
    print(f"   Generated Bitcoin address: {address}")
    
    # 2. Database Encryption
    print("\n2️⃣ Database Encryption:")
    test_notes = "This is a secret note that will be encrypted"
    encrypted = app.database._encrypt_data(test_notes)
    decrypted = app.database._decrypt_data(encrypted)
    print(f"   Original: {test_notes}")
    print(f"   Encrypted: {encrypted[:50]}...")
    print(f"   Decrypted: {decrypted}")
    
    # 3. Savings Summary
    print("\n3️⃣ Savings Summary:")
    summary = app.get_savings_summary()
    if summary:
        total_data = summary.get('total_contributions', [0, 0])
        print(f"   Total contributions: {total_data[1]} transactions")
        print(f"   Total amount: {total_data[0]:.2f}")
        
        member_data = summary.get('member_contributions', [])
        print(f"   Active members: {len(member_data)}")
        
        for member in member_data[:3]:  # Show first 3 members
            print(f"   - {member[0]}: {member[1]:.2f}")
    
    # 4. API Status
    print("\n4️⃣ API Integration Status:")
    api_status = app.api.get_api_status()
    print(f"   Online: {api_status.get('online', False)}")
    print(f"   API Key configured: {api_status.get('api_key_configured', False)}")
    
    # 5. Wallet Status
    print("\n5️⃣ Bitcoin Wallet Status:")
    wallet_status = app.wallet.get_wallet_status()
    print(f"   Wallet exists: {wallet_status.get('wallet_exists', False)}")
    print(f"   Network: {wallet_status.get('network', 'Unknown')}")
    
    # 6. Offline Transaction Queue
    print("\n6️⃣ Offline Transaction Queue:")
    print(f"   Pending transactions: {len(app.pending_transactions)}")
    for i, tx in enumerate(app.pending_transactions[:3]):  # Show first 3
        print(f"   - {tx['type']}: {tx['member_name']} - {tx['amount']} {tx['contribution_type']}")

def run_interactive_demo():
    """Run interactive demo with user input"""
    print("\n🎮 Interactive Demo Mode")
    print("=" * 50)
    
    # Initialize app
    app = AjoApp()
    
    while True:
        print("\nChoose an option:")
        print("1. Add new contribution")
        print("2. View savings summary")
        print("3. Generate Bitcoin address")
        print("4. Process mobile money payout")
        print("5. Export savings report")
        print("6. Show all features")
        print("7. Exit demo")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            member = input("Enter member name: ").strip()
            amount = input("Enter amount: ").strip()
            contrib_type = input("Enter type (bitcoin/usdt/ugx): ").strip()
            
            try:
                amount_val = float(amount)
                contribution_id = app.add_contribution(member, amount_val, contrib_type)
                if contribution_id:
                    print(f"✅ Contribution added! ID: {contribution_id}")
                else:
                    print("❌ Failed to add contribution")
            except ValueError:
                print("❌ Invalid amount")
        
        elif choice == "2":
            summary = app.get_savings_summary()
            if summary:
                total_data = summary.get('total_contributions', [0, 0])
                print(f"\n💰 Total Savings: {total_data[0]:.2f}")
                print(f"📊 Total Transactions: {total_data[1]}")
                
                member_data = summary.get('member_contributions', [])
                print(f"👥 Active Members: {len(member_data)}")
                
                print("\nTop Contributors:")
                for member in member_data[:5]:
                    print(f"   {member[0]}: {member[1]:.2f}")
        
        elif choice == "3":
            address = app.wallet.generate_address()
            print(f"\n🔑 Generated Bitcoin Address: {address}")
        
        elif choice == "4":
            member = input("Enter member name: ").strip()
            amount = input("Enter amount (UGX): ").strip()
            phone = input("Enter phone number: ").strip()
            
            try:
                amount_val = float(amount)
                success, message = app.process_mobile_money_payout(member, amount_val, phone)
                if success:
                    print(f"✅ Payout processed: {message}")
                else:
                    print(f"⚠️ Payout status: {message}")
            except ValueError:
                print("❌ Invalid amount")
        
        elif choice == "5":
            filename = app.export_savings_report()
            if filename:
                print(f"✅ Report exported to: {filename}")
            else:
                print("❌ Failed to export report")
        
        elif choice == "6":
            demonstrate_features(app)
        
        elif choice == "7":
            print("👋 Thanks for trying Ajo Bitcoin Savings App!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

def main():
    """Main demo function"""
    print("💰 Ajo Bitcoin Savings App - Demo Mode")
    print("=" * 60)
    print("🎯 Bitnob Uganda Hackathon Entry")
    print("🌍 Empowering Uganda through Bitcoin-based group savings")
    print("=" * 60)
    
    setup_demo_logging()
    
    # Check if user wants to create sample data
    create_data = input("\nDo you want to create sample data? (y/n): ").strip().lower()
    
    if create_data == 'y':
        print("\n📊 Creating sample data...")
        app = AjoApp()
        create_sample_data(app)
        demonstrate_features(app)
        
        # Ask if user wants to run interactive demo
        interactive = input("\nDo you want to run interactive demo? (y/n): ").strip().lower()
        if interactive == 'y':
            run_interactive_demo()
        else:
            print("\n🎉 Demo completed! Run 'python main.py' to start the full application.")
    
    else:
        print("\n🎮 Starting interactive demo without sample data...")
        run_interactive_demo()

if __name__ == "__main__":
    main() 