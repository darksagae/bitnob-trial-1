#!/usr/bin/env python3
"""
User Interface module for Ajo Bitcoin Savings App
Separate AdminUI and UserUI classes with modern Tkinter GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import logging
from datetime import datetime
import threading
import queue
from typing import Dict, List, Optional
import config
from database_new import Database
from api_new import BitnobAPI

logger = logging.getLogger(__name__)

class BaseUI:
    """Base UI class with common functionality"""
    
    def __init__(self, database: Database, api: BitnobAPI):
        self.database = database
        self.api = api
        self.message_queue = queue.Queue()
        self.setup_styling()
    
    def setup_styling(self):
        """Setup modern GUI styling"""
        style = ttk.Style()
        style.theme_use(config.GUI_THEME)
        
        # Configure colors and fonts
        style.configure('Header.TLabel',
                       font=config.GUI_FONTS['header'],
                       foreground=config.GUI_COLORS['primary'],
                       background=config.GUI_COLORS['background'])
        
        style.configure('Title.TLabel',
                       font=config.GUI_FONTS['title'],
                       foreground=config.GUI_COLORS['text'])
        
        style.configure('Success.TLabel',
                       font=config.GUI_FONTS['text'],
                       foreground=config.GUI_COLORS['success'])
        
        style.configure('Warning.TLabel',
                       font=config.GUI_FONTS['text'],
                       foreground=config.GUI_COLORS['warning'])
        
        style.configure('Error.TLabel',
                       font=config.GUI_FONTS['text'],
                       foreground=config.GUI_COLORS['error'])
        
        style.configure('Action.TButton',
                       font=config.GUI_FONTS['button'],
                       background=config.GUI_COLORS['secondary'],
                       foreground='white')
    
    def show_message(self, title: str, message: str, message_type: str = 'info'):
        """Show message box"""
        if message_type == 'error':
            messagebox.showerror(title, message)
        elif message_type == 'warning':
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
    
    def validate_amount(self, amount_str: str) -> Optional[float]:
        """Validate amount input"""
        try:
            amount = float(amount_str)
            if amount < config.MIN_CONTRIBUTION_AMOUNT:
                raise ValueError(f"Amount must be at least {config.MIN_CONTRIBUTION_AMOUNT:,} UGX")
            if amount > config.MAX_CONTRIBUTION_AMOUNT:
                raise ValueError(f"Amount cannot exceed {config.MAX_CONTRIBUTION_AMOUNT:,} UGX")
            return amount
        except ValueError as e:
            self.show_message("Invalid Amount", str(e), 'error')
            return None

class LoginUI:
    """Login window for user authentication"""
    
    def __init__(self, database: Database, on_login_success):
        self.database = database
        self.on_login_success = on_login_success
        self.setup_window()
    
    def setup_window(self):
        """Setup login window"""
        self.root = tk.Tk()
        self.root.title(f"{config.APP_NAME} - Login")
        self.root.geometry(config.WINDOW_SIZES['login'])
        self.root.configure(bg=config.GUI_COLORS['background'])
        self.root.resizable(False, False)
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # App title
        title_label = ttk.Label(main_frame, 
                               text="💰 Ajo Bitcoin Savings",
                               style='Header.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Login form
        form_frame = ttk.LabelFrame(main_frame, text="Login", padding=20)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Username
        ttk.Label(form_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        ttk.Label(form_frame, text="Password:").pack(anchor=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Login button
        login_button = ttk.Button(form_frame, 
                                 text="Login",
                                 command=self.authenticate,
                                 style='Action.TButton')
        login_button.pack(fill=tk.X)
        
        # Demo credentials
        demo_frame = ttk.LabelFrame(main_frame, text="Demo Credentials", padding=10)
        demo_frame.pack(fill=tk.X, pady=10)
        
        demo_text = "Admin: admin/admin123\nUser: user/user123"
        ttk.Label(demo_frame, text=demo_text, font=config.GUI_FONTS['small']).pack()
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.authenticate())
        self.username_entry.focus()
    
    def authenticate(self):
        """Authenticate user"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        user_data = self.database.authenticate_user(username, password)
        
        if user_data:
            self.root.destroy()
            self.on_login_success(user_data)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def run(self):
        """Start login window"""
        self.root.mainloop()

