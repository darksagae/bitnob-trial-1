#!/usr/bin/env python3
"""
Test script for Ajo Bitcoin Savings App
Verifies all components work correctly before hackathon presentation
"""

import sys
import os
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from main import AjoApp
        print("✅ main.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import main.py: {e}")
        return False
    
    try:
        from database import AjoDatabase
        print("✅ database.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import database.py: {e}")
        return False
    
    try:
        from wallet import BitcoinWallet
        print("✅ wallet.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wallet.py: {e}")
        return False
    
    try:
        from api import BitnobAPI
        print("✅ api.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import api.py: {e}")
        return False
    
    try:
        from ui import AjoUI
        print("✅ ui.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ui.py: {e}")
        return False
    
    return True

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing database functionality...")
    
    try:
        from database import AjoDatabase
        
        # Create database
        db = AjoDatabase("test_ajo.db")
        print("✅ Database created successfully")
        
        # Test encryption
        test_data = "Test secret data"
        encrypted = db._encrypt_data(test_data)
        decrypted = db._decrypt_data(encrypted)
        
        if decrypted == test_data:
            print("✅ Encryption/decryption working")
        else:
            print("❌ Encryption/decryption failed")
            return False
        
        # Test adding member
        member_id = db.add_member("Test Member", "+256701234567", "test@example.com")
        if member_id:
            print("✅ Member added successfully")
        else:
            print("❌ Failed to add member")
            return False
        
        # Test adding contribution
        contrib_id = db.add_contribution("Test Member", 100.0, "bitcoin", "test_address")
        if contrib_id:
            print("✅ Contribution added successfully")
        else:
            print("❌ Failed to add contribution")
            return False
        
        # Test getting summary
        summary = db.get_savings_summary()
        if summary:
            print("✅ Savings summary retrieved")
        else:
            print("❌ Failed to get savings summary")
            return False
        
        # Cleanup
        if os.path.exists("test_ajo.db"):
            os.remove("test_ajo.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_wallet():
    """Test Bitcoin wallet functionality"""
    print("\n🔑 Testing Bitcoin wallet functionality...")
    
    try:
        from wallet import BitcoinWallet
        
        # Create wallet
        wallet = BitcoinWallet("test_wallet")
        print("✅ Wallet created successfully")
        
        # Test address generation
        address = wallet.generate_address()
        if address:
            print(f"✅ Bitcoin address generated: {address}")
        else:
            print("❌ Failed to generate Bitcoin address")
            return False
        
        # Test address validation
        if wallet.validate_address(address):
            print("✅ Address validation working")
        else:
            print("❌ Address validation failed")
            return False
        
        # Test wallet status
        status = wallet.get_wallet_status()
        if status:
            print("✅ Wallet status retrieved")
        else:
            print("❌ Failed to get wallet status")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Wallet test failed: {e}")
        return False

def test_api():
    """Test Bitnob API functionality"""
    print("\n🌐 Testing Bitnob API functionality...")
    
    try:
        from api import BitnobAPI
        
        # Create API client
        api = BitnobAPI()
        print("✅ API client created successfully")
        
        # Test online status
        online = api.is_online()
        print(f"✅ Online status check: {'Online' if online else 'Offline'}")
        
        # Test API status
        status = api.get_api_status()
        if status:
            print("✅ API status retrieved")
        else:
            print("❌ Failed to get API status")
            return False
        
        # Test mobile money providers
        providers = api.get_uganda_mobile_money_providers()
        if providers:
            print(f"✅ Mobile money providers retrieved: {len(providers)} providers")
        else:
            print("❌ Failed to get mobile money providers")
            return False
        
        # Test phone validation
        valid_phone = api.validate_phone_number("+256701234567", "UG")
        if valid_phone:
            print("✅ Phone validation working")
        else:
            print("❌ Phone validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_app_integration():
    """Test full app integration"""
    print("\n🔗 Testing full app integration...")
    
    try:
        from main import AjoApp
        
        # Create app
        app = AjoApp()
        print("✅ App created successfully")
        
        # Test adding contribution
        contrib_id = app.add_contribution("Integration Test", 50.0, "bitcoin")
        if contrib_id:
            print("✅ App contribution added successfully")
        else:
            print("❌ Failed to add app contribution")
            return False
        
        # Test getting summary
        summary = app.get_savings_summary()
        if summary:
            print("✅ App savings summary retrieved")
        else:
            print("❌ Failed to get app savings summary")
            return False
        
        # Test mobile money payout
        success, message = app.process_mobile_money_payout("Test User", 1000, "+256701234567")
        print(f"✅ Mobile money payout test: {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'bitcoinlib',
        'Crypto',
        'requests',
        'tkinter'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not available")
            return False
    
    return True

def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    test_files = [
        "test_ajo.db",
        "wallets/test_wallet.json",
        "wallets/test_wallet_mnemonic.txt",
        "wallets/bitcoinlib.db"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed {file_path}")
            except Exception as e:
                print(f"⚠️ Could not remove {file_path}: {e}")

def main():
    """Run all tests"""
    print("🧪 Ajo Bitcoin Savings App - Test Suite")
    print("=" * 60)
    print("🎯 Bitnob Uganda Hackathon - Pre-submission Testing")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(level=logging.ERROR)  # Suppress most logs during testing
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Module Imports", test_imports),
        ("Database", test_database),
        ("Bitcoin Wallet", test_wallet),
        ("Bitnob API", test_api),
        ("App Integration", test_app_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    # Cleanup
    cleanup_test_files()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print(f"{'='*60}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! App is ready for hackathon submission.")
        print("🚀 Run 'python main.py' to start the application.")
        print("🎮 Run 'python demo.py' to see the demo mode.")
        return True
    else:
        print("⚠️ Some tests failed. Please fix issues before submission.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 