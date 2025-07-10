#!/usr/bin/env python3
"""
Utility functions for Ajo Bitcoin Savings App
Helper functions for queue management, validation, and common operations
"""

import queue
import threading
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import config

logger = logging.getLogger(__name__)

class SyncQueue:
    """Thread-safe queue for managing API sync operations"""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.sync_thread = None
        self.is_running = False
        self.sync_interval = config.SYNC_INTERVAL
        
    def start_sync_thread(self, api_client):
        """Start the background sync thread"""
        if not self.is_running:
            self.is_running = True
            self.sync_thread = threading.Thread(target=self._sync_worker, args=(api_client,), daemon=True)
            self.sync_thread.start()
            logger.info("Sync thread started")
    
    def stop_sync_thread(self):
        """Stop the background sync thread"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
            logger.info("Sync thread stopped")
    
    def _sync_worker(self, api_client):
        """Background worker for processing sync queue"""
        while self.is_running:
            try:
                # Process all items in queue
                while not self.queue.empty():
                    sync_item = self.queue.get_nowait()
                    self._process_sync_item(sync_item, api_client)
                    self.queue.task_done()
                
                # Wait before next sync cycle
                threading.Event().wait(self.sync_interval)
                
            except Exception as e:
                logger.error(f"Sync worker error: {e}")
                threading.Event().wait(10)  # Wait 10 seconds on error
    
    def _process_sync_item(self, sync_item: Dict, api_client):
        """Process a single sync item"""
        try:
            item_type = sync_item.get('type')
            data = sync_item.get('data')
            
            if item_type == 'contribution':
                success = api_client.sync_contribution(data)
            elif item_type == 'payout':
                success = api_client.sync_payout(data)
            elif item_type == 'commission':
                success = api_client.sync_commission(data)
            else:
                logger.warning(f"Unknown sync item type: {item_type}")
                return
            
            if success:
                logger.info(f"Successfully synced {item_type}: {data.get('id')}")
            else:
                logger.error(f"Failed to sync {item_type}: {data.get('id')}")
                
        except Exception as e:
            logger.error(f"Error processing sync item: {e}")
    
    def add_sync_item(self, item_type: str, data: Dict):
        """Add an item to the sync queue"""
        sync_item = {
            'type': item_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.queue.put(sync_item)
        logger.info(f"Added {item_type} to sync queue")

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_amount(amount_str: str) -> Optional[float]:
        """Validate and convert amount string to float"""
        try:
            amount = float(amount_str)
            if amount < config.MIN_CONTRIBUTION_AMOUNT:
                raise ValueError(f"Amount must be at least {config.MIN_CONTRIBUTION_AMOUNT:,} UGX")
            if amount > config.MAX_CONTRIBUTION_AMOUNT:
                raise ValueError(f"Amount cannot exceed {config.MAX_CONTRIBUTION_AMOUNT:,} UGX")
            return amount
        except ValueError as e:
            logger.warning(f"Invalid amount: {amount_str} - {e}")
            return None
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate Ugandan phone number format"""
        # Remove spaces and special characters
        phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check for Ugandan phone number patterns
        patterns = [
            r'^\+256[0-9]{9}$',  # +256XXXXXXXXX
            r'^256[0-9]{9}$',    # 256XXXXXXXXX
            r'^0[0-9]{9}$',      # 0XXXXXXXXX
            r'^[0-9]{9}$'        # XXXXXXXXX
        ]
        
        for pattern in patterns:
            if re.match(pattern, phone_clean):
                return True
        
        return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if len(username) < 3 or len(username) > 20:
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        if len(password) < config.PASSWORD_MIN_LENGTH:
            return False
        return True

class DataExporter:
    """Data export utilities"""
    
    @staticmethod
    def export_to_csv(data: List[Dict], filename: str, headers: List[str]) -> bool:
        """Export data to CSV file"""
        try:
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                for row in data:
                    writer.writerow([row.get(header.lower().replace(' ', '_'), '') for header in headers])
            logger.info(f"Data exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False
    
    @staticmethod
    def export_to_json(data: List[Dict], filename: str) -> bool:
        """Export data to JSON file"""
        try:
            import json
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, default=str)
            logger.info(f"Data exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False

class DateUtils:
    """Date and time utilities"""
    
    @staticmethod
    def format_date(date_obj: datetime) -> str:
        """Format date for display"""
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency"""
        return f"{amount:,.2f} UGX"
    
    @staticmethod
    def get_date_range(days: int) -> tuple:
        """Get date range for the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    @staticmethod
    def is_recent_date(date_obj: datetime, hours: int = 24) -> bool:
        """Check if date is within recent hours"""
        return datetime.now() - date_obj < timedelta(hours=hours)

class SecurityUtils:
    """Security utilities"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for storage"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a random session token"""
        import secrets
        return secrets.token_hex(32)
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = '*') -> str:
        """Mask sensitive data for display"""
        if len(data) <= 4:
            return mask_char * len(data)
        return data[:2] + mask_char * (len(data) - 4) + data[-2:]

class ErrorHandler:
    """Error handling utilities"""
    
    @staticmethod
    def handle_database_error(error: Exception, operation: str) -> str:
        """Handle database errors and return user-friendly message"""
        logger.error(f"Database error during {operation}: {error}")
        
        if "UNIQUE constraint failed" in str(error):
            return "This record already exists."
        elif "FOREIGN KEY constraint failed" in str(error):
            return "Referenced record not found."
        elif "NOT NULL constraint failed" in str(error):
            return "Required field is missing."
        else:
            return "Database operation failed. Please try again."
    
    @staticmethod
    def handle_api_error(error: Exception, operation: str) -> str:
        """Handle API errors and return user-friendly message"""
        logger.error(f"API error during {operation}: {error}")
        
        if "Connection" in str(error):
            return "Network connection failed. Working in offline mode."
        elif "Timeout" in str(error):
            return "Request timed out. Please try again."
        elif "401" in str(error):
            return "Authentication failed. Please check API credentials."
        elif "403" in str(error):
            return "Access denied. Please check permissions."
        else:
            return "API operation failed. Working in offline mode."

class NotificationManager:
    """Notification management utilities"""
    
    def __init__(self):
        self.notifications = []
    
    def add_notification(self, message: str, level: str = "info"):
        """Add a notification"""
        notification = {
            'message': message,
            'level': level,
            'timestamp': datetime.now()
        }
        self.notifications.append(notification)
        logger.info(f"Notification: {message}")
    
    def get_notifications(self, limit: int = 10) -> List[Dict]:
        """Get recent notifications"""
        return self.notifications[-limit:]
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications.clear()

# Global instances
sync_queue = SyncQueue()
notification_manager = NotificationManager() 