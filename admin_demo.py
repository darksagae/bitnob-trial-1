#!/usr/bin/env python3
"""
Admin Portal Demo for Ajo Bitcoin Savings App
Demonstrates comprehensive admin functionality with sample data
"""

import logging # Logging for demo operations
from datetime import datetime, timedelta # Date and time handling for demo data
from main import AjoApp # Main application class
from admin import AdminPortal # Admin portal class

def setup_demo_data(app): # Setup demo data for admin portal testing. App is the main application instance
    """Setup demo data for admin portal testing"""
    try: # Try to setup demo data
        print("📊 Setting up demo data for admin portal...") # Print setup message
        
        # Add demo members
        members = [ # List of demo members
            ("John Doe", "+256701234567", "john@example.com"), # Demo member 1
            ("Jane Smith", "+256702345678", "jane@example.com"), # Demo member 2
            ("Bob Johnson", "+256703456789", "bob@example.com"), # Demo member 3
            ("Alice Brown", "+256704567890", "alice@example.com"), # Demo member 4
            ("Charlie Wilson", "+256705678901", "charlie@example.com"), # Demo member 5
            ("Diana Davis", "+256706789012", "diana@example.com"), # Demo member 6
            ("Edward Miller", "+256707890123", "edward@example.com"), # Demo member 7
            ("Fiona Garcia", "+256708901234", "fiona@example.com") # Demo member 8
        ]
        
        for name, phone, email in members: # Iterate through demo members
            app.database.add_member(name, phone, email) # Add member to database
        
        # Add demo contributions
        contributions = [ # List of demo contributions
            ("John Doe", 0.001, "bitcoin"), # Bitcoin contribution
            ("Jane Smith", 50.0, "usdt"), # USDT contribution
            ("Bob Johnson", 100000, "ugx"), # UGX contribution
            ("Alice Brown", 0.002, "bitcoin"), # Bitcoin contribution
            ("Charlie Wilson", 75.0, "usdt"), # USDT contribution
            ("Diana Davis", 150000, "ugx"), # UGX contribution
            ("Edward Miller", 0.0015, "bitcoin"), # Bitcoin contribution
            ("Fiona Garcia", 25.0, "usdt"), # USDT contribution
            ("John Doe", 200000, "ugx"), # UGX contribution
            ("Jane Smith", 0.003, "bitcoin"), # Bitcoin contribution
            ("Bob Johnson", 100.0, "usdt"), # USDT contribution
            ("Alice Brown", 300000, "ugx"), # UGX contribution
            ("Charlie Wilson", 0.0025, "bitcoin"), # Bitcoin contribution
            ("Diana Davis", 125.0, "usdt"), # USDT contribution
            ("Edward Miller", 250000, "ugx") # UGX contribution
        ]
        
        for member, amount, contrib_type in contributions: # Iterate through demo contributions
            app.add_contribution(member, amount, contrib_type) # Add contribution
        
        # Add demo payouts
        payouts = [ # List of demo payouts
            ("John Doe", 50000, "+256701234567"), # Demo payout 1
            ("Jane Smith", 75000, "+256702345678"), # Demo payout 2
            ("Bob Johnson", 100000, "+256703456789"), # Demo payout 3
            ("Alice Brown", 125000, "+256704567890"), # Demo payout 4
            ("Charlie Wilson", 150000, "+256705678901") # Demo payout 5
        ]
        
        for member, amount, phone in payouts: # Iterate through demo payouts
            app.database.record_payout(member, amount, phone) # Record payout
        
        # Update some payouts as processed
        app.database.update_payout_status(1, "completed") # Update payout status
        app.database.update_payout_status(2, "completed") # Update payout status
        app.database.update_payout_status(3, "failed") # Update payout status
        
        print("✅ Demo data setup completed!") # Print completion message
        print(f"   - {len(members)} members added") # Print member count
        print(f"   - {len(contributions)} contributions added") # Print contribution count
        print(f"   - {len(payouts)} payouts added") # Print payout count
        
    except Exception as e: # Catch any exceptions during demo setup
        print(f"❌ Error setting up demo data: {e}") # Print error message
        logging.error(f"Demo data setup failed: {e}") # Log the error

