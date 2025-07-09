#!/usr/bin/env python3
"""
Database module for Ajo Bitcoin Savings App
Handles local SQLite storage with encryption for offline savings management
"""

import sqlite3
import logging
import json
from datetime import datetime
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

class AjoDatabase:
    """SQLite database manager for Ajo savings app with encryption"""
    
    def __init__(self, db_path="ajo_savings.db"):
        """Initialize database with encryption"""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Encryption key (in production, this should be stored securely)
        self.encryption_key = self._generate_encryption_key()
        
        # Initialize database
        self._create_tables()
        self.logger.info(f"Database initialized: {db_path}")
    
    def _generate_encryption_key(self):
        """Generate encryption key for sensitive data"""
        # In production, use a proper key management system
        key_material = "ajo_bitcoin_savings_uganda_2024"
        return hashlib.sha256(key_material.encode()).digest()
    
    def _encrypt_data(self, data):
        """Encrypt sensitive data before storage"""
        try:
            if not data:
                return None
            
            cipher = AES.new(self.encryption_key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
            iv = base64.b64encode(cipher.iv).decode('utf-8')
            ct = base64.b64encode(ct_bytes).decode('utf-8')
            return json.dumps({'iv': iv, 'data': ct})
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return None
    
    def _decrypt_data(self, encrypted_data):
        """Decrypt sensitive data after retrieval"""
        try:
            if not encrypted_data:
                return None
            
            b64 = json.loads(encrypted_data)
            iv = base64.b64decode(b64['iv'])
            ct = base64.b64decode(b64['data'])
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return None
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    phone_number TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
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
            ''')
            
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
            ''')
            
            # Exchange rates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exchange_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency_pair TEXT NOT NULL,
                    rate REAL NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User balance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_balance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT NOT NULL,
                    balance REAL NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            self.logger.info("Database tables created successfully")
    
    def add_member(self, name, phone_number=None, email=None):
        """Add a new member to the savings group"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO members (name, phone_number, email)
                    VALUES (?, ?, ?)
                ''', (name, phone_number, email))
                member_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Added member: {name}")
                return member_id
        except sqlite3.IntegrityError:
            self.logger.warning(f"Member already exists: {name}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to add member: {e}")
            return None
    
    def add_contribution(self, member_name, amount, contribution_type="bitcoin", 
                        bitcoin_address=None, notes=None):
        """Add a new contribution to the savings group"""
        try:
            # Encrypt notes if provided
            encrypted_notes = self._encrypt_data(notes) if notes else None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO contributions 
                    (member_name, amount, contribution_type, bitcoin_address, encrypted_notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (member_name, amount, contribution_type, bitcoin_address, encrypted_notes))
                contribution_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Added contribution: {member_name} - {amount} {contribution_type}")
                return contribution_id
        except Exception as e:
            self.logger.error(f"Failed to add contribution: {e}")
            return None
    
    def get_savings_summary(self):
        """Get comprehensive savings group summary"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total contributions by type
                cursor.execute('''
                    SELECT contribution_type, SUM(amount), COUNT(*)
                    FROM contributions
                    GROUP BY contribution_type
                ''')
                contributions_by_type = cursor.fetchall()
                
                # Total contributions
                cursor.execute('''
                    SELECT SUM(amount), COUNT(*)
                    FROM contributions
                ''')
                total_contributions = cursor.fetchone()
                
                # Member contributions
                cursor.execute('''
                    SELECT member_name, SUM(amount), COUNT(*)
                    FROM contributions
                    GROUP BY member_name
                    ORDER BY SUM(amount) DESC
                ''')
                member_contributions = cursor.fetchall()
                
                # Recent contributions
                cursor.execute('''
                    SELECT member_name, amount, contribution_type, created_at
                    FROM contributions
                    ORDER BY created_at DESC
                    LIMIT 10
                ''')
                recent_contributions = cursor.fetchall()
                
                # Pending payouts
                cursor.execute('''
                    SELECT member_name, amount, status
                    FROM payouts
                    WHERE status = 'pending'
                ''')
                pending_payouts = cursor.fetchall()
                
                return {
                    'contributions_by_type': contributions_by_type,
                    'total_contributions': total_contributions,
                    'member_contributions': member_contributions,
                    'recent_contributions': recent_contributions,
                    'pending_payouts': pending_payouts
                }
        except Exception as e:
            self.logger.error(f"Failed to get savings summary: {e}")
            return None
    
    def get_member_contributions(self, member_name):
        """Get all contributions for a specific member"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, amount, contribution_type, bitcoin_address, 
                           encrypted_notes, created_at, synced_with_bitnob
                    FROM contributions
                    WHERE member_name = ?
                    ORDER BY created_at DESC
                ''', (member_name,))
                
                contributions = cursor.fetchall()
                
                # Decrypt notes
                decrypted_contributions = []
                for contrib in contributions:
                    decrypted_notes = self._decrypt_data(contrib[4]) if contrib[4] else None
                    decrypted_contributions.append({
                        'id': contrib[0],
                        'amount': contrib[1],
                        'contribution_type': contrib[2],
                        'bitcoin_address': contrib[3],
                        'notes': decrypted_notes,
                        'created_at': contrib[5],
                        'synced': contrib[6]
                    })
                
                return decrypted_contributions
        except Exception as e:
            self.logger.error(f"Failed to get member contributions: {e}")
            return []
    
    def mark_contribution_synced(self, contribution_id):
        """Mark a contribution as synced with Bitnob API"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE contributions
                    SET synced_with_bitnob = 1
                    WHERE id = ?
                ''', (contribution_id,))
                conn.commit()
                
                self.logger.info(f"Marked contribution {contribution_id} as synced")
        except Exception as e:
            self.logger.error(f"Failed to mark contribution as synced: {e}")
    
    def record_payout(self, member_name, amount, phone_number, payout_type="mobile_money"):
        """Record a payout transaction"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payouts (member_name, amount, phone_number, payout_type)
                    VALUES (?, ?, ?, ?)
                ''', (member_name, amount, phone_number, payout_type))
                payout_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Recorded payout: {member_name} - {amount}")
                return payout_id
        except Exception as e:
            self.logger.error(f"Failed to record payout: {e}")
            return None
    
    def update_payout_status(self, payout_id, status):
        """Update payout status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE payouts
                    SET status = ?, processed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, payout_id))
                conn.commit()
                
                self.logger.info(f"Updated payout {payout_id} status to {status}")
        except Exception as e:
            self.logger.error(f"Failed to update payout status: {e}")
    
    def update_exchange_rates(self, rates):
        """Update exchange rates from Bitnob API"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for currency_pair, rate in rates.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO exchange_rates (currency_pair, rate)
                        VALUES (?, ?)
                    ''', (currency_pair, rate))
                
                conn.commit()
                self.logger.info("Exchange rates updated")
        except Exception as e:
            self.logger.error(f"Failed to update exchange rates: {e}")
    
    def update_user_balance(self, balance_data):
        """Update user balance from Bitnob API"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for currency, balance in balance_data.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO user_balance (currency, balance)
                        VALUES (?, ?)
                    ''', (currency, balance))
                
                conn.commit()
                self.logger.info("User balance updated")
        except Exception as e:
            self.logger.error(f"Failed to update user balance: {e}")
    
    def get_setting(self, key, default=None):
        """Get application setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
                result = cursor.fetchone()
                return result[0] if result else default
        except Exception as e:
            self.logger.error(f"Failed to get setting {key}: {e}")
            return default
    
    def set_setting(self, key, value):
        """Set application setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value)
                    VALUES (?, ?)
                ''', (key, value))
                conn.commit()
                
                self.logger.info(f"Setting updated: {key}")
        except Exception as e:
            self.logger.error(f"Failed to set setting {key}: {e}")
    
    def export_savings_report(self):
        """Export savings data for reporting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT member_name, amount, contribution_type, 
                           created_at, bitcoin_address
                    FROM contributions
                    ORDER BY created_at DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Failed to export savings report: {e}")
            return []
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        try:
            if not backup_path:
                backup_path = f"backups/ajo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            Path(backup_path).parent.mkdir(exist_ok=True)
            
            with sqlite3.connect(self.db_path) as source_conn:
                with sqlite3.connect(backup_path) as backup_conn:
                    source_conn.backup(backup_conn)
            
            self.logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return None 