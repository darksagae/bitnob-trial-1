#!/usr/bin/env python3
"""
Database module for Ajo Bitcoin Savings App
Handles local SQLite storage with encryption for offline savings management
"""

import sqlite3 # SQLite database interface for local data storage
import logging # Logging for error tracking, debugging and monitoring database operations
import json # JSON handling for storing encrypted data structures
from datetime import datetime # Date and time handling for timestamps and file naming
from pathlib import Path # Object-oriented filesystem paths for cross-platform directory operations
from Crypto.Cipher import AES # Advanced Encryption Standard for data encryption
from Crypto.Util.Padding import pad, unpad # Padding functions for AES encryption
import base64 # Base64 encoding for storing encrypted data as text
import hashlib # Hash functions for generating encryption keys

class AjoDatabase: # SQLite database manager for Ajo savings app with encryption
    """SQLite database manager for Ajo savings app with encryption"""
    
    def __init__(self, db_path="ajo_savings.db"): # Initialize database with encryption. Self is the instance of the class, db_path is the database file path (default is ajo_savings.db)
        """Initialize database with encryption"""
        self.db_path = db_path # Store the database file path
        self.logger = logging.getLogger(__name__) # Logger for the database class
        
        # Encryption key (in production, this should be stored securely)
        self.encryption_key = self._generate_encryption_key() # Generate encryption key for sensitive data
        
        # Initialize database
        self._create_tables() # Create database tables if they don't exist
        self.logger.info(f"Database initialized: {db_path}") # Log successful database initialization
    
    def _generate_encryption_key(self): # Generate encryption key for sensitive data. Self is the instance of the class
        """Generate encryption key for sensitive data"""
        # In production, use a proper key management system
        key_material = "ajo_bitcoin_savings_uganda_2024" # Key material for generating encryption key
        return hashlib.sha256(key_material.encode()).digest() # Return SHA-256 hash of key material as bytes
    
    def _encrypt_data(self, data): # Encrypt sensitive data before storage. Self is the instance of the class, data is the plaintext data to encrypt
        """Encrypt sensitive data before storage"""
        try: # Try to encrypt the data
            if not data: # If data is empty or None
                return None # Return None for empty data
            
            cipher = AES.new(self.encryption_key, AES.MODE_CBC) # Create AES cipher in CBC mode with random IV
            ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size)) # Encrypt padded data
            iv = base64.b64encode(cipher.iv).decode('utf-8') # Encode initialization vector as base64 string
            ct = base64.b64encode(ct_bytes).decode('utf-8') # Encode ciphertext as base64 string
            return json.dumps({'iv': iv, 'data': ct}) # Return JSON string containing IV and encrypted data
        except Exception as e: # Catch any exceptions during encryption
            self.logger.error(f"Encryption failed: {e}") # Log the encryption error
            return None # Return None if encryption fails
    
    def _decrypt_data(self, encrypted_data): # Decrypt sensitive data after retrieval. Self is the instance of the class, encrypted_data is the JSON string containing encrypted data
        """Decrypt sensitive data after retrieval"""
        try: # Try to decrypt the data
            if not encrypted_data: # If encrypted data is empty or None
                return None # Return None for empty data
            
            b64 = json.loads(encrypted_data) # Parse JSON string to get IV and encrypted data
            iv = base64.b64decode(b64['iv']) # Decode initialization vector from base64
            ct = base64.b64decode(b64['data']) # Decode ciphertext from base64
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv) # Create AES cipher with stored IV
            pt = unpad(cipher.decrypt(ct), AES.block_size) # Decrypt and remove padding
            return pt.decode('utf-8') # Return decrypted data as string
        except Exception as e: # Catch any exceptions during decryption
            self.logger.error(f"Decryption failed: {e}") # Log the decryption error
            return None # Return None if decryption fails
    
    def _get_connection(self): # Get database connection. Self is the instance of the class
        """Get database connection"""
        return sqlite3.connect(self.db_path) # Return SQLite connection
    
    def _create_tables(self): # Create database tables if they don't exist. Self is the instance of the class
        """Create database tables if they don't exist"""
        with self._get_connection() as conn: # Connect to SQLite database
            cursor = conn.cursor() # Create cursor for executing SQL commands
            
            # Users table for authentication and roles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    full_name TEXT,
                    phone_number TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''') # Create users table with authentication and role management
            
            # Groups table for savings groups
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    admin_user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (admin_user_id) REFERENCES users (id)
                )
            ''') # Create groups table for managing savings groups
            
            # Group members table (many-to-many relationship)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (group_id) REFERENCES groups (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(group_id, user_id)
                )
            ''') # Create group members table for user-group relationships
            
            # Members table (legacy - for backward compatibility)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    phone_number TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''') # Create members table with auto-incrementing ID, unique name, phone, email, timestamp, and active status
            
            # Contributions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER,
                    member_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    contribution_type TEXT DEFAULT 'bitcoin',
                    bitcoin_address TEXT,
                    encrypted_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    synced_with_bitnob BOOLEAN DEFAULT 0,
                    FOREIGN KEY (member_id) REFERENCES members (id)
                )
            ''') # Create contributions table with member info, amount, type, Bitcoin address, encrypted notes, timestamp, and sync status
            
            # Payouts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    phone_number TEXT,
                    payout_type TEXT DEFAULT 'mobile_money',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            ''') # Create payouts table with member info, amount, phone, type, status, and timestamps
            
            # Exchange rates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exchange_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency_pair TEXT NOT NULL,
                    rate REAL NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''') # Create exchange rates table for storing currency conversion rates
            
            # User balance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_balance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT NOT NULL,
                    balance REAL NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''') # Create user balance table for storing account balances by currency
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''') # Create settings table for storing application configuration
            
            conn.commit() # Commit all table creation statements
            self.logger.info("Database tables created successfully") # Log successful table creation
    
    def create_user(self, username, password, role='user', full_name=None, phone_number=None, email=None): # Create a new user with authentication. Self is the instance of the class, username is the username, password is the plaintext password, role is the user role (default is user), full_name is the user's full name (optional), phone_number is the phone number (optional), email is the email address (optional)
        """Create a new user with authentication"""
        try: # Try to create user
            # Hash password (simple hash for demo - use proper hashing in production)
            password_hash = self._hash_password(password) # Hash the password
            
            with self._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, full_name, phone_number, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, password_hash, role, full_name, phone_number, email)) # Insert new user
                user_id = cursor.lastrowid # Get the auto-generated user ID
                conn.commit() # Commit the transaction
                
                self.logger.info(f"Created user: {username} with role: {role}") # Log successful user creation
                return user_id # Return the new user ID
        except sqlite3.IntegrityError: # Catch unique constraint violation
            self.logger.warning(f"User already exists: {username}") # Log warning about duplicate user
            return None # Return None for duplicate users
        except Exception as e: # Catch any other exceptions
            self.logger.error(f"Failed to create user: {e}") # Log the error
            return None # Return None if user creation fails
    
    def authenticate_user(self, username, password): # Authenticate user with username and password. Self is the instance of the class, username is the username, password is the plaintext password, returns user data dictionary or None if authentication fails
        """Authenticate user with username and password"""
        try: # Try to authenticate user
            password_hash = self._hash_password(password) # Hash the provided password
            
            with self._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    SELECT id, username, role, full_name, phone_number, email, is_active
                    FROM users
                    WHERE username = ? AND password_hash = ? AND is_active = 1
                ''', (username, password_hash)) # Query user with matching credentials
                
                user_data = cursor.fetchone() # Fetch user data
                
                if user_data: # If user found
                    user_dict = { # Create user dictionary
                        'id': user_data[0], # User ID
                        'username': user_data[1], # Username
                        'role': user_data[2], # User role
                        'full_name': user_data[3], # Full name
                        'phone_number': user_data[4], # Phone number
                        'email': user_data[5], # Email address
                        'is_active': bool(user_data[6]) # Active status
                    }
                    self.logger.info(f"User authenticated: {username}") # Log successful authentication
                    return user_dict # Return user data
                else: # If user not found
                    self.logger.warning(f"Authentication failed for user: {username}") # Log failed authentication
                    return None # Return None for failed authentication
                    
        except Exception as e: # Catch any exceptions during authentication
            self.logger.error(f"Authentication error: {e}") # Log the error
            return None # Return None for authentication error
    
    def get_user_role(self, user_id): # Get user role by user ID. Self is the instance of the class, user_id is the user ID, returns role string or None if user not found
        """Get user role by user ID"""
        try: # Try to get user role
            with self._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    SELECT role FROM users WHERE id = ? AND is_active = 1
                ''', (user_id,)) # Query user role
                
                result = cursor.fetchone() # Fetch result
                return result[0] if result else None # Return role or None
                
        except Exception as e: # Catch any exceptions
            self.logger.error(f"Error getting user role: {e}") # Log the error
            return None # Return None for error
    
    def _hash_password(self, password): # Hash password for storage. Self is the instance of the class, password is the plaintext password, returns hashed password string
        """Hash password for storage (simple hash for demo)"""
        # In production, use proper password hashing (bcrypt, scrypt, etc.)
        return hashlib.sha256(password.encode()).hexdigest() # Return SHA-256 hash of password
    
    def create_group(self, name, description=None, admin_user_id=None): # Create a new savings group. Self is the instance of the class, name is the group name, description is the group description (optional), admin_user_id is the admin user ID (optional)
        """Create a new savings group"""
        try: # Try to create group
            with self._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    INSERT INTO groups (name, description, admin_user_id)
                    VALUES (?, ?, ?)
                ''', (name, description, admin_user_id)) # Insert new group
                group_id = cursor.lastrowid # Get the auto-generated group ID
                conn.commit() # Commit the transaction
                
                self.logger.info(f"Created group: {name}") # Log successful group creation
                return group_id # Return the new group ID
        except sqlite3.IntegrityError: # Catch unique constraint violation
            self.logger.warning(f"Group already exists: {name}") # Log warning about duplicate group
            return None # Return None for duplicate groups
        except Exception as e: # Catch any other exceptions
            self.logger.error(f"Failed to create group: {e}") # Log the error
            return None # Return None if group creation fails
    
    def get_all_groups(self): # Get all active groups. Self is the instance of the class, returns list of group dictionaries
        """Get all active groups"""
        try: # Try to get groups
            with self._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    SELECT g.id, g.name, g.description, g.created_at, 
                           u.full_name as admin_name, COUNT(gm.user_id) as member_count
                    FROM groups g
                    LEFT JOIN users u ON g.admin_user_id = u.id
                    LEFT JOIN group_members gm ON g.id = gm.group_id AND gm.is_active = 1
                    WHERE g.is_active = 1
                    GROUP BY g.id
                    ORDER BY g.created_at DESC
                ''') # Query all active groups with member count
                
                groups = [] # List to store groups
                for row in cursor.fetchall(): # Iterate through results
                    groups.append({ # Add group data
                        'id': row[0], # Group ID
                        'name': row[1], # Group name
                        'description': row[2], # Group description
                        'created_at': row[3], # Creation timestamp
                        'admin_name': row[4], # Admin name
                        'member_count': row[5] # Member count
                    })
                
                return groups # Return groups list
                
        except Exception as e: # Catch any exceptions
            self.logger.error(f"Error getting groups: {e}") # Log the error
            return [] # Return empty list for error
    
    def add_member(self, name, phone_number=None, email=None): # Add a new member to the savings group. Self is the instance of the class, name is the member's name, phone_number is the member's phone number (optional), email is the member's email (optional)
        """Add a new member to the savings group"""
        try: # Try to add the member
            with self._get_connection() as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    INSERT INTO members (name, phone_number, email)
                    VALUES (?, ?, ?)
                ''', (name, phone_number, email)) # Insert new member with name, phone, and email
                member_id = cursor.lastrowid # Get the auto-generated member ID
                conn.commit() # Commit the transaction
                
                self.logger.info(f"Added member: {name}") # Log successful member addition
                return member_id # Return the new member ID
        except sqlite3.IntegrityError: # Catch unique constraint violation
            self.logger.warning(f"Member already exists: {name}") # Log warning about duplicate member
            return None # Return None for duplicate members
        except Exception as e: # Catch any other exceptions
            self.logger.error(f"Failed to add member: {e}") # Log the error
            return None # Return None if member addition fails
    
    def add_contribution(self, member_name, amount, contribution_type="bitcoin", 
                        bitcoin_address=None, notes=None): # Add a new contribution to the savings group. Self is the instance of the class, member_name is the member's name, amount is the contribution amount, contribution_type is the type of contribution (default is bitcoin), bitcoin_address is the Bitcoin address (optional), notes are additional notes (optional)
        """Add a new contribution to the savings group"""
        try: # Try to add the contribution
            # Encrypt notes if provided
            encrypted_notes = self._encrypt_data(notes) if notes else None # Encrypt notes if provided, otherwise None
            
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    INSERT INTO contributions 
                    (member_name, amount, contribution_type, bitcoin_address, encrypted_notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (member_name, amount, contribution_type, bitcoin_address, encrypted_notes)) # Insert new contribution with all details
                contribution_id = cursor.lastrowid # Get the auto-generated contribution ID
                conn.commit() # Commit the transaction
                
                self.logger.info(f"Added contribution: {member_name} - {amount} {contribution_type}") # Log successful contribution addition
                return contribution_id # Return the new contribution ID
        except Exception as e: # Catch any exceptions during contribution addition
            self.logger.error(f"Failed to add contribution: {e}") # Log the error
            return None # Return None if contribution addition fails
    
    def get_savings_summary(self): # Get comprehensive savings group summary. Self is the instance of the class
        """Get comprehensive savings group summary"""
        try: # Try to get savings summary
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                
                # Total contributions by type
                cursor.execute('''
                    SELECT contribution_type, SUM(amount), COUNT(*)
                    FROM contributions
                    GROUP BY contribution_type
                ''') # Get total amount and count for each contribution type
                contributions_by_type = cursor.fetchall() # Fetch all results
                
                # Total contributions
                cursor.execute('''
                    SELECT SUM(amount), COUNT(*)
                    FROM contributions
                ''') # Get overall total amount and count of all contributions
                total_contributions = cursor.fetchone() # Fetch single result
                
                # Member contributions
                cursor.execute('''
                    SELECT member_name, SUM(amount), COUNT(*)
                    FROM contributions
                    GROUP BY member_name
                    ORDER BY SUM(amount) DESC
                ''') # Get total amount and count for each member, ordered by amount descending
                member_contributions = cursor.fetchall() # Fetch all results
                
                # Recent contributions
                cursor.execute('''
                    SELECT member_name, amount, contribution_type, created_at
                    FROM contributions
                    ORDER BY created_at DESC
                    LIMIT 10
                ''') # Get 10 most recent contributions
                recent_contributions = cursor.fetchall() # Fetch all results
                
                # Pending payouts
                cursor.execute('''
                    SELECT member_name, amount, status
                    FROM payouts
                    WHERE status = 'pending'
                ''') # Get all pending payouts
                pending_payouts = cursor.fetchall() # Fetch all results
                
                return { # Return comprehensive summary dictionary
                    'contributions_by_type': contributions_by_type, # Contributions grouped by type
                    'total_contributions': total_contributions, # Overall totals
                    'member_contributions': member_contributions, # Contributions grouped by member
                    'recent_contributions': recent_contributions, # Recent contributions
                    'pending_payouts': pending_payouts # Pending payouts
                }
        except Exception as e: # Catch any exceptions during summary retrieval
            self.logger.error(f"Failed to get savings summary: {e}") # Log the error
            return None # Return None if summary retrieval fails
    
    def get_member_contributions(self, member_name): # Get all contributions for a specific member. Self is the instance of the class, member_name is the name of the member
        """Get all contributions for a specific member"""
        try: # Try to get member contributions
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    SELECT id, amount, contribution_type, bitcoin_address, 
                           encrypted_notes, created_at, synced_with_bitnob
                    FROM contributions
                    WHERE member_name = ?
                    ORDER BY created_at DESC
                ''', (member_name,)) # Get all contributions for specific member, ordered by date descending
                
                contributions = cursor.fetchall() # Fetch all results
                
                # Decrypt notes
                decrypted_contributions = [] # List to store decrypted contributions
                for contrib in contributions: # Iterate through each contribution
                    decrypted_notes = self._decrypt_data(contrib[4]) if contrib[4] else None # Decrypt notes if they exist
                    decrypted_contributions.append({ # Add decrypted contribution to list
                        'id': contrib[0], # Contribution ID
                        'amount': contrib[1], # Amount
                        'contribution_type': contrib[2], # Type
                        'bitcoin_address': contrib[3], # Bitcoin address
                        'notes': decrypted_notes, # Decrypted notes
                        'created_at': contrib[5], # Creation timestamp
                        'synced': contrib[6] # Sync status
                    })
                
                return decrypted_contributions # Return list of decrypted contributions
        except Exception as e: # Catch any exceptions during contribution retrieval
            self.logger.error(f"Failed to get member contributions: {e}") # Log the error
            return [] # Return empty list if retrieval fails
    
    def mark_contribution_synced(self, contribution_id): # Mark a contribution as synced with Bitnob API. Self is the instance of the class, contribution_id is the ID of the contribution to mark as synced
        """Mark a contribution as synced with Bitnob API"""
        try: # Try to mark contribution as synced
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    UPDATE contributions
                    SET synced_with_bitnob = 1
                    WHERE id = ?
                ''', (contribution_id,)) # Update contribution to mark it as synced
                conn.commit() # Commit the transaction
                
                self.logger.info(f"Marked contribution {contribution_id} as synced") # Log successful sync marking
        except Exception as e: # Catch any exceptions during sync marking
            self.logger.error(f"Failed to mark contribution as synced: {e}") # Log the error
    
    def record_payout(self, member_name, amount, phone_number, payout_type="mobile_money"): # Record a payout transaction. Self is the instance of the class, member_name is the name of the member, amount is the payout amount, phone_number is the recipient's phone number, payout_type is the type of payout (default is mobile_money)
        """Record a payout transaction"""
        try: # Try to record the payout
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    INSERT INTO payouts (member_name, amount, phone_number, payout_type)
                    VALUES (?, ?, ?, ?)
                ''', (member_name, amount, phone_number, payout_type)) # Insert new payout record
                payout_id = cursor.lastrowid # Get the auto-generated payout ID
                conn.commit() # Commit the transaction
                
                self.logger.info(f"Recorded payout: {member_name} - {amount}") # Log successful payout recording
                return payout_id # Return the new payout ID
        except Exception as e: # Catch any exceptions during payout recording
            self.logger.error(f"Failed to record payout: {e}") # Log the error
            return None # Return None if payout recording fails
    
    def update_payout_status(self, payout_id, status): # Update payout status. Self is the instance of the class, payout_id is the ID of the payout, status is the new status
        """Update payout status"""
        try: # Try to update payout status
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    UPDATE payouts
                    SET status = ?, processed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, payout_id)) # Update payout status and set processed timestamp
                conn.commit() # Commit the transaction
                
                self.logger.info(f"Updated payout {payout_id} status to {status}") # Log successful status update
        except Exception as e: # Catch any exceptions during status update
            self.logger.error(f"Failed to update payout status: {e}") # Log the error
    
    def update_exchange_rates(self, rates): # Update exchange rates from Bitnob API. Self is the instance of the class, rates is a dictionary of currency pairs and their rates
        """Update exchange rates from Bitnob API"""
        try: # Try to update exchange rates
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                
                for currency_pair, rate in rates.items(): # Iterate through each currency pair and rate
                    cursor.execute('''
                        INSERT OR REPLACE INTO exchange_rates (currency_pair, rate)
                        VALUES (?, ?)
                    ''', (currency_pair, rate)) # Insert or update exchange rate for currency pair
                
                conn.commit() # Commit all exchange rate updates
                self.logger.info("Exchange rates updated") # Log successful exchange rate update
        except Exception as e: # Catch any exceptions during exchange rate update
            self.logger.error(f"Failed to update exchange rates: {e}") # Log the error
    
    def update_user_balance(self, balance_data): # Update user balance from Bitnob API. Self is the instance of the class, balance_data is a dictionary of currencies and their balances
        """Update user balance from Bitnob API"""
        try: # Try to update user balance
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                
                for currency, balance in balance_data.items(): # Iterate through each currency and balance
                    cursor.execute('''
                        INSERT OR REPLACE INTO user_balance (currency, balance)
                        VALUES (?, ?)
                    ''', (currency, balance)) # Insert or update balance for currency
                
                conn.commit() # Commit all balance updates
                self.logger.info("User balance updated") # Log successful balance update
        except Exception as e: # Catch any exceptions during balance update
            self.logger.error(f"Failed to update user balance: {e}") # Log the error
    
    def get_setting(self, key, default=None): # Get application setting. Self is the instance of the class, key is the setting key, default is the default value if setting doesn't exist
        """Get application setting"""
        try: # Try to get the setting
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('SELECT value FROM settings WHERE key = ?', (key,)) # Get setting value by key
                result = cursor.fetchone() # Fetch single result
                return result[0] if result else default # Return setting value or default if not found
        except Exception as e: # Catch any exceptions during setting retrieval
            self.logger.error(f"Failed to get setting {key}: {e}") # Log the error
            return default # Return default value if retrieval fails
    
    def set_setting(self, key, value): # Set application setting. Self is the instance of the class, key is the setting key, value is the setting value
        """Set application setting"""
        try: # Try to set the setting
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value)
                    VALUES (?, ?)
                ''', (key, value)) # Insert or update setting
                conn.commit() # Commit the transaction
                
                self.logger.info(f"Setting updated: {key}") # Log successful setting update
        except Exception as e: # Catch any exceptions during setting update
            self.logger.error(f"Failed to set setting {key}: {e}") # Log the error
    
    def export_savings_report(self): # Export savings data for reporting. Self is the instance of the class
        """Export savings data for reporting"""
        try: # Try to export savings report
            with sqlite3.connect(self.db_path) as conn: # Connect to database
                cursor = conn.cursor() # Create cursor for executing SQL commands
                cursor.execute('''
                    SELECT member_name, amount, contribution_type, 
                           created_at, bitcoin_address
                    FROM contributions
                    ORDER BY created_at DESC
                ''') # Get all contributions ordered by date descending
                return cursor.fetchall() # Return all results
        except Exception as e: # Catch any exceptions during report export
            self.logger.error(f"Failed to export savings report: {e}") # Log the error
            return [] # Return empty list if export fails
    
    def backup_database(self, backup_path=None): # Create a backup of the database. Self is the instance of the class, backup_path is the path for the backup file (optional)
        """Create a backup of the database"""
        try: # Try to backup the database
            if not backup_path: # If no backup path provided
                backup_path = f"backups/ajo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db" # Generate backup path with timestamp
            
            Path(backup_path).parent.mkdir(exist_ok=True) # Create backup directory if it doesn't exist
            
            with sqlite3.connect(self.db_path) as source_conn: # Connect to source database
                with sqlite3.connect(backup_path) as backup_conn: # Connect to backup database
                    source_conn.backup(backup_conn) # Copy source database to backup
            
            self.logger.info(f"Database backed up to: {backup_path}") # Log successful backup
            return backup_path # Return the backup file path
        except Exception as e: # Catch any exceptions during backup
            self.logger.error(f"Failed to backup database: {e}") # Log the error
            return None # Return None if backup fails 