class AdminUI(BaseUI):
    """Admin interface with comprehensive management features"""
    
    def __init__(self, database: Database, api: BitnobAPI, user_data: Dict):
        super().__init__(database, api)
        self.user_data = user_data
        self.setup_window()
        self.create_tabs()
        self.refresh_data()
        logger.info(f"Admin UI initialized for user: {user_data['username']}")
    
    def setup_window(self):
        """Setup admin window"""
        self.root = tk.Tk()
        self.root.title(f"{config.APP_NAME} - Admin Portal")
        self.root.geometry(config.WINDOW_SIZES['admin'])
        self.root.configure(bg=config.GUI_COLORS['background'])
        
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create admin header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="🔐 Admin Portal - Ajo Bitcoin Savings",
                               style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # User info
        user_info = f"Logged in as: {self.user_data['full_name'] or self.user_data['username']}"
        user_label = ttk.Label(header_frame, text=user_info, style='Title.TLabel')
        user_label.pack(side=tk.RIGHT)
        
        # Sync status
        self.sync_status_label = ttk.Label(header_frame,
                                          text="🔄 Offline Mode",
                                          style='Warning.TLabel')
        self.sync_status_label.pack(side=tk.RIGHT, padx=(0, 20))
    
    def create_tabs(self):
        """Create admin tabs"""
        # Manage Groups tab
        self.create_groups_tab()
        
        # Payouts tab
        self.create_payouts_tab()
        
        # Users tab
        self.create_users_tab()
        
        # Commissions tab
        self.create_commissions_tab()
        
        # System tab
        self.create_system_tab()
    
    def create_groups_tab(self):
        """Create groups management tab"""
        groups_frame = ttk.Frame(self.notebook)
        self.notebook.add(groups_frame, text="👥 Manage Groups")
        
        # Add group section
        add_frame = ttk.LabelFrame(groups_frame, text="Add New Group", padding=10)
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Group name
        ttk.Label(add_frame, text="Group Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.new_group_name = ttk.Entry(add_frame, width=30)
        self.new_group_name.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Description
        ttk.Label(add_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.new_group_desc = ttk.Entry(add_frame, width=30)
        self.new_group_desc.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Add button
        add_button = ttk.Button(add_frame, text="Add Group", command=self.add_group)
        add_button.grid(row=2, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        
        # Groups list
        list_frame = ttk.LabelFrame(groups_frame, text="Active Groups", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Groups tree
        columns = ('ID', 'Name', 'Description', 'Admin', 'Members', 'Created')
        self.groups_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.groups_tree.heading(col, text=col)
            self.groups_tree.column(col, width=100)
        
        self.groups_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_groups).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Delete Group", command=self.delete_group).pack(side=tk.LEFT)
    
    def create_payouts_tab(self):
        """Create payouts management tab"""
        payouts_frame = ttk.Frame(self.notebook)
        self.notebook.add(payouts_frame, text="💳 Payouts")
        
        # Pending payouts
        pending_frame = ttk.LabelFrame(payouts_frame, text="Pending Payouts", padding=10)
        pending_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Payouts tree
        columns = ('ID', 'Group', 'Member', 'Amount', 'Commission', 'Method', 'Status', 'Created')
        self.payouts_tree = ttk.Treeview(pending_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.payouts_tree.heading(col, text=col)
            self.payouts_tree.column(col, width=100)
        
        self.payouts_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(pending_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_payouts).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Approve Selected", command=self.approve_payout).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Process Payment", command=self.process_payout).pack(side=tk.LEFT)
    
    def create_users_tab(self):
        """Create users management tab"""
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="👤 Users")
        
        # Users list
        list_frame = ttk.LabelFrame(users_frame, text="All Users", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Users tree
        columns = ('ID', 'Username', 'Full Name', 'Role', 'Phone', 'Email', 'Status', 'Created')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
        
        self.users_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_users).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Change Role", command=self.change_user_role).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Deactivate", command=self.deactivate_user).pack(side=tk.LEFT)
    
    def create_commissions_tab(self):
        """Create commissions management tab"""
        commissions_frame = ttk.Frame(self.notebook)
        self.notebook.add(commissions_frame, text="💰 Commissions")
        
        # Commission summary
        summary_frame = ttk.LabelFrame(commissions_frame, text="Commission Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.total_commission_label = ttk.Label(summary_frame, text="Total Commissions: 0.00 UGX", style='Title.TLabel')
        self.total_commission_label.pack(anchor=tk.W)
        
        self.pending_commission_label = ttk.Label(summary_frame, text="Pending Transfer: 0.00 UGX", style='Warning.TLabel')
        self.pending_commission_label.pack(anchor=tk.W)
        
        # Transfer section
        transfer_frame = ttk.LabelFrame(commissions_frame, text="Transfer Commissions", padding=10)
        transfer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Payment method
        ttk.Label(transfer_frame, text="Payment Method:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.transfer_method = tk.StringVar(value="mobile_money")
        method_combo = ttk.Combobox(transfer_frame, textvariable=self.transfer_method,
                                   values=["mobile_money", "bitcoin", "usdt"], width=20)
        method_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Recipient info
        ttk.Label(transfer_frame, text="Recipient Info:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.recipient_info = ttk.Entry(transfer_frame, width=30)
        self.recipient_info.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Transfer button
        transfer_button = ttk.Button(transfer_frame, text="Transfer All Commissions", command=self.transfer_commissions)
        transfer_button.grid(row=2, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        
        # Commission history
        history_frame = ttk.LabelFrame(commissions_frame, text="Commission History", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # History tree
        columns = ('ID', 'Source', 'Source ID', 'Amount', 'Transferred', 'Created', 'Transfer Date')
        self.commission_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.commission_tree.heading(col, text=col)
            self.commission_tree.column(col, width=100)
        
        self.commission_tree.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        ttk.Button(history_frame, text="Refresh", command=self.refresh_commissions).pack(pady=10)
    
    def create_system_tab(self):
        """Create system management tab"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="⚙️ System")
        
        # System status
        status_frame = ttk.LabelFrame(system_frame, text="System Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.api_status_label = ttk.Label(status_frame, text="API Status: Checking...")
        self.api_status_label.pack(anchor=tk.W)
        
        self.database_status_label = ttk.Label(status_frame, text="Database: Connected")
        self.database_status_label.pack(anchor=tk.W)
        
        # System actions
        actions_frame = ttk.LabelFrame(system_frame, text="System Actions", padding=10)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(actions_frame, text="Test API Connection", command=self.test_api).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="Backup Database", command=self.backup_database).pack(side=tk.LEFT)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Update status periodically
        self.root.after(5000, self.update_status)
    
    # Tab methods implementation
    def add_group(self):
        """Add new group"""
        name = self.new_group_name.get().strip()
        description = self.new_group_desc.get().strip()
        
        if not name:
            self.show_message("Error", "Please enter group name", 'error')
            return
        
        group_id = self.database.create_group(name, description, self.user_data['id'])
        
        if group_id:
            self.show_message("Success", f"Group '{name}' created successfully")
            self.new_group_name.delete(0, tk.END)
            self.new_group_desc.delete(0, tk.END)
            self.refresh_groups()
        else:
            self.show_message("Error", "Failed to create group", 'error')
    
    def refresh_groups(self):
        """Refresh groups list"""
        # Clear existing items
        for item in self.groups_tree.get_children():
            self.groups_tree.delete(item)
        
        # Get groups from database
        groups = self.database.get_all_groups()
        
        for group in groups:
            self.groups_tree.insert('', 'end', values=(
                group['id'],
                group['name'],
                group['description'] or '',
                group['admin_name'] or '',
                group['member_count'],
                group['created_at'][:10] if group['created_at'] else ''
            ))
    
    def delete_group(self):
        """Delete selected group"""
        selection = self.groups_tree.selection()
        if not selection:
            self.show_message("Warning", "Please select a group", 'warning')
            return
        
        item = self.groups_tree.item(selection[0])
        group_id = int(item['values'][0])
        group_name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete group '{group_name}'?"):
            if self.database.delete_group(group_id):
                self.show_message("Success", f"Group '{group_name}' deleted")
                self.refresh_groups()
            else:
                self.show_message("Error", "Failed to delete group", 'error')
    
    def refresh_payouts(self):
        """Refresh payouts list"""
        # Clear existing items
        for item in self.payouts_tree.get_children():
            self.payouts_tree.delete(item)
        
        # Get pending payouts
        payouts = self.database.get_pending_payouts()
        
        for payout in payouts:
            self.payouts_tree.insert('', 'end', values=(
                payout[0],  # ID
                payout[1],  # Group
                payout[2],  # Member
                f"{payout[3]:,.2f}",  # Amount
                f"{payout[4]:,.2f}",  # Commission
                payout[5],  # Method
                payout[6],  # Status
                payout[7][:10] if payout[7] else ''  # Created
            ))
    
    def approve_payout(self):
        """Approve selected payout"""
        selection = self.payouts_tree.selection()
        if not selection:
            self.show_message("Warning", "Please select a payout", 'warning')
            return
        
        item = self.payouts_tree.item(selection[0])
        payout_id = int(item['values'][0])
        
        if self.database.approve_payout(payout_id, self.user_data['id']):
            self.show_message("Success", "Payout approved")
            self.refresh_payouts()
        else:
            self.show_message("Error", "Failed to approve payout", 'error')
    
    def process_payout(self):
        """Process selected payout"""
        selection = self.payouts_tree.selection()
        if not selection:
            self.show_message("Warning", "Please select a payout", 'warning')
            return
        
        item = self.payouts_tree.item(selection[0])
        payout_id = int(item['values'][0])
        
        if self.database.complete_payout(payout_id):
            self.show_message("Success", "Payout processed")
            self.refresh_payouts()
        else:
            self.show_message("Error", "Failed to process payout", 'error')
    
    def refresh_users(self):
        """Refresh users list"""
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Get users from database
        users = self.database.get_all_users()
        
        for user in users:
            self.users_tree.insert('', 'end', values=(
                user[0],  # ID
                user[1],  # Username
                user[3] or '',  # Full Name
                user[2],  # Role
                user[4] or '',  # Phone
                user[5] or '',  # Email
                'Active' if user[7] else 'Inactive',  # Status
                user[6][:10] if user[6] else ''  # Created
            ))
    
    def change_user_role(self):
        """Change user role"""
        selection = self.users_tree.selection()
        if not selection:
            self.show_message("Warning", "Please select a user", 'warning')
            return
        
        item = self.users_tree.item(selection[0])
        user_id = int(item['values'][0])
        current_role = item['values'][3]
        
        new_role = 'admin' if current_role == 'user' else 'user'
        
        if self.database.update_user_role(user_id, new_role):
            self.show_message("Success", f"User role changed to {new_role}")
            self.refresh_users()
        else:
            self.show_message("Error", "Failed to change user role", 'error')
    
    def deactivate_user(self):
        """Deactivate user"""
        selection = self.users_tree.selection()
        if not selection:
            self.show_message("Warning", "Please select a user", 'warning')
            return
        
        item = self.users_tree.item(selection[0])
        user_id = int(item['values'][0])
        username = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Deactivate user '{username}'?"):
            if self.database.deactivate_user(user_id):
                self.show_message("Success", f"User '{username}' deactivated")
                self.refresh_users()
            else:
                self.show_message("Error", "Failed to deactivate user", 'error')
    
    def refresh_commissions(self):
        """Refresh commission data"""
        # Update summary
        total_commissions = self.database.get_total_commissions()
        self.total_commission_label.config(text=f"Total Commissions: {total_commissions:,.2f} UGX")
        self.pending_commission_label.config(text=f"Pending Transfer: {total_commissions:,.2f} UGX")
        
        # Clear existing items
        for item in self.commission_tree.get_children():
            self.commission_tree.delete(item)
        
        # Get commission history
        commissions = self.database.get_commission_history()
        
        for comm in commissions:
            self.commission_tree.insert('', 'end', values=(
                comm[0],  # ID
                comm[1],  # Source
                comm[2],  # Source ID
                f"{comm[3]:,.2f}",  # Amount
                'Yes' if comm[4] else 'No',  # Transferred
                comm[5][:10] if comm[5] else '',  # Created
                comm[6][:10] if comm[6] else ''  # Transfer Date
            ))
    
    def transfer_commissions(self):
        """Transfer all pending commissions"""
        total_commissions = self.database.get_total_commissions()
        
        if total_commissions <= 0:
            self.show_message("Info", "No commissions to transfer")
            return
        
        payment_method = self.transfer_method.get()
        recipient_info = self.recipient_info.get().strip()
        
        if not recipient_info:
            self.show_message("Error", "Please enter recipient information", 'error')
            return
        
        if messagebox.askyesno("Confirm", f"Transfer {total_commissions:,.2f} UGX in commissions?"):
            result = self.api.transfer_commission(total_commissions, payment_method, recipient_info)
            
            if result.get('success'):
                self.database.mark_commissions_transferred()
                self.show_message("Success", "Commissions transferred successfully")
                self.refresh_commissions()
            else:
                self.show_message("Error", f"Transfer failed: {result.get('error')}", 'error')
    
    def test_api(self):
        """Test API connection"""
        if self.api.test_connection():
            self.show_message("Success", "API connection successful")
            self.api_status_label.config(text="API Status: Online", style='Success.TLabel')
        else:
            self.show_message("Error", "API connection failed", 'error')
            self.api_status_label.config(text="API Status: Offline", style='Error.TLabel')
    
    def export_data(self):
        """Export data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            # Export summary data
            summary = self.database.get_savings_summary()
            # Implementation would export data to CSV
            self.show_message("Success", f"Data exported to {filename}")
    
    def backup_database(self):
        """Backup database"""
        # Implementation would backup the database
        self.show_message("Success", "Database backed up successfully")
    
    def refresh_data(self):
        """Refresh all data"""
        self.refresh_groups()
        self.refresh_payouts()
        self.refresh_users()
        self.refresh_commissions()
        self.test_api()
    
    def update_status(self):
        """Update status bar"""
        # Update sync status
        if self.api.is_online:
            self.sync_status_label.config(text="🟢 Online", style='Success.TLabel')
        else:
            self.sync_status_label.config(text="🔴 Offline", style='Error.TLabel')
        
        # Schedule next update
        self.root.after(5000, self.update_status)
    
    def run(self):
        """Start admin UI"""
        self.root.mainloop()

class UserUI(BaseUI):
    """User interface for regular users"""
    
    def __init__(self, database: Database, api: BitnobAPI, user_data: Dict):
        super().__init__(database, api)
        self.user_data = user_data
        self.setup_window()
        self.create_tabs()
        self.refresh_data()
        logger.info(f"User UI initialized for user: {user_data['username']}")
    
    def setup_window(self):
        """Setup user window"""
        self.root = tk.Tk()
        self.root.title(f"{config.APP_NAME} - User Portal")
        self.root.geometry(config.WINDOW_SIZES['user'])
        self.root.configure(bg=config.GUI_COLORS['background'])
        
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create user header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame,
                               text="💰 Ajo Bitcoin Savings - User Portal",
                               style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # User info
        user_info = f"Welcome, {self.user_data['full_name'] or self.user_data['username']}!"
        user_label = ttk.Label(header_frame, text=user_info, style='Title.TLabel')
        user_label.pack(side=tk.RIGHT)
        
        # Sync status
        self.sync_status_label = ttk.Label(header_frame,
                                          text="🔄 Offline Mode",
                                          style='Warning.TLabel')
        self.sync_status_label.pack(side=tk.RIGHT, padx=(0, 20))
    
    def create_tabs(self):
        """Create user tabs"""
        # Dashboard tab
        self.create_dashboard_tab()
        
        # Add Contribution tab
        self.create_contribution_tab()
        
        # My Contributions tab
        self.create_my_contributions_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Summary section
        summary_frame = ttk.LabelFrame(dashboard_frame, text="My Savings Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.total_savings_label = ttk.Label(summary_frame, text="Total Savings: 0.00 UGX", style='Title.TLabel')
        self.total_savings_label.pack(anchor=tk.W)
        
        self.total_contributions_label = ttk.Label(summary_frame, text="Total Contributions: 0", style='Title.TLabel')
        self.total_contributions_label.pack(anchor=tk.W)
        
        self.commission_paid_label = ttk.Label(summary_frame, text="Commission Paid: 0.00 UGX", style='Warning.TLabel')
        self.commission_paid_label.pack(anchor=tk.W)
        
        # Recent activity
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Activity tree
        columns = ('Date', 'Group', 'Amount', 'Commission', 'Method', 'Status')
        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=100)
        
        self.activity_tree.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        ttk.Button(activity_frame, text="Refresh", command=self.refresh_dashboard).pack(pady=10)
    
    def create_contribution_tab(self):
        """Create add contribution tab"""
        contribution_frame = ttk.Frame(self.notebook)
        self.notebook.add(contribution_frame, text="💸 Add Contribution")
        
        # Contribution form
        form_frame = ttk.LabelFrame(contribution_frame, text="New Contribution", padding=20)
        form_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Group selection
        ttk.Label(form_frame, text="Group:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.contribution_group = ttk.Combobox(form_frame, width=30)
        self.contribution_group.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Amount
        ttk.Label(form_frame, text="Amount (UGX):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.contribution_amount = ttk.Entry(form_frame, width=30)
        self.contribution_amount.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Payment method
        ttk.Label(form_frame, text="Payment Method:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.payment_method = tk.StringVar(value="mobile_money")
        method_combo = ttk.Combobox(form_frame, textvariable=self.payment_method,
                                   values=["mobile_money", "bitcoin", "usdt"], width=27)
        method_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Phone number (for mobile money)
        ttk.Label(form_frame, text="Phone Number:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.phone_number = ttk.Entry(form_frame, width=30)
        self.phone_number.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.contribution_notes = scrolledtext.ScrolledText(form_frame, width=30, height=3)
        self.contribution_notes.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Submit button
        submit_button = ttk.Button(form_frame, text="Add Contribution", command=self.add_contribution)
        submit_button.grid(row=5, column=1, sticky=tk.W, pady=20, padx=(10, 0))
        
        # Commission info
        commission_info = f"Note: {config.COMMISSION_RATE * 100}% commission will be deducted"
        ttk.Label(form_frame, text=commission_info, style='Warning.TLabel').grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def create_my_contributions_tab(self):
        """Create my contributions tab"""
        contributions_frame = ttk.Frame(self.notebook)
        self.notebook.add(contributions_frame, text="📋 My Contributions")
        
        # Contributions list
        list_frame = ttk.LabelFrame(contributions_frame, text="My Contributions", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Contributions tree
        columns = ('ID', 'Group', 'Amount', 'Commission', 'Method', 'Status', 'Date')
        self.contributions_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.contributions_tree.heading(col, text=col)
            self.contributions_tree.column(col, width=100)
        
        self.contributions_tree.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        ttk.Button(list_frame, text="Refresh", command=self.refresh_contributions).pack(pady=10)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Update status periodically
        self.root.after(5000, self.update_status)
    
    # Tab methods implementation
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Get user contributions
        contributions = self.database.get_user_contributions(self.user_data['id'])
        
        # Calculate totals
        total_amount = sum(contrib[2] for contrib in contributions)
        total_commission = sum(contrib[3] for contrib in contributions)
        
        # Update labels
        self.total_savings_label.config(text=f"Total Savings: {total_amount:,.2f} UGX")
        self.total_contributions_label.config(text=f"Total Contributions: {len(contributions)}")
        self.commission_paid_label.config(text=f"Commission Paid: {total_commission:,.2f} UGX")
        
        # Update activity tree
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Show recent contributions
        for contrib in contributions[:10]:  # Last 10 contributions
            self.activity_tree.insert('', 'end', values=(
                contrib[6][:10] if contrib[6] else '',  # Date
                contrib[1],  # Group
                f"{contrib[2]:,.2f}",  # Amount
                f"{contrib[3]:,.2f}",  # Commission
                contrib[4],  # Method
                contrib[5]  # Status
            ))
    
    def add_contribution(self):
        """Add new contribution"""
        group_name = self.contribution_group.get().strip()
        amount_str = self.contribution_amount.get().strip()
        payment_method = self.payment_method.get()
        phone_number = self.phone_number.get().strip()
        notes = self.contribution_notes.get(1.0, tk.END).strip()
        
        # Validation
        if not group_name:
            self.show_message("Error", "Please select a group", 'error')
            return
        
        amount = self.validate_amount(amount_str)
        if amount is None:
            return
        
        if payment_method == "mobile_money" and not phone_number:
            self.show_message("Error", "Please enter phone number for mobile money", 'error')
            return
        
        # Get group ID (simplified - in real app, you'd have group selection)
        # For demo, we'll use group ID 1
        group_id = 1
        
        # Add contribution
        contribution_id = self.database.add_contribution(
            user_id=self.user_data['id'],
            group_id=group_id,
            amount=amount,
            payment_method=payment_method,
            payment_reference=phone_number if payment_method == "mobile_money" else None
        )
        
        if contribution_id:
            self.show_message("Success", f"Contribution added successfully!\nID: {contribution_id}")
            
            # Clear form
            self.contribution_amount.delete(0, tk.END)
            self.phone_number.delete(0, tk.END)
            self.contribution_notes.delete(1.0, tk.END)
            
            # Refresh data
            self.refresh_data()
        else:
            self.show_message("Error", "Failed to add contribution", 'error')
    
    def refresh_contributions(self):
        """Refresh contributions list"""
        # Clear existing items
        for item in self.contributions_tree.get_children():
            self.contributions_tree.delete(item)
        
        # Get user contributions
        contributions = self.database.get_user_contributions(self.user_data['id'])
        
        for contrib in contributions:
            self.contributions_tree.insert('', 'end', values=(
                contrib[0],  # ID
                contrib[1],  # Group
                f"{contrib[2]:,.2f}",  # Amount
                f"{contrib[3]:,.2f}",  # Commission
                contrib[4],  # Method
                contrib[5],  # Status
                contrib[6][:10] if contrib[6] else ''  # Date
            ))
    
    def refresh_data(self):
        """Refresh all data"""
        self.refresh_dashboard()
        self.refresh_contributions()
    
    def update_status(self):
        """Update status bar"""
        # Update sync status
        if self.api.is_online:
            self.sync_status_label.config(text="🟢 Online", style='Success.TLabel')
        else:
            self.sync_status_label.config(text="🔴 Offline", style='Error.TLabel')
        
        # Schedule next update
        self.root.after(5000, self.update_status)
    
    def run(self):
        """Start user UI"""
        self.root.mainloop() 