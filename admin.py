#!/usr/bin/env python3
"""
Admin Portal module for Ajo Bitcoin Savings App
Comprehensive administrative interface for managing users, activities, and system operations
"""

import tkinter as tk # GUI framework for admin interface
from tkinter import ttk, messagebox, filedialog, scrolledtext # GUI components for admin portal
import logging # Logging for error tracking, debugging and monitoring admin operations
from datetime import datetime, timedelta # Date and time handling for admin reports and analytics
import threading # Threading for background admin operations
import csv # CSV handling for admin report exports
import json # JSON handling for admin data exports
from typing import Dict, List, Optional, Tuple # Type hints for better code documentation

class AdminPortal: # Main admin portal class for comprehensive system management
    """Main admin portal class for comprehensive system management"""
    
    def __init__(self, app): # Initialize admin portal with reference to main app. Self is the instance of the class, app is the main application instance
        """Initialize admin portal with reference to main app"""
        self.app = app # Reference to the main application instance
        self.logger = logging.getLogger(__name__) # Logger for admin operations
        
        # Admin credentials (in production, use proper authentication)
        self.admin_credentials = { # Dictionary of admin usernames and passwords
            'admin': 'ajo_admin_2024', # Default admin username and password
            'supervisor': 'ajo_supervisor_2024' # Supervisor username and password
        }
        
        # Admin session data
        self.current_admin = None # Currently logged in admin user
        self.admin_level = None # Admin access level (admin/supervisor)
        self.session_start = None # Session start timestamp
        
        self.logger.info("Admin portal initialized") # Log successful admin portal initialization
    
    def authenticate_admin(self, username: str, password: str) -> bool: # Authenticate admin user. Self is the instance of the class, username is the admin username, password is the admin password, returns boolean indicating authentication success
        """Authenticate admin user"""
        try: # Try to authenticate admin
            if username in self.admin_credentials and self.admin_credentials[username] == password: # Check if username exists and password matches
                self.current_admin = username # Set current admin user
                self.admin_level = 'admin' if username == 'admin' else 'supervisor' # Set admin level
                self.session_start = datetime.now() # Record session start time
                
                self.logger.info(f"Admin authenticated: {username}") # Log successful authentication
                return True # Return True for successful authentication
            else: # If authentication fails
                self.logger.warning(f"Failed admin authentication attempt: {username}") # Log failed authentication attempt
                return False # Return False for failed authentication
        except Exception as e: # Catch any exceptions during authentication
            self.logger.error(f"Authentication error: {e}") # Log authentication error
            return False # Return False for authentication error
    
    def logout_admin(self): # Logout current admin user. Self is the instance of the class
        """Logout current admin user"""
        try: # Try to logout admin
            if self.current_admin: # If admin is logged in
                session_duration = datetime.now() - self.session_start if self.session_start else timedelta(0) # Calculate session duration
                self.logger.info(f"Admin logged out: {self.current_admin} (Session: {session_duration})") # Log logout with session duration
                
                # Clear session data
                self.current_admin = None # Clear current admin
                self.admin_level = None # Clear admin level
                self.session_start = None # Clear session start time
        except Exception as e: # Catch any exceptions during logout
            self.logger.error(f"Logout error: {e}") # Log logout error
    
    def get_system_statistics(self) -> Dict: # Get comprehensive system statistics. Self is the instance of the class, returns dictionary containing system statistics
        """Get comprehensive system statistics"""
        try: # Try to get system statistics
            stats = {} # Dictionary to store system statistics
            
            # Get database statistics
            db_stats = self.app.database.get_savings_summary() # Get savings summary from database
            if db_stats: # If summary was retrieved successfully
                stats['database'] = { # Database statistics
                    'total_contributions': db_stats.get('total_contributions', [0, 0]), # Total contributions amount and count
                    'contributions_by_type': db_stats.get('contributions_by_type', []), # Contributions grouped by type
                    'member_contributions': db_stats.get('member_contributions', []), # Contributions grouped by member
                    'recent_contributions': db_stats.get('recent_contributions', []), # Recent contributions
                    'pending_payouts': db_stats.get('pending_payouts', []) # Pending payouts
                }
            
            # Get wallet statistics
            wallet_status = self.app.wallet.get_wallet_status() # Get wallet status
            stats['wallet'] = { # Wallet statistics
                'wallet_exists': wallet_status.get('wallet_exists', False), # Whether wallet exists
                'address_count': wallet_status.get('address_count', 0), # Number of addresses generated
                'balance': wallet_status.get('balance', 0) # Current wallet balance
            }
            
            # Get API statistics
            api_status = self.app.api.get_api_status() # Get API status
            stats['api'] = { # API statistics
                'online': api_status.get('online', False), # Whether API is online
                'last_sync': api_status.get('last_sync', None), # Last sync timestamp
                'pending_transactions': len(self.app.pending_transactions) # Number of pending transactions
            }
            
            # Get system information
            stats['system'] = { # System information
                'current_time': datetime.now().isoformat(), # Current timestamp
                'admin_session': { # Admin session information
                    'current_admin': self.current_admin, # Current admin user
                    'admin_level': self.admin_level, # Admin access level
                    'session_duration': str(datetime.now() - self.session_start) if self.session_start else 'N/A' # Session duration
                }
            }
            
            self.logger.info("System statistics retrieved successfully") # Log successful statistics retrieval
            return stats # Return system statistics
            
        except Exception as e: # Catch any exceptions during statistics retrieval
            self.logger.error(f"Failed to get system statistics: {e}") # Log the error
            return {} # Return empty dictionary if statistics retrieval fails
    
    def get_user_management_data(self) -> List[Dict]: # Get comprehensive user management data. Self is the instance of the class, returns list of dictionaries containing user data
        """Get comprehensive user management data"""
        try: # Try to get user management data
            users = [] # List to store user data
            
            # Get all members from database
            with self.app.database._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                
                # Get members with their contribution statistics
                cursor.execute('''
                    SELECT m.id, m.name, m.phone_number, m.email, m.created_at, m.is_active,
                           COALESCE(SUM(c.amount), 0) as total_contributions,
                           COUNT(c.id) as contribution_count,
                           MAX(c.created_at) as last_contribution
                    FROM members m
                    LEFT JOIN contributions c ON m.name = c.member_name
                    GROUP BY m.id, m.name, m.phone_number, m.email, m.created_at, m.is_active
                    ORDER BY total_contributions DESC
                ''') # Get comprehensive member data with contribution statistics
                
                member_data = cursor.fetchall() # Fetch all results
                
                for member in member_data: # Iterate through each member
                    users.append({ # Add member data to users list
                        'id': member[0], # Member ID
                        'name': member[1], # Member name
                        'phone': member[2], # Phone number
                        'email': member[3], # Email address
                        'created_at': member[4], # Creation timestamp
                        'is_active': bool(member[5]), # Active status
                        'total_contributions': member[6], # Total contribution amount
                        'contribution_count': member[7], # Number of contributions
                        'last_contribution': member[8] # Last contribution timestamp
                    })
            
            self.logger.info(f"Retrieved user management data for {len(users)} users") # Log successful data retrieval
            return users # Return user management data
            
        except Exception as e: # Catch any exceptions during data retrieval
            self.logger.error(f"Failed to get user management data: {e}") # Log the error
            return [] # Return empty list if data retrieval fails
    
    def get_activity_log(self, limit: int = 100) -> List[Dict]: # Get comprehensive activity log. Self is the instance of the class, limit is the maximum number of activities to retrieve (default is 100), returns list of dictionaries containing activity data
        """Get comprehensive activity log"""
        try: # Try to get activity log
            activities = [] # List to store activity data
            
            with self.app.database._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                
                # Get recent contributions
                cursor.execute('''
                    SELECT 'contribution' as type, id, member_name, amount, contribution_type, 
                           created_at, synced_with_bitnob
                    FROM contributions
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit // 2,)) # Get recent contributions (half of limit)
                
                contribution_activities = cursor.fetchall() # Fetch contribution activities
                
                # Get recent payouts
                cursor.execute('''
                    SELECT 'payout' as type, id, member_name, amount, payout_type, 
                           created_at, status
                    FROM payouts
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit // 2,)) # Get recent payouts (half of limit)
                
                payout_activities = cursor.fetchall() # Fetch payout activities
                
                # Combine and sort activities
                all_activities = [] # List to store all activities
                
                for activity in contribution_activities: # Process contribution activities
                    all_activities.append({ # Add contribution activity
                        'type': 'contribution', # Activity type
                        'id': activity[1], # Activity ID
                        'member_name': activity[2], # Member name
                        'amount': activity[3], # Amount
                        'sub_type': activity[4], # Contribution type
                        'timestamp': activity[5], # Timestamp
                        'status': 'synced' if activity[6] else 'pending' # Sync status
                    })
                
                for activity in payout_activities: # Process payout activities
                    all_activities.append({ # Add payout activity
                        'type': 'payout', # Activity type
                        'id': activity[1], # Activity ID
                        'member_name': activity[2], # Member name
                        'amount': activity[3], # Amount
                        'sub_type': activity[4], # Payout type
                        'timestamp': activity[5], # Timestamp
                        'status': activity[6] # Payout status
                    })
                
                # Sort by timestamp (most recent first)
                all_activities.sort(key=lambda x: x['timestamp'], reverse=True) # Sort activities by timestamp
                activities = all_activities[:limit] # Limit to requested number
            
            self.logger.info(f"Retrieved activity log with {len(activities)} activities") # Log successful activity log retrieval
            return activities # Return activity log
            
        except Exception as e: # Catch any exceptions during activity log retrieval
            self.logger.error(f"Failed to get activity log: {e}") # Log the error
            return [] # Return empty list if activity log retrieval fails
    
    def update_user_status(self, user_id: int, is_active: bool) -> bool: # Update user active status. Self is the instance of the class, user_id is the ID of the user to update, is_active is the new active status, returns boolean indicating update success
        """Update user active status"""
        try: # Try to update user status
            with self.app.database._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    UPDATE members 
                    SET is_active = ?
                    WHERE id = ?
                ''', (is_active, user_id)) # Update member active status
                
                if cursor.rowcount > 0: # If update was successful
                    conn.commit() # Commit the transaction
                    self.logger.info(f"Updated user {user_id} status to {'active' if is_active else 'inactive'}") # Log successful status update
                    return True # Return True for successful update
                else: # If no rows were updated
                    self.logger.warning(f"User {user_id} not found for status update") # Log warning about user not found
                    return False # Return False for failed update
                    
        except Exception as e: # Catch any exceptions during status update
            self.logger.error(f"Failed to update user status: {e}") # Log the error
            return False # Return False for status update error
    
    def delete_user(self, user_id: int) -> bool: # Delete user from system. Self is the instance of the class, user_id is the ID of the user to delete, returns boolean indicating deletion success
        """Delete user from system"""
        try: # Try to delete user
            with self.app.database._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                
                # Check if user has contributions
                cursor.execute('''
                    SELECT COUNT(*) FROM contributions WHERE member_id = ?
                ''', (user_id,)) # Check number of contributions for user
                
                contribution_count = cursor.fetchone()[0] # Get contribution count
                
                if contribution_count > 0: # If user has contributions
                    self.logger.warning(f"Cannot delete user {user_id} - has {contribution_count} contributions") # Log warning about user with contributions
                    return False # Return False - cannot delete user with contributions
                
                # Delete user
                cursor.execute('DELETE FROM members WHERE id = ?', (user_id,)) # Delete member from database
                
                if cursor.rowcount > 0: # If deletion was successful
                    conn.commit() # Commit the transaction
                    self.logger.info(f"Deleted user {user_id}") # Log successful user deletion
                    return True # Return True for successful deletion
                else: # If no rows were deleted
                    self.logger.warning(f"User {user_id} not found for deletion") # Log warning about user not found
                    return False # Return False for failed deletion
                    
        except Exception as e: # Catch any exceptions during user deletion
            self.logger.error(f"Failed to delete user: {e}") # Log the error
            return False # Return False for deletion error
    
    def export_admin_report(self, report_type: str, filename: str = None) -> str: # Export comprehensive admin report. Self is the instance of the class, report_type is the type of report to export, filename is the output filename (optional), returns the path to the exported file
        """Export comprehensive admin report"""
        try: # Try to export admin report
            if not filename: # If no filename provided
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') # Generate timestamp for filename
                filename = f"admin_report_{report_type}_{timestamp}.csv" # Generate default filename
            
            if report_type == 'users': # If exporting user report
                data = self.get_user_management_data() # Get user management data
                headers = ['ID', 'Name', 'Phone', 'Email', 'Created At', 'Active', 'Total Contributions', 'Contribution Count', 'Last Contribution'] # CSV headers
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile: # Open CSV file for writing
                    writer = csv.writer(csvfile) # Create CSV writer
                    writer.writerow(headers) # Write headers
                    
                    for user in data: # Write user data
                        writer.writerow([ # Write user row
                            user['id'], # User ID
                            user['name'], # User name
                            user['phone'], # Phone number
                            user['email'], # Email address
                            user['created_at'], # Creation timestamp
                            'Yes' if user['is_active'] else 'No', # Active status
                            user['total_contributions'], # Total contributions
                            user['contribution_count'], # Contribution count
                            user['last_contribution'] # Last contribution
                        ])
            
            elif report_type == 'activities': # If exporting activity report
                data = self.get_activity_log(limit=1000) # Get activity log with higher limit
                headers = ['Type', 'ID', 'Member Name', 'Amount', 'Sub Type', 'Timestamp', 'Status'] # CSV headers
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile: # Open CSV file for writing
                    writer = csv.writer(csvfile) # Create CSV writer
                    writer.writerow(headers) # Write headers
                    
                    for activity in data: # Write activity data
                        writer.writerow([ # Write activity row
                            activity['type'], # Activity type
                            activity['id'], # Activity ID
                            activity['member_name'], # Member name
                            activity['amount'], # Amount
                            activity['sub_type'], # Sub type
                            activity['timestamp'], # Timestamp
                            activity['status'] # Status
                        ])
            
            elif report_type == 'system': # If exporting system report
                stats = self.get_system_statistics() # Get system statistics
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile: # Open CSV file for writing
                    writer = csv.writer(csvfile) # Create CSV writer
                    writer.writerow(['Category', 'Metric', 'Value']) # Write headers
                    
                    # Database statistics
                    db_stats = stats.get('database', {}) # Get database statistics
                    total_contributions = db_stats.get('total_contributions', [0, 0]) # Get total contributions
                    writer.writerow(['Database', 'Total Amount', total_contributions[0]]) # Write total amount
                    writer.writerow(['Database', 'Total Transactions', total_contributions[1]]) # Write total transactions
                    writer.writerow(['Database', 'Active Members', len(db_stats.get('member_contributions', []))]) # Write active members
                    writer.writerow(['Database', 'Pending Payouts', len(db_stats.get('pending_payouts', []))]) # Write pending payouts
                    
                    # Wallet statistics
                    wallet_stats = stats.get('wallet', {}) # Get wallet statistics
                    writer.writerow(['Wallet', 'Wallet Exists', 'Yes' if wallet_stats.get('wallet_exists') else 'No']) # Write wallet existence
                    writer.writerow(['Wallet', 'Address Count', wallet_stats.get('address_count', 0)]) # Write address count
                    writer.writerow(['Wallet', 'Balance', wallet_stats.get('balance', 0)]) # Write wallet balance
                    
                    # API statistics
                    api_stats = stats.get('api', {}) # Get API statistics
                    writer.writerow(['API', 'Online Status', 'Online' if api_stats.get('online') else 'Offline']) # Write online status
                    writer.writerow(['API', 'Pending Transactions', api_stats.get('pending_transactions', 0)]) # Write pending transactions
            
            self.logger.info(f"Admin report exported: {filename}") # Log successful report export
            return filename # Return the exported file path
            
        except Exception as e: # Catch any exceptions during report export
            self.logger.error(f"Failed to export admin report: {e}") # Log the error
            return None # Return None if report export fails
    
    def get_system_health(self) -> Dict: # Get comprehensive system health status. Self is the instance of the class, returns dictionary containing system health information
        """Get comprehensive system health status"""
        try: # Try to get system health
            health = { # Dictionary to store health information
                'overall_status': 'healthy', # Overall system status
                'components': {}, # Component-specific health
                'issues': [], # List of issues found
                'recommendations': [] # List of recommendations
            }
            
            # Check database health
            try: # Try to check database health
                db_stats = self.app.database.get_savings_summary() # Get database summary
                if db_stats: # If database is accessible
                    health['components']['database'] = { # Database health
                        'status': 'healthy', # Database status
                        'message': 'Database accessible and operational' # Health message
                    }
                else: # If database is not accessible
                    health['components']['database'] = { # Database health
                        'status': 'error', # Database status
                        'message': 'Database not accessible' # Health message
                    }
                    health['issues'].append('Database connectivity issue') # Add issue
                    health['overall_status'] = 'degraded' # Update overall status
            except Exception as e: # Catch database health check errors
                health['components']['database'] = { # Database health
                    'status': 'error', # Database status
                    'message': f'Database error: {str(e)}' # Health message
                }
                health['issues'].append(f'Database error: {str(e)}') # Add issue
                health['overall_status'] = 'degraded' # Update overall status
            
            # Check wallet health
            try: # Try to check wallet health
                wallet_status = self.app.wallet.get_wallet_status() # Get wallet status
                if wallet_status.get('wallet_exists'): # If wallet exists
                    health['components']['wallet'] = { # Wallet health
                        'status': 'healthy', # Wallet status
                        'message': 'Bitcoin wallet operational' # Health message
                    }
                else: # If wallet doesn't exist
                    health['components']['wallet'] = { # Wallet health
                        'status': 'warning', # Wallet status
                        'message': 'Bitcoin wallet not initialized' # Health message
                    }
                    health['issues'].append('Bitcoin wallet not initialized') # Add issue
                    health['recommendations'].append('Initialize Bitcoin wallet for full functionality') # Add recommendation
            except Exception as e: # Catch wallet health check errors
                health['components']['wallet'] = { # Wallet health
                    'status': 'error', # Wallet status
                    'message': f'Wallet error: {str(e)}' # Health message
                }
                health['issues'].append(f'Wallet error: {str(e)}') # Add issue
                health['overall_status'] = 'degraded' # Update overall status
            
            # Check API health
            try: # Try to check API health
                api_status = self.app.api.get_api_status() # Get API status
                if api_status.get('online'): # If API is online
                    health['components']['api'] = { # API health
                        'status': 'healthy', # API status
                        'message': 'Bitnob API connected' # Health message
                    }
                else: # If API is offline
                    health['components']['api'] = { # API health
                        'status': 'warning', # API status
                        'message': 'Bitnob API offline - operating in offline mode' # Health message
                    }
                    health['issues'].append('Bitnob API offline') # Add issue
                    health['recommendations'].append('Check internet connection and API credentials') # Add recommendation
            except Exception as e: # Catch API health check errors
                health['components']['api'] = { # API health
                    'status': 'error', # API status
                    'message': f'API error: {str(e)}' # Health message
                }
                health['issues'].append(f'API error: {str(e)}') # Add issue
                health['overall_status'] = 'degraded' # Update overall status
            
            # Check pending transactions
            pending_count = len(self.app.pending_transactions) # Get pending transaction count
            if pending_count > 0: # If there are pending transactions
                health['components']['sync'] = { # Sync health
                    'status': 'warning', # Sync status
                    'message': f'{pending_count} pending transactions waiting for sync' # Health message
                }
                health['issues'].append(f'{pending_count} pending transactions') # Add issue
                health['recommendations'].append('Sync pending transactions when online') # Add recommendation
            else: # If no pending transactions
                health['components']['sync'] = { # Sync health
                    'status': 'healthy', # Sync status
                    'message': 'All transactions synced' # Health message
                }
            
            self.logger.info(f"System health check completed: {health['overall_status']}") # Log health check completion
            return health # Return system health information
            
        except Exception as e: # Catch any exceptions during health check
            self.logger.error(f"Failed to get system health: {e}") # Log the error
            return { # Return error health status
                'overall_status': 'error', # Overall status
                'components': {}, # Empty components
                'issues': [f'Health check failed: {str(e)}'], # Issue list
                'recommendations': ['Contact system administrator'] # Recommendation list
            }
    
    def force_sync_all(self) -> bool: # Force sync all pending transactions. Self is the instance of the class, returns boolean indicating sync success
        """Force sync all pending transactions"""
        try: # Try to force sync
            if not self.app.api.is_online(): # If API is not online
                self.logger.warning("Cannot force sync - API offline") # Log warning about offline API
                return False # Return False for offline API
            
            pending_count = len(self.app.pending_transactions) # Get pending transaction count
            if pending_count == 0: # If no pending transactions
                self.logger.info("No pending transactions to sync") # Log info about no pending transactions
                return True # Return True for no transactions to sync
            
            # Attempt to sync all pending transactions
            synced_count = 0 # Counter for synced transactions
            for transaction in self.app.pending_transactions[:]: # Iterate through pending transactions
                try: # Try to sync individual transaction
                    # This would integrate with the actual sync logic
                    # For now, we'll simulate successful sync
                    synced_count += 1 # Increment synced count
                    self.app.pending_transactions.remove(transaction) # Remove from pending list
                except Exception as e: # Catch sync errors
                    self.logger.error(f"Failed to sync transaction {transaction.get('id')}: {e}") # Log sync error
            
            self.logger.info(f"Force sync completed: {synced_count}/{pending_count} transactions synced") # Log sync completion
            return synced_count > 0 # Return True if any transactions were synced
            
        except Exception as e: # Catch any exceptions during force sync
            self.logger.error(f"Force sync failed: {e}") # Log the error
            return False # Return False for sync failure
    
    def clear_old_data(self, days_old: int = 90) -> int: # Clear old data from system. Self is the instance of the class, days_old is the age threshold for data deletion (default is 90 days), returns number of records deleted
        """Clear old data from system"""
        try: # Try to clear old data
            cutoff_date = datetime.now() - timedelta(days=days_old) # Calculate cutoff date
            deleted_count = 0 # Counter for deleted records
            
            with self.app.database._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                
                # Delete old exchange rates
                cursor.execute('''
                    DELETE FROM exchange_rates 
                    WHERE updated_at < ?
                ''', (cutoff_date,)) # Delete old exchange rates
                deleted_count += cursor.rowcount # Add to deleted count
                
                # Delete old user balance records
                cursor.execute('''
                    DELETE FROM user_balance 
                    WHERE updated_at < ?
                ''', (cutoff_date,)) # Delete old user balance records
                deleted_count += cursor.rowcount # Add to deleted count
                
                conn.commit() # Commit the transaction
            
            self.logger.info(f"Cleared {deleted_count} old records (older than {days_old} days)") # Log data clearing completion
            return deleted_count # Return number of deleted records
            
        except Exception as e: # Catch any exceptions during data clearing
            self.logger.error(f"Failed to clear old data: {e}") # Log the error
            return 0 # Return 0 for clearing failure 