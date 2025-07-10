#!/usr/bin/env python3
"""
Database module for Ajo Bitcoin Savings App
SQLite database with comprehensive tables for users, groups, contributions, payouts, and commissions
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import config

logger = logging.getLogger(__name__)

class Database:
    """SQLite database manager for Ajo savings app"""
    
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self._init_database()
        logger.info(f"Database initialized: {db_path}")
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table for authentication and roles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT CHECK(role IN ('admin', 'user')) NOT NULL DEFAULT 'user',
                    full_name TEXT,
                    phone_number TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    login_attempts INTEGER DEFAULT 0
                )
            ''')
            
            # Groups table for savings groups
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    admin_user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (admin_user_id) REFERENCES users (id)
                )
            ''')
            
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
            ''')
            
            # Contributions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    group_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    commission REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    payment_reference TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    synced INTEGER DEFAULT 0,
                    sync_timestamp TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (group_id) REFERENCES groups (id)
                )
            ''')
            
            # Payouts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    commission REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    payment_reference TEXT,
                    status TEXT DEFAULT 'pending',
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    synced INTEGER DEFAULT 0,
                    sync_timestamp TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (approved_by) REFERENCES users (id)
                )
            ''')
            
            # Commissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL, -- 'contribution' or 'payout'
                    source_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    transferred INTEGER DEFAULT 0,
                    transfer_timestamp TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_contributions_user ON contributions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_contributions_group ON contributions(group_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_payouts_user ON payouts(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_payouts_group ON payouts(group_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_commissions_source ON commissions(source, source_id)')
            
            conn.commit()
            logger.info("Database tables created successfully")
    
    # User Management Methods
    def create_user(self, username: str, password: str, role: str = 'user', 
                   full_name: str = None, phone_number: str = None, email: str = None) -> Optional[int]:
        """Create a new user"""
        try:
            from utils import SecurityUtils
            password_hash = SecurityUtils.hash_password(password)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, full_name, phone_number, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, password_hash, role, full_name, phone_number, email))
                user_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Created user: {username} with role: {role}")
                return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"User already exists: {username}")
            return None
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        try:
            from utils import SecurityUtils
            password_hash = SecurityUtils.hash_password(password)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, role, full_name, phone_number, email, is_active
                    FROM users
                    WHERE username = ? AND password_hash = ? AND is_active = 1
                ''', (username, password_hash))
                
                user_data = cursor.fetchone()
                
                if user_data:
                    # Update last login
                    cursor.execute('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP, login_attempts = 0
                        WHERE id = ?
                    ''', (user_data[0],))
                    conn.commit()
                    
                    user_dict = {
                        'id': user_data[0],
                        'username': user_data[1],
                        'role': user_data[2],
                        'full_name': user_data[3],
                        'phone_number': user_data[4],
                        'email': user_data[5],
                        'is_active': bool(user_data[6])
                    }
                    logger.info(f"User authenticated: {username}")
                    return user_dict
                else:
                    # Increment login attempts
                    cursor.execute('''
                        UPDATE users SET login_attempts = login_attempts + 1
                        WHERE username = ?
                    ''', (username,))
                    conn.commit()
                    
                    logger.warning(f"Authentication failed for user: {username}")
                    return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_user_role(self, user_id: int) -> Optional[str]:
        """Get user role by user ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT role FROM users WHERE id = ? AND is_active = 1', (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return None
    
    def get_all_users(self) -> List[Tuple]:
        """Get all users"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, role, full_name, phone_number, email, created_at, is_active
                    FROM users ORDER BY created_at DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    def update_user_role(self, user_id: int, role: str) -> bool:
        """Update user role"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
                conn.commit()
                logger.info(f"Updated user {user_id} role to {role}")
                return True
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
                conn.commit()
                logger.info(f"Deactivated user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return False
    
    # Group Management Methods
    def create_group(self, name: str, description: str = None, admin_user_id: int = None) -> Optional[int]:
        """Create a new savings group"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO groups (name, description, admin_user_id)
                    VALUES (?, ?, ?)
                ''', (name, description, admin_user_id))
                group_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Created group: {name}")
                return group_id
        except sqlite3.IntegrityError:
            logger.warning(f"Group already exists: {name}")
            return None
        except Exception as e:
            logger.error(f"Failed to create group: {e}")
            return None
    
    def get_all_groups(self) -> List[Dict]:
        """Get all active groups with member count"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT g.id, g.name, g.description, g.created_at, 
                           u.full_name as admin_name, COUNT(gm.user_id) as member_count
                    FROM groups g
                    LEFT JOIN users u ON g.admin_user_id = u.id
                    LEFT JOIN group_members gm ON g.id = gm.group_id AND gm.is_active = 1
                    WHERE g.is_active = 1
                    GROUP BY g.id
                    ORDER BY g.created_at DESC
                ''')
                
                groups = []
                for row in cursor.fetchall():
                    groups.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'created_at': row[3],
                        'admin_name': row[4],
                        'member_count': row[5]
                    })
                
                return groups
        except Exception as e:
            logger.error(f"Error getting groups: {e}")
            return []
    
    def delete_group(self, group_id: int) -> bool:
        """Delete a group (soft delete)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE groups SET is_active = 0 WHERE id = ?', (group_id,))
                conn.commit()
                logger.info(f"Deleted group {group_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting group: {e}")
            return False
    
    def add_user_to_group(self, user_id: int, group_id: int) -> bool:
        """Add user to group"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO group_members (group_id, user_id)
                    VALUES (?, ?)
                ''', (group_id, user_id))
                conn.commit()
                logger.info(f"Added user {user_id} to group {group_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding user to group: {e}")
            return False
    
    def remove_user_from_group(self, user_id: int, group_id: int) -> bool:
        """Remove user from group"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE group_members SET is_active = 0
                    WHERE group_id = ? AND user_id = ?
                ''', (group_id, user_id))
                conn.commit()
                logger.info(f"Removed user {user_id} from group {group_id}")
                return True
        except Exception as e:
            logger.error(f"Error removing user from group: {e}")
            return False
    
    # Contribution Methods
    def add_contribution(self, user_id: int, group_id: int, amount: float, 
                        payment_method: str, payment_reference: str = None) -> Optional[int]:
        """Add a new contribution with commission calculation"""
        try:
            commission = round(amount * config.COMMISSION_RATE, 2)
            net_amount = amount - commission
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO contributions (user_id, group_id, amount, commission, 
                                             payment_method, payment_reference)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, group_id, net_amount, commission, payment_method, payment_reference))
                contribution_id = cursor.lastrowid
                
                # Add commission record
                cursor.execute('''
                    INSERT INTO commissions (source, source_id, amount)
                    VALUES (?, ?, ?)
                ''', ('contribution', contribution_id, commission))
                
                conn.commit()
                logger.info(f"Added contribution: {contribution_id} - Amount: {amount}, Commission: {commission}")
                return contribution_id
        except Exception as e:
            logger.error(f"Failed to add contribution: {e}")
            return None
    
    def get_user_contributions(self, user_id: int) -> List[Tuple]:
        """Get all contributions for a user"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.id, g.name, c.amount, c.commission, c.payment_method, 
                           c.status, c.created_at
                    FROM contributions c 
                    JOIN groups g ON c.group_id = g.id
                    WHERE c.user_id = ?
                    ORDER BY c.created_at DESC
                ''', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting user contributions: {e}")
            return []
    
    def get_group_contributions(self, group_id: int) -> List[Tuple]:
        """Get all contributions for a group"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.id, u.full_name, c.amount, c.commission, c.payment_method,
                           c.status, c.created_at
                    FROM contributions c 
                    JOIN users u ON c.user_id = u.id
                    WHERE c.group_id = ?
                    ORDER BY c.created_at DESC
                ''', (group_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting group contributions: {e}")
            return []
    
    # Payout Methods
    def add_payout(self, group_id: int, user_id: int, amount: float,
                  payment_method: str, payment_reference: str = None) -> Optional[int]:
        """Add a new payout with commission calculation"""
        try:
            commission = round(amount * config.COMMISSION_RATE, 2)
            net_amount = amount - commission
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payouts (group_id, user_id, amount, commission,
                                       payment_method, payment_reference)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (group_id, user_id, net_amount, commission, payment_method, payment_reference))
                payout_id = cursor.lastrowid
                
                # Add commission record
                cursor.execute('''
                    INSERT INTO commissions (source, source_id, amount)
                    VALUES (?, ?, ?)
                ''', ('payout', payout_id, commission))
                
                conn.commit()
                logger.info(f"Added payout: {payout_id} - Amount: {amount}, Commission: {commission}")
                return payout_id
        except Exception as e:
            logger.error(f"Failed to add payout: {e}")
            return None
    
    def get_pending_payouts(self) -> List[Tuple]:
        """Get all pending payouts"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.id, g.name, u.full_name, p.amount, p.commission,
                           p.payment_method, p.status, p.created_at
                    FROM payouts p
                    JOIN groups g ON p.group_id = g.id
                    JOIN users u ON p.user_id = u.id
                    WHERE p.status = 'pending'
                    ORDER BY p.created_at ASC
                ''')
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting pending payouts: {e}")
            return []
    
    def approve_payout(self, payout_id: int, approved_by: int) -> bool:
        """Approve a payout"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE payouts SET status = 'approved', approved_by = ?, approved_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (approved_by, payout_id))
                conn.commit()
                logger.info(f"Approved payout: {payout_id}")
                return True
        except Exception as e:
            logger.error(f"Error approving payout: {e}")
            return False
    
    def complete_payout(self, payout_id: int) -> bool:
        """Mark payout as completed"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE payouts SET status = 'completed', synced = 1, sync_timestamp = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (payout_id,))
                conn.commit()
                logger.info(f"Completed payout: {payout_id}")
                return True
        except Exception as e:
            logger.error(f"Error completing payout: {e}")
            return False
    
    # Commission Methods
    def get_total_commissions(self) -> float:
        """Get total untransferred commissions"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(amount) FROM commissions WHERE transferred = 0')
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0.0
        except Exception as e:
            logger.error(f"Error getting total commissions: {e}")
            return 0.0
    
    def get_commission_history(self) -> List[Tuple]:
        """Get commission history"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, source, source_id, amount, transferred, created_at, transfer_timestamp
                    FROM commissions
                    ORDER BY created_at DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting commission history: {e}")
            return []
    
    def mark_commissions_transferred(self) -> bool:
        """Mark all pending commissions as transferred"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE commissions 
                    SET transferred = 1, transfer_timestamp = CURRENT_TIMESTAMP
                    WHERE transferred = 0
                ''')
                conn.commit()
                logger.info("Marked all commissions as transferred")
                return True
        except Exception as e:
            logger.error(f"Error marking commissions transferred: {e}")
            return False
    
    # Statistics Methods
    def get_savings_summary(self) -> Dict:
        """Get comprehensive savings summary"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total contributions
                cursor.execute('SELECT SUM(amount), COUNT(*) FROM contributions')
                contrib_result = cursor.fetchone()
                total_contributions = contrib_result[0] if contrib_result[0] else 0
                contrib_count = contrib_result[1] if contrib_result[1] else 0
                
                # Total payouts
                cursor.execute('SELECT SUM(amount), COUNT(*) FROM payouts WHERE status = "completed"')
                payout_result = cursor.fetchone()
                total_payouts = payout_result[0] if payout_result[0] else 0
                payout_count = payout_result[1] if payout_result[1] else 0
                
                # Total commissions
                cursor.execute('SELECT SUM(amount) FROM commissions')
                comm_result = cursor.fetchone()
                total_commissions = comm_result[0] if comm_result[0] else 0
                
                # Active users
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
                user_count = cursor.fetchone()[0]
                
                # Active groups
                cursor.execute('SELECT COUNT(*) FROM groups WHERE is_active = 1')
                group_count = cursor.fetchone()[0]
                
                return {
                    'total_contributions': total_contributions,
                    'contrib_count': contrib_count,
                    'total_payouts': total_payouts,
                    'payout_count': payout_count,
                    'total_commissions': total_commissions,
                    'user_count': user_count,
                    'group_count': group_count
                }
        except Exception as e:
            logger.error(f"Error getting savings summary: {e}")
            return {}
    
    # Settings Methods
    def get_setting(self, key: str, default: str = None) -> str:
        """Get application setting"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
                result = cursor.fetchone()
                return result[0] if result else default
        except Exception as e:
            logger.error(f"Error getting setting: {e}")
            return default
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set application setting"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error setting setting: {e}")
            return False 