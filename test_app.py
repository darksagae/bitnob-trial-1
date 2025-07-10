#!/usr/bin/env python3
"""
Test script for Ajo Bitcoin Savings App
Verifies all components work correctly before hackathon presentation
"""

import sys # System-specific parameters and functions for exit codes and command line arguments
import os # Operating system interface for file and directory operations
import logging # Logging for error tracking, debugging and monitoring test operations
from pathlib import Path # Object-oriented filesystem paths for cross-platform directory operations

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) # Add current directory to Python path for module imports

def test_imports(): # Test that all modules can be imported. No parameters, returns boolean indicating success
    """Test that all modules can be imported"""
    print("🔍 Testing module imports...") # Print test header
    
    try: # Try to import main module
        from main import AjoApp # Import main application class
        print("✅ main.py imported successfully") # Print success message
    except Exception as e: # Catch any import exceptions
        print(f"❌ Failed to import main.py: {e}") # Print error message
        return False # Return False for failed import
    
    try: # Try to import database module
        from database import AjoDatabase # Import database class
        print("✅ database.py imported successfully") # Print success message
    except Exception as e: # Catch any import exceptions
        print(f"❌ Failed to import database.py: {e}") # Print error message
        return False # Return False for failed import
    
    try: # Try to import wallet module
        from wallet import BitcoinWallet # Import Bitcoin wallet class
        print("✅ wallet.py imported successfully") # Print success message
    except Exception as e: # Catch any import exceptions
        print(f"❌ Failed to import wallet.py: {e}") # Print error message
        return False # Return False for failed import
    
    try: # Try to import API module
        from api import BitnobAPI # Import Bitnob API class
        print("✅ api.py imported successfully") # Print success message
    except Exception as e: # Catch any import exceptions
        print(f"❌ Failed to import api.py: {e}") # Print error message
        return False # Return False for failed import
    
    try: # Try to import UI module
        from ui import AjoUI # Import user interface class
        print("✅ ui.py imported successfully") # Print success message
    except Exception as e: # Catch any import exceptions
        print(f"❌ Failed to import ui.py: {e}") # Print error message
        return False # Return False for failed import
    
    return True # Return True if all imports succeeded

def test_database(): # Test database functionality. No parameters, returns boolean indicating success
    """Test database functionality"""
    print("\n🗄️ Testing database functionality...") # Print test header
    
    try: # Try to test database functionality
        from database import AjoDatabase # Import database class
        
        # Create database
        db = AjoDatabase("test_ajo.db") # Create test database instance
        print("✅ Database created successfully") # Print success message
        
        # Test encryption
        test_data = "Test secret data" # Test data for encryption
        encrypted = db._encrypt_data(test_data) # Encrypt test data
        decrypted = db._decrypt_data(encrypted) # Decrypt test data
        
        if decrypted == test_data: # If decrypted data matches original
            print("✅ Encryption/decryption working") # Print success message
        else: # If decrypted data doesn't match original
            print("❌ Encryption/decryption failed") # Print error message
            return False # Return False for failed encryption test
        
        # Test adding member
        member_id = db.add_member("Test Member", "+256701234567", "test@example.com") # Add test member
        if member_id: # If member was added successfully
            print("✅ Member added successfully") # Print success message
        else: # If member addition failed
            print("❌ Failed to add member") # Print error message
            return False # Return False for failed member addition
        
        # Test adding contribution
        contrib_id = db.add_contribution("Test Member", 100.0, "bitcoin", "test_address") # Add test contribution
        if contrib_id: # If contribution was added successfully
            print("✅ Contribution added successfully") # Print success message
        else: # If contribution addition failed
            print("❌ Failed to add contribution") # Print error message
            return False # Return False for failed contribution addition
        
        # Test getting summary
        summary = db.get_savings_summary() # Get savings summary
        if summary: # If summary was retrieved successfully
            print("✅ Savings summary retrieved") # Print success message
        else: # If summary retrieval failed
            print("❌ Failed to get savings summary") # Print error message
            return False # Return False for failed summary retrieval
        
        # Cleanup
        if os.path.exists("test_ajo.db"): # If test database file exists
            os.remove("test_ajo.db") # Remove test database file
        
        return True # Return True if all database tests passed
        
    except Exception as e: # Catch any exceptions during database testing
        print(f"❌ Database test failed: {e}") # Print error message
        return False # Return False for failed database test

