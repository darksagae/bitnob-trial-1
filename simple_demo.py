#!/usr/bin/env python3
"""
Simple Demo for Ajo Bitcoin Savings App
Works without external dependencies for hackathon presentation
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime
from pathlib import Path

class SimpleAjoDemo:
    """Simplified demo version of Ajo Bitcoin Savings App"""
    
    def __init__(self):
        """Initialize the demo"""
        self.db_path = "demo_ajo.db"
        self.setup_database()
        print("💰 Ajo Bitcoin Savings App - Simple Demo")
        print("=" * 60)
        print("🎯 Bitnob Uganda Hackathon Entry")
        print("🌍 Empowering Uganda through Bitcoin-based group savings")
        print("=" * 60)
    
    def setup_database(self):
        """Setup simple SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_name TEXT NOT NULL,
                amount REAL NOT NULL,
                contribution_type TEXT DEFAULT 'bitcoin',
                bitcoin_address TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_name TEXT NOT NULL,
                amount REAL NOT NULL,
                phone_number TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def generate_bitcoin_address(self):
        """Generate a demo Bitcoin address"""
        random_bytes = secrets.token_bytes(32)
        address_hash = hashlib.sha256(random_bytes).hexdigest()
        return f"1Ajo{address_hash[:26].upper()}"
    
    def add_member(self, name, phone=None, email=None):
        """Add a new member"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO members (name, phone, email)
            VALUES (?, ?, ?)
        ''', (name, phone, email))
        
        member_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Added member: {name}")
        return member_id
    
    def add_contribution(self, member_name, amount, contribution_type="bitcoin", notes=None):
        """Add a new contribution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        bitcoin_address = None
        if contribution_type == "bitcoin":
            bitcoin_address = self.generate_bitcoin_address()
        
        cursor.execute('''
            INSERT INTO contributions (member_name, amount, contribution_type, bitcoin_address, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (member_name, amount, contribution_type, bitcoin_address, notes))
        
        contribution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Added contribution: {member_name} - {amount} {contribution_type}")
        if bitcoin_address:
            print(f"   Bitcoin Address: {bitcoin_address}")
        
        return contribution_id
    
    def get_savings_summary(self):
        """Get savings summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total contributions
        cursor.execute('SELECT SUM(amount), COUNT(*) FROM contributions')
        total_data = cursor.fetchone()
        
        # Member contributions
        cursor.execute('''
            SELECT member_name, SUM(amount), COUNT(*)
            FROM contributions
            GROUP BY member_name
            ORDER BY SUM(amount) DESC
        ''')
        member_data = cursor.fetchall()
        
        # Recent contributions
        cursor.execute('''
            SELECT member_name, amount, contribution_type, created_at
            FROM contributions
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        recent_data = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_contributions': total_data,
            'member_contributions': member_data,
            'recent_contributions': recent_data
        }
    
    def process_payout(self, member_name, amount, phone_number):
        """Process mobile money payout"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO payouts (member_name, amount, phone_number)
            VALUES (?, ?, ?)
        ''', (member_name, amount, phone_number))
        
        payout_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Payout processed: {member_name} - {amount} UGX to {phone_number}")
        return payout_id
    
    def export_report(self):
        """Export savings report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT member_name, amount, contribution_type, created_at, bitcoin_address
            FROM contributions
            ORDER BY created_at DESC
        ''')
        
        data = cursor.fetchall()
        conn.close()
        
        filename = f"ajo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            f.write("Member Name,Amount,Contribution Type,Date,Bitcoin Address\n")
            for row in data:
                f.write(f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4] or ''}\n")
        
        print(f"✅ Report exported to: {filename}")
        return filename
    
    def create_sample_data(self):
        """Create sample data for demonstration"""
        print("\n🎯 Creating sample data...")
        
        # Sample members
        members = [
            {"name": "Sarah Nakimera", "phone": "+256701234567", "email": "sarah@example.com"},
            {"name": "John Muwonge", "phone": "+256702345678", "email": "john@example.com"},
            {"name": "Grace Nalukenge", "phone": "+256703456789", "email": "grace@example.com"},
            {"name": "David Ssewanyana", "phone": "+256704567890", "email": "david@example.com"},
            {"name": "Mary Namukasa", "phone": "+256705678901", "email": "mary@example.com"}
        ]
        
        for member in members:
            self.add_member(member["name"], member["phone"], member["email"])
        
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
        
        for contrib in contributions:
            self.add_contribution(
                contrib["member"], 
                contrib["amount"], 
                contrib["type"], 
                contrib["notes"]
            )
        
        # Sample payouts
        payouts = [
            {"member": "Sarah Nakimera", "amount": 25000, "phone": "+256701234567"},
            {"member": "John Muwonge", "amount": 50000, "phone": "+256702345678"},
            {"member": "Grace Nalukenge", "amount": 75000, "phone": "+256703456789"}
        ]
        
        for payout in payouts:
            self.process_payout(payout["member"], payout["amount"], payout["phone"])
        
        print("🎉 Sample data created successfully!")
    
    def show_features(self):
        """Demonstrate key features"""
        print("\n🚀 Demonstrating Ajo Bitcoin Savings App Features...")
        
        # 1. Bitcoin Address Generation
        print("\n1️⃣ Bitcoin Address Generation:")
        address = self.generate_bitcoin_address()
        print(f"   Generated Bitcoin address: {address}")
        
        # 2. Savings Summary
        print("\n2️⃣ Savings Summary:")
        summary = self.get_savings_summary()
        if summary:
            total_data = summary.get('total_contributions', [0, 0])
            print(f"   Total contributions: {total_data[1]} transactions")
            print(f"   Total amount: {total_data[0]:.2f}")
            
            member_data = summary.get('member_contributions', [])
            print(f"   Active members: {len(member_data)}")
            
            print("\n   Top Contributors:")
            for member in member_data[:3]:
                print(f"   - {member[0]}: {member[1]:.2f}")
        
        # 3. Recent Activity
        print("\n3️⃣ Recent Activity:")
        recent_data = summary.get('recent_contributions', [])
        for contrib in recent_data[:5]:
            print(f"   {contrib[0]}: {contrib[1]} {contrib[2]} ({contrib[3][:10]})")
    
    def run_interactive_demo(self):
        """Run interactive demo"""
        print("\n🎮 Interactive Demo Mode")
        print("=" * 50)
        
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
                    contribution_id = self.add_contribution(member, amount_val, contrib_type)
                    if contribution_id:
                        print(f"✅ Contribution added! ID: {contribution_id}")
                except ValueError:
                    print("❌ Invalid amount")
            
            elif choice == "2":
                summary = self.get_savings_summary()
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
                address = self.generate_bitcoin_address()
                print(f"\n🔑 Generated Bitcoin Address: {address}")
            
            elif choice == "4":
                member = input("Enter member name: ").strip()
                amount = input("Enter amount (UGX): ").strip()
                phone = input("Enter phone number: ").strip()
                
                try:
                    amount_val = float(amount)
                    payout_id = self.process_payout(member, amount_val, phone)
                    if payout_id:
                        print(f"✅ Payout processed! ID: {payout_id}")
                except ValueError:
                    print("❌ Invalid amount")
            
            elif choice == "5":
                filename = self.export_report()
                if filename:
                    print(f"✅ Report exported to: {filename}")
            
            elif choice == "6":
                self.show_features()
            
            elif choice == "7":
                print("👋 Thanks for trying Ajo Bitcoin Savings App!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main demo function"""
    demo = SimpleAjoDemo()
    
    # Check if user wants to create sample data
    create_data = input("\nDo you want to create sample data? (y/n): ").strip().lower()
    
    if create_data == 'y':
        demo.create_sample_data()
        demo.show_features()
        
        # Ask if user wants to run interactive demo
        interactive = input("\nDo you want to run interactive demo? (y/n): ").strip().lower()
        if interactive == 'y':
            demo.run_interactive_demo()
        else:
            print("\n🎉 Demo completed!")
    
    else:
        print("\n🎮 Starting interactive demo without sample data...")
        demo.run_interactive_demo()
    
    print("\n📚 Full Application Features:")
    print("   - Complete Bitnob API integration")
    print("   - Advanced encryption and security")
    print("   - Offline Bitcoin wallet management")
    print("   - Tkinter GUI interface")
    print("   - Background sync capabilities")
    print("   - Mobile money payout processing")
    print("\n🚀 Run 'python main.py' to start the full application!")

if __name__ == "__main__":
    main() 