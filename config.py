#!/usr/bin/env python3
"""
Configuration file for Ajo Bitcoin Savings App
Contains constants, API settings, and app configuration
"""

# App Configuration
APP_NAME = "Ajo Bitcoin Savings App"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Bitcoin and Mobile Money Group Savings for Uganda"

# Database Configuration
DATABASE_PATH = "ajo.db"
BACKUP_PATH = "backups/"

# Commission System
COMMISSION_RATE = 0.01  # 1% commission on transactions
COMMISSION_DESCRIPTION = "1% transaction fee"

# Bitnob API Configuration
BITNOB_ API_BASE_URL = "https://api.bitnob.co"
BITNOB_API_KEY = "YOUR_BITNOB_API_KEY_HERE"  # Replace with actual API key
BITNOB_WEBHOOK_URL = "https://your-domain.com/webhook"

# Mobile Money Providers (Uganda)
MOBILE_MONEY_PROVIDERS = {
    "mtn": "MTN Mobile Money",
    "airtel": "Airtel Money",
    "mpesa": "M-Pesa Uganda"
}

# Payment Methods
PAYMENT_METHODS = {
    "mobile_money": "Mobile Money",
    "bitcoin": "Bitcoin",
    "usdt": "USDT (TRC20)"
}

# GUI Configuration
GUI_THEME = "clam"
GUI_FONTS = {
    "header": ("Arial", 18, "bold"),
    "title": ("Arial", 14, "bold"),
    "button": ("Arial", 12),
    "text": ("Arial", 10),
    "small": ("Arial", 9)
}

# GUI Colors
GUI_COLORS = {
    "primary": "#1E3A8A",      # Dark blue for headers
    "secondary": "#2563EB",    # Blue for buttons
    "background": "#F3F4F6",   # Light gray background
    "surface": "#FFFFFF",      # White surface
    "text": "#1F2937",         # Dark gray text
    "text_light": "#6B7280",   # Light gray text
    "success": "#059669",      # Green for success
    "warning": "#D97706",      # Orange for warnings
    "error": "#DC2626",        # Red for errors
    "border": "#D1D5DB"        # Light gray border
}

# Window Sizes
WINDOW_SIZES = {
    "admin": "1200x800",
    "user": "1000x700",
    "login": "400x300"
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/app.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Sync Configuration
SYNC_INTERVAL = 300  # 5 minutes
SYNC_TIMEOUT = 30    # 30 seconds
MAX_RETRY_ATTEMPTS = 3

# Validation Rules
MIN_CONTRIBUTION_AMOUNT = 1000  # 1000 UGX minimum
MAX_CONTRIBUTION_AMOUNT = 10000000  # 10M UGX maximum
MIN_PAYOUT_AMOUNT = 1000  # 1000 UGX minimum
MAX_PAYOUT_AMOUNT = 10000000  # 10M UGX maximum

# User Roles
USER_ROLES = {
    "admin": "Administrator",
    "user": "Regular User"
}

# Transaction Status
TRANSACTION_STATUS = {
    "pending": "Pending",
    "approved": "Approved",
    "completed": "Completed",
    "failed": "Failed",
    "cancelled": "Cancelled"
}

# Sync Status
SYNC_STATUS = {
    "pending": "Pending Sync",
    "syncing": "Syncing...",
    "synced": "Synced",
    "failed": "Sync Failed"
}

# File Paths
ICON_PATH = "assets/ajo_logo.png"
BACKUP_DIR = "backups/"
EXPORT_DIR = "exports/"
TEMP_DIR = "temp/"

# Security Settings
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT = 3600  # 1 hour
MAX_LOGIN_ATTEMPTS = 3

# Development Settings
DEBUG_MODE = True
DEMO_MODE = True  # Use demo data for testing
API_MOCK_MODE = True  # Mock API calls for offline development 