def test_wallet(): # Test Bitcoin wallet functionality. No parameters, returns boolean indicating success
    """Test Bitcoin wallet functionality"""
    print("\n🔑 Testing Bitcoin wallet functionality...") # Print test header
    
    try: # Try to test wallet functionality
        from wallet import BitcoinWallet # Import Bitcoin wallet class
        
        # Create wallet
        wallet = BitcoinWallet("test_wallet") # Create test wallet instance
        print("✅ Wallet created successfully") # Print success message
        
        # Test address generation
        address = wallet.generate_address() # Generate Bitcoin address
        if address: # If address was generated successfully
            print(f"✅ Bitcoin address generated: {address}") # Print success message with address
        else: # If address generation failed
            print("❌ Failed to generate Bitcoin address") # Print error message
            return False # Return False for failed address generation
        
        # Test address validation
        if wallet.validate_address(address): # If address validation succeeds
            print("✅ Address validation working") # Print success message
        else: # If address validation fails
            print("❌ Address validation failed") # Print error message
            return False # Return False for failed address validation
        
        # Test wallet status
        status = wallet.get_wallet_status() # Get wallet status
        if status: # If status was retrieved successfully
            print("✅ Wallet status retrieved") # Print success message
        else: # If status retrieval failed
            print("❌ Failed to get wallet status") # Print error message
            return False # Return False for failed status retrieval
        
        return True # Return True if all wallet tests passed
        
    except Exception as e: # Catch any exceptions during wallet testing
        print(f"❌ Wallet test failed: {e}") # Print error message
        return False # Return False for failed wallet test

def test_api(): # Test Bitnob API functionality. No parameters, returns boolean indicating success
    """Test Bitnob API functionality"""
    print("\n🌐 Testing Bitnob API functionality...") # Print test header
    
    try: # Try to test API functionality
        from api import BitnobAPI # Import Bitnob API class
        
        # Create API client
        api = BitnobAPI() # Create API client instance
        print("✅ API client created successfully") # Print success message
        
        # Test online status
        online = api.is_online() # Check if API is online
        print(f"✅ Online status check: {'Online' if online else 'Offline'}") # Print online status
        
        # Test API status
        status = api.get_api_status() # Get API status
        if status: # If status was retrieved successfully
            print("✅ API status retrieved") # Print success message
        else: # If status retrieval failed
            print("❌ Failed to get API status") # Print error message
            return False # Return False for failed status retrieval
        
        # Test mobile money providers
        providers = api.get_uganda_mobile_money_providers() # Get mobile money providers
        if providers: # If providers were retrieved successfully
            print(f"✅ Mobile money providers retrieved: {len(providers)} providers") # Print success message with count
        else: # If providers retrieval failed
            print("❌ Failed to get mobile money providers") # Print error message
            return False # Return False for failed providers retrieval
        
        # Test phone validation
        valid_phone = api.validate_phone_number("+256701234567", "UG") # Validate Ugandan phone number
        if valid_phone: # If phone validation succeeds
            print("✅ Phone validation working") # Print success message
        else: # If phone validation fails
            print("❌ Phone validation failed") # Print error message
            return False # Return False for failed phone validation
        
        return True # Return True if all API tests passed
        
    except Exception as e: # Catch any exceptions during API testing
        print(f"❌ API test failed: {e}") # Print error message
        return False # Return False for failed API test

def test_app_integration(): # Test full app integration. No parameters, returns boolean indicating success
    """Test full app integration"""
    print("\n🔗 Testing full app integration...") # Print test header
    
    try: # Try to test app integration
        from main import AjoApp # Import main application class
        
        # Create app
        app = AjoApp() # Create main application instance
        print("✅ App created successfully") # Print success message
        
        # Test adding contribution
        contrib_id = app.add_contribution("Integration Test", 50.0, "bitcoin") # Add test contribution
        if contrib_id: # If contribution was added successfully
            print("✅ App contribution added successfully") # Print success message
        else: # If contribution addition failed
            print("❌ Failed to add app contribution") # Print error message
            return False # Return False for failed contribution addition
        
        # Test getting summary
        summary = app.get_savings_summary() # Get savings summary
        if summary: # If summary was retrieved successfully
            print("✅ App savings summary retrieved") # Print success message
        else: # If summary retrieval failed
            print("❌ Failed to get app savings summary") # Print error message
            return False # Return False for failed summary retrieval
        
        # Test mobile money payout
        success, message = app.process_mobile_money_payout("Test User", 1000, "+256701234567") # Process test payout
        print(f"✅ Mobile money payout test: {message}") # Print payout test result
        
        return True # Return True if all integration tests passed
        
    except Exception as e: # Catch any exceptions during integration testing
        print(f"❌ App integration test failed: {e}") # Print error message
        return False # Return False for failed integration test