def test_admin_portal(app): # Test admin portal functionality. App is the main application instance
    """Test admin portal functionality"""
    try: # Try to test admin portal
        print("\n🔐 Testing Admin Portal...") # Print test message
        
        # Initialize admin portal
        admin = AdminPortal(app) # Create admin portal instance
        
        # Test authentication
        print("\n1. Testing Authentication:") # Print test section
        print("   - Testing valid admin credentials...") # Print test step
        if admin.authenticate_admin("admin", "ajo_admin_2024"): # Test admin authentication
            print("   ✅ Admin authentication successful") # Print success message
        else: # If authentication failed
            print("   ❌ Admin authentication failed") # Print failure message
        
        print("   - Testing invalid credentials...") # Print test step
        if not admin.authenticate_admin("invalid", "wrong_password"): # Test invalid authentication
            print("   ✅ Invalid authentication correctly rejected") # Print success message
        else: # If invalid authentication succeeded
            print("   ❌ Invalid authentication incorrectly accepted") # Print failure message
        
        # Test system statistics
        print("\n2. Testing System Statistics:") # Print test section
        stats = admin.get_system_statistics() # Get system statistics
        if stats: # If statistics retrieved successfully
            print("   ✅ System statistics retrieved") # Print success message
            db_stats = stats.get('database', {}) # Get database statistics
            total_contributions = db_stats.get('total_contributions', [0, 0]) # Get total contributions
            print(f"   - Total contributions: {total_contributions[0]:.2f}") # Print total amount
            print(f"   - Transaction count: {total_contributions[1]}") # Print transaction count
        else: # If statistics retrieval failed
            print("   ❌ Failed to retrieve system statistics") # Print failure message
        
        # Test user management
        print("\n3. Testing User Management:") # Print test section
        users = admin.get_user_management_data() # Get user management data
        if users: # If user data retrieved successfully
            print(f"   ✅ Retrieved {len(users)} users") # Print success message
            print(f"   - Active users: {sum(1 for u in users if u['is_active'])}") # Print active user count
            print(f"   - Total contributions: {sum(u['total_contributions'] for u in users):.2f}") # Print total contributions
        else: # If user data retrieval failed
            print("   ❌ Failed to retrieve user data") # Print failure message
        
        # Test activity log
        print("\n4. Testing Activity Log:") # Print test section
        activities = admin.get_activity_log(limit=20) # Get activity log
        if activities: # If activity log retrieved successfully
            print(f"   ✅ Retrieved {len(activities)} activities") # Print success message
            contribution_count = sum(1 for a in activities if a['type'] == 'contribution') # Count contributions
            payout_count = sum(1 for a in activities if a['type'] == 'payout') # Count payouts
            print(f"   - Contributions: {contribution_count}") # Print contribution count
            print(f"   - Payouts: {payout_count}") # Print payout count
        else: # If activity log retrieval failed
            print("   ❌ Failed to retrieve activity log") # Print failure message
        
        # Test system health
        print("\n5. Testing System Health:") # Print test section
        health = admin.get_system_health() # Get system health
        if health: # If health check successful
            print(f"   ✅ System health: {health['overall_status']}") # Print health status
            print(f"   - Issues found: {len(health['issues'])}") # Print issue count
            print(f"   - Recommendations: {len(health['recommendations'])}") # Print recommendation count
        else: # If health check failed
            print("   ❌ Failed to check system health") # Print failure message
        
        # Test report export
        print("\n6. Testing Report Export:") # Print test section
        try: # Try to export reports
            user_report = admin.export_admin_report('users', 'demo_user_report.csv') # Export user report
            if user_report: # If export successful
                print(f"   ✅ User report exported: {user_report}") # Print success message
            
            activity_report = admin.export_admin_report('activities', 'demo_activity_report.csv') # Export activity report
            if activity_report: # If export successful
                print(f"   ✅ Activity report exported: {activity_report}") # Print success message
            
            system_report = admin.export_admin_report('system', 'demo_system_report.csv') # Export system report
            if system_report: # If export successful
                print(f"   ✅ System report exported: {system_report}") # Print success message
        except Exception as e: # Catch export errors
            print(f"   ❌ Report export failed: {e}") # Print error message
        
        # Test user status update
        print("\n7. Testing User Status Management:") # Print test section
        if users: # If users exist
            test_user = users[0] # Get first user
            original_status = test_user['is_active'] # Get original status
            new_status = not original_status # Toggle status
            
            if admin.update_user_status(test_user['id'], new_status): # Update user status
                print(f"   ✅ Updated user {test_user['name']} status to {'active' if new_status else 'inactive'}") # Print success message
                
                # Restore original status
                admin.update_user_status(test_user['id'], original_status) # Restore original status
                print(f"   ✅ Restored user {test_user['name']} status") # Print success message
            else: # If status update failed
                print(f"   ❌ Failed to update user {test_user['name']} status") # Print failure message
        
        # Test data clearing
        print("\n8. Testing Data Management:") # Print test section
        try: # Try to clear old data
            deleted_count = admin.clear_old_data(days=1) # Clear data older than 1 day
            print(f"   ✅ Cleared {deleted_count} old records") # Print success message
        except Exception as e: # Catch clearing errors
            print(f"   ❌ Data clearing failed: {e}") # Print error message
        
        # Logout
        admin.logout_admin() # Logout admin
        print("\n✅ Admin portal testing completed successfully!") # Print completion message
        
    except Exception as e: # Catch any exceptions during testing
        print(f"❌ Admin portal testing failed: {e}") # Print error message
        logging.error(f"Admin portal testing failed: {e}") # Log the error

