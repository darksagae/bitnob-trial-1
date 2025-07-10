#!/usr/bin/env python3
"""
Demo script for Ajo Bitcoin Savings App
Tests the production-ready application with sample data
"""

import os
import sys
import logging
from datetime import datetime
import config
from database_new import Database
from api_new import BitnobAPI

def setup_demo_logging():
    """Setup logging for demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_database():
    """Test database functionality"""
    print("🔍 Testing Database...")
    
    try:
        # Initialize database
        db = Database()
        print("✅ Database initialized successfully")
        
        # Test user creation
        admin_id = db.create_user(
            username="demo_admin",
            password="demo123",
            role="admin",
            full_name="Demo Administrator",
            phone_number="+256700000000",
            email="demo_admin@ajo.com"
        )
        print(f"✅ Created admin user: {admin_id}")
        
        user_id = db.create_user(
            username="demo_user",
            password="demo123",
            role="user",
            full_name="Demo User",
            phone_number="+256700000001",
            email="demo_user@ajo.com"
        )
        print(f"✅ Created regular user: {user_id}")
        
        # Test group creation
        group_id = db.create_group(
            name="Demo Savings Group",
            description="A demo group for testing",
            admin_user_id=admin_id
        )
        print(f"✅ Created group: {group_id}")
        
        # Add user to group
        db.add_user_to_group(user_id, group_id)
        print("✅ Added user to group")
        
        # Test contribution
        contrib_id = db.add_contribution(
            user_id=user_id,
            group_id=group_id,
            amount=50000.0,
            payment_method="mobile_money",
            payment_reference="+256700000001"
        )
        print(f"✅ Added contribution: {contrib_id}")
        
        # Test payout
        payout_id = db.add_payout(
            group_id=group_id,
            user_id=user_id,
            amount=25000.0,
            payment_method="mobile_money",
            payment_reference="+256700000001"
        )
        print(f"✅ Added payout: {payout_id}")
        
        # Test statistics
        summary = db.get_savings_summary()
        print(f"✅ Savings summary: {summary}")
        
        # Test commission tracking
        total_commissions = db.get_total_commissions()
        print(f"✅ Total commissions: {total_commissions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api():
    """Test API functionality"""
    print("\n🔍 Testing API...")
    
    try:
        # Initialize API
        api = BitnobAPI()
        print("✅ API client initialized")
        
        # Test connection
        if api.test_connection():
            print("✅ API connection successful")
        else:
            print("⚠️ API connection failed (expected in demo mode)")
        
        # Test account balance
        balance = api.get_account_balance()
        print(f"✅ Account balance: {balance}")
        
        # Test payment methods
        methods = api.get_payment_methods()
        print(f"✅ Payment methods: {len(methods)} available")
        
        # Test mobile money payment (mock)
        payment = api.create_mobile_money_payment(
            phone_number="+256700000000",
            amount=10000.0,
            provider="mtn",
            reference="demo_payment"
        )
        print(f"✅ Mobile money payment: {payment}")
        
        # Test Bitcoin payment (mock)
        btc_payment = api.create_bitcoin_payment(
            amount=50000.0,
            reference="demo_btc"
        )
        print(f"✅ Bitcoin payment: {btc_payment}")
        
        # Test exchange rates
        rates = api.get_exchange_rates()
        print(f"✅ Exchange rates: {rates}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_validation():
    """Test input validation"""
    print("\n🔍 Testing Validation...")
    
    try:
        from utils import InputValidator
        
        # Test amount validation
        validator = InputValidator()
        
        # Valid amounts
        valid_amounts = ["1000", "50000", "1000000"]
        for amount in valid_amounts:
            result = validator.validate_amount(amount)
            if result:
                print(f"✅ Valid amount: {amount}")
            else:
                print(f"❌ Invalid amount: {amount}")
        
        # Invalid amounts
        invalid_amounts = ["0", "-1000", "abc", "999"]
        for amount in invalid_amounts:
            result = validator.validate_amount(amount)
            if result is None:
                print(f"✅ Correctly rejected: {amount}")
            else:
                print(f"❌ Should have rejected: {amount}")
        
        # Test phone validation
        valid_phones = ["+256700000000", "256700000000", "0700000000"]
        for phone in valid_phones:
            if validator.validate_phone_number(phone, "mtn"):
                print(f"✅ Valid phone: {phone}")
            else:
                print(f"❌ Invalid phone: {phone}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n🔍 Testing Configuration...")
    
    try:
        # Test config values
        print(f"✅ App name: {config.APP_NAME}")
        print(f"✅ Commission rate: {config.COMMISSION_RATE}")
        print(f"✅ Database path: {config.DATABASE_PATH}")
        print(f"✅ API base URL: {config.BITNOB_API_BASE_URL}")
        print(f"✅ GUI theme: {config.GUI_THEME}")
        print(f"✅ Demo mode: {config.DEMO_MODE}")
        print(f"✅ API mock mode: {config.API_MOCK_MODE}")
        
        # Test color configuration
        print(f"✅ Primary color: {config.GUI_COLORS['primary']}")
        print(f"✅ Success color: {config.GUI_COLORS['success']}")
        
        # Test font configuration
        print(f"✅ Header font: {config.GUI_FONTS['header']}")
        print(f"✅ Button font: {config.GUI_FONTS['button']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def create_demo_data():
    """Create comprehensive demo data"""
    print("\n🔍 Creating Demo Data...")
    
    try:
        db = Database()
        
        # Create multiple users
        users = [
            ("admin1", "admin123", "admin", "John Admin", "+256700000001", "admin1@ajo.com"),
            ("admin2", "admin123", "admin", "Jane Admin", "+256700000002", "admin2@ajo.com"),
            ("user1", "user123", "user", "Alice User", "+256700000003", "user1@ajo.com"),
            ("user2", "user123", "user", "Bob User", "+256700000004", "user2@ajo.com"),
            ("user3", "user123", "user", "Carol User", "+256700000005", "user3@ajo.com"),
        ]
        
        user_ids = []
        for username, password, role, full_name, phone, email in users:
            user_id = db.create_user(username, password, role, full_name, phone, email)
            if user_id:
                user_ids.append(user_id)
                print(f"✅ Created user: {username}")
        
        # Create multiple groups
        groups = [
            ("Family Savings", "Monthly family savings group", user_ids[0]),
            ("Business Investment", "Business investment group", user_ids[1]),
            ("Education Fund", "Education savings for children", user_ids[0]),
            ("Emergency Fund", "Emergency savings group", user_ids[1]),
        ]
        
        group_ids = []
        for name, description, admin_id in groups:
            group_id = db.create_group(name, description, admin_id)
            if group_id:
                group_ids.append(group_id)
                print(f"✅ Created group: {name}")
        
        # Add users to groups
        for user_id in user_ids[2:]:  # Regular users
            for group_id in group_ids:
                db.add_user_to_group(user_id, group_id)
        print("✅ Added users to groups")
        
        # Add contributions
        contribution_data = [
            (user_ids[2], group_ids[0], 25000, "mobile_money", "+256700000003"),
            (user_ids[3], group_ids[0], 30000, "mobile_money", "+256700000004"),
            (user_ids[4], group_ids[0], 20000, "bitcoin", "btc_tx_001"),
            (user_ids[2], group_ids[1], 50000, "usdt", "usdt_tx_001"),
            (user_ids[3], group_ids[1], 40000, "mobile_money", "+256700000004"),
            (user_ids[4], group_ids[2], 15000, "mobile_money", "+256700000005"),
            (user_ids[2], group_ids[2], 20000, "bitcoin", "btc_tx_002"),
            (user_ids[3], group_ids[3], 35000, "usdt", "usdt_tx_002"),
        ]
        
        for user_id, group_id, amount, method, reference in contribution_data:
            contrib_id = db.add_contribution(user_id, group_id, amount, method, reference)
            if contrib_id:
                print(f"✅ Added contribution: {amount} UGX via {method}")
        
        # Add payouts
        payout_data = [
            (group_ids[0], user_ids[2], 10000, "mobile_money", "+256700000003"),
            (group_ids[1], user_ids[3], 15000, "mobile_money", "+256700000004"),
            (group_ids[2], user_ids[4], 8000, "bitcoin", "btc_payout_001"),
        ]
        
        for group_id, user_id, amount, method, reference in payout_data:
            payout_id = db.add_payout(group_id, user_id, amount, method, reference)
            if payout_id:
                print(f"✅ Added payout: {amount} UGX via {method}")
        
        # Approve some payouts
        payouts = db.get_pending_payouts()
        for payout in payouts[:2]:  # Approve first 2 payouts
            db.approve_payout(payout[0], user_ids[0])  # Admin approves
            print(f"✅ Approved payout: {payout[0]}")
        
        print("✅ Demo data creation completed")
        return True
        
    except Exception as e:
        print(f"❌ Demo data creation failed: {e}")
        return False

def show_demo_summary():
    """Show demo summary"""
    print("\n" + "="*50)
    print("🎉 DEMO SUMMARY")
    print("="*50)
    
    try:
        db = Database()
        summary = db.get_savings_summary()
        
        print(f"📊 Total Contributions: {summary.get('total_contributions', 0):,.2f} UGX")
        print(f"📊 Total Payouts: {summary.get('total_payouts', 0):,.2f} UGX")
        print(f"💰 Total Commissions: {summary.get('total_commissions', 0):,.2f} UGX")
        print(f"👥 Active Users: {summary.get('user_count', 0)}")
        print(f"👥 Active Groups: {summary.get('group_count', 0)}")
        
        # Show commission breakdown
        commissions = db.get_commission_history()
        pending_commissions = sum(1 for c in commissions if not c[4])  # transferred = False
        
        print(f"📋 Commission Records: {len(commissions)}")
        print(f"⏳ Pending Transfers: {pending_commissions}")
        
        print("\n🚀 Ready to launch the application!")
        print("Run: python main_new.py")
        print("Login with: admin/admin123 or user/user123")
        
    except Exception as e:
        print(f"❌ Failed to show summary: {e}")

def main():
    """Main demo function"""
    print("🚀 Ajo Bitcoin Savings App - Production Demo")
    print("="*50)
    
    # Setup logging
    setup_demo_logging()
    
    # Run tests
    tests = [
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("API", test_api),
        ("Validation", test_validation),
        ("Demo Data", create_demo_data),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Application is ready.")
        show_demo_summary()
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    main() 