#!/usr/bin/env python3
"""
User Interface module for Ajo Bitcoin Savings App
Tkinter-based GUI for offline savings management and contribution tracking
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import logging
from datetime import datetime
import threading
import queue

class AjoUI:
    """Main user interface for Ajo Bitcoin Savings App"""
    
    def __init__(self, app):
        """Initialize the user interface"""
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Ajo - Bitcoin Group Savings App")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Set icon and styling
        self.setup_styling()
        
        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize UI components
        self.create_header()
        self.create_notebook()
        self.create_status_bar()
        
        # Message queue for thread-safe UI updates
        self.message_queue = queue.Queue()
        self.root.after(100, self.check_message_queue)
        
        self.logger.info("User interface initialized")
    
    def setup_styling(self):
        """Configure application styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Header.TLabel', 
                       font=('Arial', 16, 'bold'), 
                       foreground='#2c3e50',
                       background='#ecf0f1')
        
        style.configure('Title.TLabel', 
                       font=('Arial', 12, 'bold'), 
                       foreground='#34495e')
        
        style.configure('Success.TLabel', 
                       font=('Arial', 10), 
                       foreground='#27ae60')
        
        style.configure('Warning.TLabel', 
                       font=('Arial', 10), 
                       foreground='#e67e22')
        
        style.configure('Error.TLabel', 
                       font=('Arial', 10), 
                       foreground='#e74c3c')
    
    def create_header(self):
        """Create application header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # App title
        title_label = ttk.Label(header_frame, 
                               text="💰 Ajo Bitcoin Group Savings", 
                               style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # Sync status
        self.sync_status_label = ttk.Label(header_frame, 
                                          text="🔄 Offline Mode", 
                                          style='Warning.TLabel')
        self.sync_status_label.pack(side=tk.RIGHT)
        
        # Manual sync button
        sync_button = ttk.Button(header_frame, 
                                text="Sync Now", 
                                command=self.manual_sync)
        sync_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_notebook(self):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_contributions_tab()
        self.create_members_tab()
        self.create_payouts_tab()
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard tab with savings overview"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Summary section
        summary_frame = ttk.LabelFrame(dashboard_frame, text="Savings Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Total savings
        self.total_savings_label = ttk.Label(summary_frame, 
                                            text="Total Savings: 0.00", 
                                            style='Title.TLabel')
        self.total_savings_label.pack(anchor=tk.W)
        
        # Member count
        self.member_count_label = ttk.Label(summary_frame, 
                                           text="Active Members: 0", 
                                           style='Title.TLabel')
        self.member_count_label.pack(anchor=tk.W)
        
        # Recent activity
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Activity list
        self.activity_tree = ttk.Treeview(activity_frame, columns=('Date', 'Member', 'Amount', 'Type'), 
                                         show='headings', height=10)
        self.activity_tree.heading('Date', text='Date')
        self.activity_tree.heading('Member', text='Member')
        self.activity_tree.heading('Amount', text='Amount')
        self.activity_tree.heading('Type', text='Type')
        
        self.activity_tree.column('Date', width=150)
        self.activity_tree.column('Member', width=150)
        self.activity_tree.column('Amount', width=100)
        self.activity_tree.column('Type', width=100)
        
        self.activity_tree.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        refresh_button = ttk.Button(dashboard_frame, 
                                   text="Refresh Dashboard", 
                                   command=self.refresh_dashboard)
        refresh_button.pack(pady=10)
    
    def create_contributions_tab(self):
        """Create contributions tab for adding new contributions"""
        contributions_frame = ttk.Frame(self.notebook)
        self.notebook.add(contributions_frame, text="💸 Add Contribution")
        
        # Contribution form
        form_frame = ttk.LabelFrame(contributions_frame, text="New Contribution", padding=20)
        form_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Member name
        ttk.Label(form_frame, text="Member Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.member_name_entry = ttk.Entry(form_frame, width=30)
        self.member_name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.amount_entry = ttk.Entry(form_frame, width=30)
        self.amount_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Contribution type
        ttk.Label(form_frame, text="Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.contribution_type = tk.StringVar(value="bitcoin")
        type_combo = ttk.Combobox(form_frame, textvariable=self.contribution_type, 
                                 values=["bitcoin", "usdt", "ugx"], width=27)
        type_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.notes_text = scrolledtext.ScrolledText(form_frame, width=30, height=3)
        self.notes_text.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Submit button
        submit_button = ttk.Button(form_frame, 
                                  text="Add Contribution", 
                                  command=self.add_contribution)
        submit_button.grid(row=4, column=1, sticky=tk.W, pady=20, padx=(10, 0))
        
        # Bitcoin address display
        self.bitcoin_address_label = ttk.Label(form_frame, 
                                              text="", 
                                              style='Success.TLabel')
        self.bitcoin_address_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
    
    def create_members_tab(self):
        """Create members management tab"""
        members_frame = ttk.Frame(self.notebook)
        self.notebook.add(members_frame, text="👥 Members")
        
        # Add member section
        add_member_frame = ttk.LabelFrame(members_frame, text="Add New Member", padding=10)
        add_member_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Member form
        ttk.Label(add_member_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.new_member_name = ttk.Entry(add_member_frame, width=30)
        self.new_member_name.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(add_member_frame, text="Phone:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.new_member_phone = ttk.Entry(add_member_frame, width=30)
        self.new_member_phone.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(add_member_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.new_member_email = ttk.Entry(add_member_frame, width=30)
        self.new_member_email.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        add_button = ttk.Button(add_member_frame, 
                               text="Add Member", 
                               command=self.add_member)
        add_button.grid(row=3, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        
        # Members list
        members_list_frame = ttk.LabelFrame(members_frame, text="Group Members", padding=10)
        members_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.members_tree = ttk.Treeview(members_list_frame, 
                                        columns=('Name', 'Phone', 'Email', 'Contributions'), 
                                        show='headings', height=15)
        self.members_tree.heading('Name', text='Name')
        self.members_tree.heading('Phone', text='Phone')
        self.members_tree.heading('Email', text='Email')
        self.members_tree.heading('Contributions', text='Total Contributions')
        
        self.members_tree.column('Name', width=150)
        self.members_tree.column('Phone', width=120)
        self.members_tree.column('Email', width=200)
        self.members_tree.column('Contributions', width=150)
        
        self.members_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_payouts_tab(self):
        """Create payouts tab for mobile money transactions"""
        payouts_frame = ttk.Frame(self.notebook)
        self.notebook.add(payouts_frame, text="💳 Payouts")
        
        # Payout form
        payout_form_frame = ttk.LabelFrame(payouts_frame, text="Process Payout", padding=20)
        payout_form_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Member selection
        ttk.Label(payout_form_frame, text="Member:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.payout_member = ttk.Entry(payout_form_frame, width=30)
        self.payout_member.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Amount
        ttk.Label(payout_form_frame, text="Amount (UGX):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.payout_amount = ttk.Entry(payout_form_frame, width=30)
        self.payout_amount.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Phone number
        ttk.Label(payout_form_frame, text="Phone Number:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.payout_phone = ttk.Entry(payout_form_frame, width=30)
        self.payout_phone.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Provider selection
        ttk.Label(payout_form_frame, text="Provider:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.payout_provider = tk.StringVar(value="mpesa")
        provider_combo = ttk.Combobox(payout_form_frame, textvariable=self.payout_provider, 
                                     values=["mpesa", "airtel", "mtn"], width=27)
        provider_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Process button
        process_button = ttk.Button(payout_form_frame, 
                                   text="Process Payout", 
                                   command=self.process_payout)
        process_button.grid(row=4, column=1, sticky=tk.W, pady=20, padx=(10, 0))
        
        # Payout history
        history_frame = ttk.LabelFrame(payouts_frame, text="Payout History", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.payouts_tree = ttk.Treeview(history_frame, 
                                        columns=('Date', 'Member', 'Amount', 'Phone', 'Status'), 
                                        show='headings', height=10)
        self.payouts_tree.heading('Date', text='Date')
        self.payouts_tree.heading('Member', text='Member')
        self.payouts_tree.heading('Amount', text='Amount')
        self.payouts_tree.heading('Phone', text='Phone')
        self.payouts_tree.heading('Status', text='Status')
        
        self.payouts_tree.column('Date', width=150)
        self.payouts_tree.column('Member', width=150)
        self.payouts_tree.column('Amount', width=100)
        self.payouts_tree.column('Phone', width=120)
        self.payouts_tree.column('Status', width=100)
        
        self.payouts_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_settings_tab(self):
        """Create settings tab for app configuration"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # API Settings
        api_frame = ttk.LabelFrame(settings_frame, text="Bitnob API Settings", padding=10)
        api_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_entry = ttk.Entry(api_frame, width=50, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Load current API key
        current_api_key = self.app.database.get_setting('bitnob_api_key', '')
        self.api_key_entry.insert(0, current_api_key)
        
        save_api_button = ttk.Button(api_frame, 
                                    text="Save API Key", 
                                    command=self.save_api_key)
        save_api_button.grid(row=1, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        
        # Export/Import
        data_frame = ttk.LabelFrame(settings_frame, text="Data Management", padding=10)
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        export_button = ttk.Button(data_frame, 
                                  text="Export Savings Report", 
                                  command=self.export_report)
        export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        backup_button = ttk.Button(data_frame, 
                                  text="Backup Database", 
                                  command=self.backup_database)
        backup_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status information
        status_frame = ttk.LabelFrame(settings_frame, text="System Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.wallet_status_label = ttk.Label(status_frame, text="Wallet: Initializing...")
        self.wallet_status_label.pack(anchor=tk.W)
        
        self.api_status_label = ttk.Label(status_frame, text="API: Checking...")
        self.api_status_label.pack(anchor=tk.W)
        
        self.database_status_label = ttk.Label(status_frame, text="Database: Connected")
        self.database_status_label.pack(anchor=tk.W)
        
        # Refresh status button
        refresh_status_button = ttk.Button(status_frame, 
                                          text="Refresh Status", 
                                          command=self.refresh_status)
        refresh_status_button.pack(pady=10)
    
    def create_status_bar(self):
        """Create status bar at bottom of window"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Update status periodically
        self.root.after(5000, self.update_status)
    
    def add_contribution(self):
        """Add a new contribution"""
        try:
            member_name = self.member_name_entry.get().strip()
            amount_str = self.amount_entry.get().strip()
            contribution_type = self.contribution_type.get()
            notes = self.notes_text.get(1.0, tk.END).strip()
            
            # Validation
            if not member_name:
                messagebox.showerror("Error", "Please enter member name")
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
            
            # Add contribution
            contribution_id = self.app.add_contribution(
                member_name=member_name,
                amount=amount,
                contribution_type=contribution_type,
                notes=notes if notes else None
            )
            
            if contribution_id:
                # Clear form
                self.member_name_entry.delete(0, tk.END)
                self.amount_entry.delete(0, tk.END)
                self.notes_text.delete(1.0, tk.END)
                
                # Show Bitcoin address if applicable
                if contribution_type == "bitcoin":
                    # Get the generated address from the last contribution
                    contributions = self.app.database.get_member_contributions(member_name)
                    if contributions:
                        address = contributions[0].get('bitcoin_address')
                        if address:
                            self.bitcoin_address_label.config(
                                text=f"Bitcoin Address: {address}",
                                style='Success.TLabel'
                            )
                
                messagebox.showinfo("Success", f"Contribution added successfully!\nID: {contribution_id}")
                self.refresh_dashboard()
            else:
                messagebox.showerror("Error", "Failed to add contribution")
                
        except Exception as e:
            self.logger.error(f"Error adding contribution: {e}")
            messagebox.showerror("Error", f"Failed to add contribution: {str(e)}")
    
    def add_member(self):
        """Add a new member"""
        try:
            name = self.new_member_name.get().strip()
            phone = self.new_member_phone.get().strip()
            email = self.new_member_email.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter member name")
                return
            
            member_id = self.app.database.add_member(name, phone, email)
            
            if member_id:
                # Clear form
                self.new_member_name.delete(0, tk.END)
                self.new_member_phone.delete(0, tk.END)
                self.new_member_email.delete(0, tk.END)
                
                messagebox.showinfo("Success", f"Member added successfully!\nID: {member_id}")
                self.refresh_members()
            else:
                messagebox.showerror("Error", "Failed to add member or member already exists")
                
        except Exception as e:
            self.logger.error(f"Error adding member: {e}")
            messagebox.showerror("Error", f"Failed to add member: {str(e)}")
    
    def process_payout(self):
        """Process mobile money payout"""
        try:
            member_name = self.payout_member.get().strip()
            amount_str = self.payout_amount.get().strip()
            phone_number = self.payout_phone.get().strip()
            
            # Validation
            if not member_name or not amount_str or not phone_number:
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
            
            # Process payout
            success, message = self.app.process_mobile_money_payout(
                member_name=member_name,
                amount=amount,
                phone_number=phone_number
            )
            
            if success:
                # Clear form
                self.payout_member.delete(0, tk.END)
                self.payout_amount.delete(0, tk.END)
                self.payout_phone.delete(0, tk.END)
                
                messagebox.showinfo("Success", f"Payout processed successfully!\n{message}")
            else:
                messagebox.showwarning("Warning", f"Payout status: {message}")
                
        except Exception as e:
            self.logger.error(f"Error processing payout: {e}")
            messagebox.showerror("Error", f"Failed to process payout: {str(e)}")
    
    def manual_sync(self):
        """Manually trigger sync with Bitnob"""
        try:
            self.sync_status_label.config(text="🔄 Syncing...", style='Warning.TLabel')
            self.status_label.config(text="Syncing with Bitnob...")
            
            # Run sync in background
            def sync_thread():
                try:
                    self.app.sync_with_bitnob()
                    self.message_queue.put(("sync_complete", "Sync completed successfully"))
                except Exception as e:
                    self.message_queue.put(("sync_error", f"Sync failed: {str(e)}"))
            
            threading.Thread(target=sync_thread, daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"Error during manual sync: {e}")
            messagebox.showerror("Error", f"Sync failed: {str(e)}")
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        try:
            summary = self.app.get_savings_summary()
            if summary:
                # Update total savings
                total_data = summary.get('total_contributions', [0, 0])
                total_amount = total_data[0] if total_data[0] else 0
                self.total_savings_label.config(text=f"Total Savings: {total_amount:.2f}")
                
                # Update member count
                member_data = summary.get('member_contributions', [])
                self.member_count_label.config(text=f"Active Members: {len(member_data)}")
                
                # Update activity list
                for item in self.activity_tree.get_children():
                    self.activity_tree.delete(item)
                
                recent_contributions = summary.get('recent_contributions', [])
                for contrib in recent_contributions:
                    self.activity_tree.insert('', 'end', values=(
                        contrib[3][:19],  # Date
                        contrib[0],       # Member
                        contrib[1],       # Amount
                        contrib[2]        # Type
                    ))
            
        except Exception as e:
            self.logger.error(f"Error refreshing dashboard: {e}")
    
    def refresh_members(self):
        """Refresh members list"""
        try:
            # Clear existing items
            for item in self.members_tree.get_children():
                self.members_tree.delete(item)
            
            # Get members from database (simplified for demo)
            # In a real implementation, this would query the database
            
        except Exception as e:
            self.logger.error(f"Error refreshing members: {e}")
    
    def save_api_key(self):
        """Save Bitnob API key"""
        try:
            api_key = self.api_key_entry.get().strip()
            if api_key:
                self.app.database.set_setting('bitnob_api_key', api_key)
                messagebox.showinfo("Success", "API key saved successfully")
            else:
                messagebox.showerror("Error", "Please enter API key")
                
        except Exception as e:
            self.logger.error(f"Error saving API key: {e}")
            messagebox.showerror("Error", f"Failed to save API key: {str(e)}")
    
    def export_report(self):
        """Export savings report"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                exported_file = self.app.export_savings_report(filename)
                if exported_file:
                    messagebox.showinfo("Success", f"Report exported to: {exported_file}")
                else:
                    messagebox.showerror("Error", "Failed to export report")
                    
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def backup_database(self):
        """Backup database"""
        try:
            backup_path = self.app.database.backup_database()
            if backup_path:
                messagebox.showinfo("Success", f"Database backed up to: {backup_path}")
            else:
                messagebox.showerror("Error", "Failed to backup database")
                
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            messagebox.showerror("Error", f"Failed to backup database: {str(e)}")
    
    def refresh_status(self):
        """Refresh system status"""
        try:
            # Update wallet status
            wallet_status = self.app.wallet.get_wallet_status()
            if wallet_status.get('wallet_exists'):
                self.wallet_status_label.config(text="Wallet: Active", style='Success.TLabel')
            else:
                self.wallet_status_label.config(text="Wallet: Demo Mode", style='Warning.TLabel')
            
            # Update API status
            api_status = self.app.api.get_api_status()
            if api_status.get('online'):
                self.api_status_label.config(text="API: Online", style='Success.TLabel')
            else:
                self.api_status_label.config(text="API: Offline", style='Warning.TLabel')
            
            # Update sync status
            if self.app.api.is_online():
                self.sync_status_label.config(text="🟢 Online", style='Success.TLabel')
            else:
                self.sync_status_label.config(text="🔴 Offline", style='Error.TLabel')
                
        except Exception as e:
            self.logger.error(f"Error refreshing status: {e}")
    
    def update_status(self):
        """Update status bar"""
        try:
            # Update sync status
            if self.app.api.is_online():
                self.sync_status_label.config(text="🟢 Online", style='Success.TLabel')
            else:
                self.sync_status_label.config(text="🔴 Offline", style='Error.TLabel')
            
            # Schedule next update
            self.root.after(5000, self.update_status)
            
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def check_message_queue(self):
        """Check for messages from background threads"""
        try:
            while True:
                try:
                    message_type, message = self.message_queue.get_nowait()
                    
                    if message_type == "sync_complete":
                        self.sync_status_label.config(text="🟢 Online", style='Success.TLabel')
                        self.status_label.config(text="Sync completed")
                        messagebox.showinfo("Sync Complete", message)
                    elif message_type == "sync_error":
                        self.sync_status_label.config(text="🔴 Offline", style='Error.TLabel')
                        self.status_label.config(text="Sync failed")
                        messagebox.showerror("Sync Error", message)
                        
                except queue.Empty:
                    break
            
            # Schedule next check
            self.root.after(100, self.check_message_queue)
            
        except Exception as e:
            self.logger.error(f"Error checking message queue: {e}")
    
    def run(self):
        """Start the user interface"""
        try:
            # Initial refresh
            self.refresh_dashboard()
            self.refresh_status()
            
            # Start the main loop
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Error running UI: {e}")
            raise 