def run_interactive_admin_demo(): # Run interactive admin demo. No parameters, provides interactive demo interface
    """Run interactive admin demo"""
    print("\n🎮 Interactive Admin Portal Demo") # Print demo header
    print("=" * 50) # Print separator line
    
    # Initialize app
    app = AjoApp() # Create main application instance
    admin = AdminPortal(app) # Create admin portal instance
    
    # Setup demo data
    setup_demo_data(app) # Setup demo data
    
    while True: # Infinite loop for interactive menu
        print("\nChoose an admin function:") # Print menu header
        print("1. View system statistics") # Menu option 1
        print("2. View user management data") # Menu option 2
        print("3. View activity log") # Menu option 3
        print("4. Check system health") # Menu option 4
        print("5. Export reports") # Menu option 5
        print("6. Test user management") # Menu option 6
        print("7. Run full admin test") # Menu option 7
        print("8. Exit demo") # Menu option 8
        
        choice = input("\nEnter your choice (1-8): ").strip() # Get user input
        
        if choice == "1": # If user chose option 1
            print("\n📊 System Statistics:") # Print section header
            stats = admin.get_system_statistics() # Get system statistics
            if stats: # If statistics retrieved successfully
                db_stats = stats.get('database', {}) # Get database statistics
                total_contributions = db_stats.get('total_contributions', [0, 0]) # Get total contributions
                print(f"Total Amount: {total_contributions[0]:.2f}") # Print total amount
                print(f"Total Transactions: {total_contributions[1]}") # Print transaction count
                print(f"Active Members: {len(db_stats.get('member_contributions', []))}") # Print member count
            else: # If statistics retrieval failed
                print("Failed to retrieve statistics") # Print error message
        
        elif choice == "2": # If user chose option 2
            print("\n👥 User Management Data:") # Print section header
            users = admin.get_user_management_data() # Get user management data
            if users: # If user data retrieved successfully
                print(f"Total Users: {len(users)}") # Print user count
                active_users = [u for u in users if u['is_active']] # Get active users
                print(f"Active Users: {len(active_users)}") # Print active user count
                print("\nTop Contributors:") # Print header
                sorted_users = sorted(users, key=lambda x: x['total_contributions'], reverse=True) # Sort users by contributions
                for user in sorted_users[:5]: # Show top 5 users
                    print(f"  {user['name']}: {user['total_contributions']:.2f}") # Print user contribution
            else: # If user data retrieval failed
                print("Failed to retrieve user data") # Print error message
        
        elif choice == "3": # If user chose option 3
            print("\n📋 Activity Log:") # Print section header
            activities = admin.get_activity_log(limit=10) # Get activity log
            if activities: # If activity log retrieved successfully
                print(f"Recent Activities ({len(activities)}):") # Print activity count
                for activity in activities: # Iterate through activities
                    print(f"  {activity['type']}: {activity['member_name']} - {activity['amount']:.2f} {activity['sub_type']} ({activity['status']})") # Print activity details
            else: # If activity log retrieval failed
                print("Failed to retrieve activity log") # Print error message
        
        elif choice == "4": # If user chose option 4
            print("\n🏥 System Health:") # Print section header
            health = admin.get_system_health() # Get system health
            if health: # If health check successful
                print(f"Overall Status: {health['overall_status']}") # Print health status
                if health['issues']: # If issues found
                    print("Issues:") # Print issues header
                    for issue in health['issues']: # Iterate through issues
                        print(f"  - {issue}") # Print issue
                if health['recommendations']: # If recommendations found
                    print("Recommendations:") # Print recommendations header
                    for rec in health['recommendations']: # Iterate through recommendations
                        print(f"  - {rec}") # Print recommendation
            else: # If health check failed
                print("Failed to check system health") # Print error message
        
        elif choice == "5": # If user chose option 5
            print("\n📤 Export Reports:") # Print section header
            try: # Try to export reports
                user_report = admin.export_admin_report('users') # Export user report
                if user_report: # If export successful
                    print(f"User report: {user_report}") # Print report path
                
                activity_report = admin.export_admin_report('activities') # Export activity report
                if activity_report: # If export successful
                    print(f"Activity report: {activity_report}") # Print report path
                
                system_report = admin.export_admin_report('system') # Export system report
                if system_report: # If export successful
                    print(f"System report: {system_report}") # Print report path
                
                print("Reports exported successfully!") # Print success message
            except Exception as e: # Catch export errors
                print(f"Export failed: {e}") # Print error message
        
        elif choice == "6": # If user chose option 6
            print("\n👤 User Management Test:") # Print section header
            users = admin.get_user_management_data() # Get user management data
            if users: # If users exist
                test_user = users[0] # Get first user
                print(f"Testing with user: {test_user['name']}") # Print test user
                
                # Test status toggle
                original_status = test_user['is_active'] # Get original status
                new_status = not original_status # Toggle status
                
                if admin.update_user_status(test_user['id'], new_status): # Update user status
                    print(f"✅ Status updated to {'active' if new_status else 'inactive'}") # Print success message
                    admin.update_user_status(test_user['id'], original_status) # Restore original status
                    print("✅ Status restored") # Print success message
                else: # If status update failed
                    print("❌ Status update failed") # Print failure message
            else: # If no users exist
                print("No users available for testing") # Print error message
        
        elif choice == "7": # If user chose option 7
            print("\n🧪 Running Full Admin Test...") # Print test message
            test_admin_portal(app) # Run full admin test
        
        elif choice == "8": # If user chose option 8
            print("👋 Thanks for trying the Admin Portal Demo!") # Print goodbye message
            break # Exit loop
        
        else: # If invalid choice
            print("❌ Invalid choice. Please try again.") # Print error message

def main(): # Main entry point for admin demo
    """Main entry point for admin demo"""
    print("🔐 Ajo Bitcoin Savings App - Admin Portal Demo") # Print demo title
    print("=" * 60) # Print separator line
    
    try: # Try to run demo
        # Setup logging
        logging.basicConfig(level=logging.INFO) # Setup basic logging
        
        # Run interactive demo
        run_interactive_admin_demo() # Run interactive demo
        
    except KeyboardInterrupt: # Handle user interruption
        print("\n👋 Demo interrupted by user") # Print interruption message
    except Exception as e: # Catch any other exceptions
        print(f"❌ Demo failed: {e}") # Print error message
        logging.error(f"Admin demo failed: {e}") # Log the error

if __name__ == "__main__": # If script is run directly
    main() # Run main function 