def test_dependencies(): # Test that all required dependencies are available. No parameters, returns boolean indicating success
    """Test that all required dependencies are available"""
    print("\n📦 Testing dependencies...") # Print test header
    
    required_packages = [ # List of required Python packages
        'bitcoinlib', # Bitcoin library for wallet management
        'Crypto', # Cryptography library for encryption
        'requests', # HTTP library for API requests
        'tkinter' # GUI library for user interface
    ]
    
    for package in required_packages: # Iterate through each required package
        try: # Try to import package
            __import__(package) # Import package
            print(f"✅ {package} available") # Print success message
        except ImportError: # If package import fails
            print(f"❌ {package} not available") # Print error message
            return False # Return False for missing package
    
    return True # Return True if all dependencies are available

def cleanup_test_files(): # Clean up test files. No parameters, removes test files created during testing
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...") # Print cleanup header
    
    test_files = [ # List of test files to remove
        "test_ajo.db", # Test database file
        "wallets/test_wallet.json", # Test wallet configuration file
        "wallets/test_wallet_mnemonic.txt", # Test wallet mnemonic file
        "wallets/bitcoinlib.db" # Test Bitcoin library database
    ]
    
    for file_path in test_files: # Iterate through each test file
        if os.path.exists(file_path): # If test file exists
            try: # Try to remove file
                os.remove(file_path) # Remove test file
                print(f"✅ Removed {file_path}") # Print success message
            except Exception as e: # If file removal fails
                print(f"⚠️ Could not remove {file_path}: {e}") # Print warning message

def main(): # Run all tests. No parameters, returns boolean indicating overall test success
    """Run all tests"""
    print("🧪 Ajo Bitcoin Savings App - Test Suite") # Print test suite header
    print("=" * 60) # Print separator line
    print("🎯 Bitnob Uganda Hackathon - Pre-submission Testing") # Print hackathon info
    print("=" * 60) # Print separator line
    
    # Setup logging
    logging.basicConfig(level=logging.ERROR)  # Suppress most logs during testing
    
    tests = [ # List of test functions to run
        ("Dependencies", test_dependencies), # Test dependencies
        ("Module Imports", test_imports), # Test module imports
        ("Database", test_database), # Test database functionality
        ("Bitcoin Wallet", test_wallet), # Test Bitcoin wallet functionality
        ("Bitnob API", test_api), # Test Bitnob API functionality
        ("App Integration", test_app_integration) # Test full app integration
    ]
    
    passed = 0 # Counter for passed tests
    total = len(tests) # Total number of tests
    
    for test_name, test_func in tests: # Iterate through each test
        print(f"\n{'='*20} {test_name} {'='*20}") # Print test section header
        try: # Try to run test
            if test_func(): # If test passes
                passed += 1 # Increment passed counter
                print(f"✅ {test_name} PASSED") # Print pass message
            else: # If test fails
                print(f"❌ {test_name} FAILED") # Print fail message
        except Exception as e: # If test throws exception
            print(f"❌ {test_name} FAILED with exception: {e}") # Print exception message
    
    # Cleanup
    cleanup_test_files() # Clean up test files
    
    # Summary
    print(f"\n{'='*60}") # Print separator line
    print(f"📊 Test Results: {passed}/{total} tests passed") # Print test results summary
    print(f"{'='*60}") # Print separator line
    
    if passed == total: # If all tests passed
        print("🎉 ALL TESTS PASSED! App is ready for hackathon submission.") # Print success message
        print("🚀 Run 'python main.py' to start the application.") # Print instructions
        print("🎮 Run 'python demo.py' to see the demo mode.") # Print demo instructions
        return True # Return True for overall success
    else: # If some tests failed
        print("⚠️ Some tests failed. Please fix issues before submission.") # Print warning message
        return False # Return False for overall failure

if __name__ == "__main__": # Check if this script is run directly
    success = main() # Run all tests and get result
    sys.exit(0 if success else 1) # Exit with appropriate code (0 for success, 1 for failure) 