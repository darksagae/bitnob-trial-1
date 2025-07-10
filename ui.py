#!/usr/bin/env python3
"""
User Interface module for Ajo Bitcoin Savings App
Tkinter-based GUI for offline savings management and contribution tracking
"""

import tkinter as tk # GUI framework
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog # GUI components 
import logging # Logging for error tracking, debugging and monitoring
from datetime import datetime # Date and time handling
import threading # Threading for background operations and parallel processing like syncing and background tasks without freezing the UI
import queue # Queue for thread-safe message passing between threads offline and online bridging
# Only import AdminPortal for admin UI

# =====================
# User Interface (UserUI)
# =====================
class UserUI:
    """User interface for regular users (no admin access)"""
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.root = tk.Tk()
        self.root.title("Ajo - Bitcoin Group Savings App (User)")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        self.setup_styling()
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.create_header()
        self.create_notebook()
        self.create_status_bar()
        self.message_queue = queue.Queue()
        self.root.after(100, self.check_message_queue)
        self.logger.info("User interface initialized")

    def setup_styling(self): # sets up the visual styling and appearance and icons, widgets, fonts, colors and layout. Self is the instance of the class on which the method is called 
        """Configure application styling"""
        style = ttk.Style() # Creates a style object for the GUI. Enhances the appearances 
        style.theme_use('clam') # Sets the theme for the GUI. clam is a theme for the GUI.
        
        # Configure colors
        style.configure('Header.TLabel', 
                       font=('Arial', 16, 'bold'), 
                       foreground='#2c3e50',
                       background='#ecf0f1') # Sets the background color for the header label. #ecf0f1 is a light grey color. Header label is the label for the header.
        
        style.configure('Title.TLabel', 
                       font=('Arial', 12, 'bold'), 
                       foreground='#34495e') # Sets the foreground color for the title label. Title label is the label for the title.
        
        style.configure('Success.TLabel', 
                       font=('Arial', 10), 
                       foreground='#27ae60') # Sets the foreground color for the success label. 
        
        style.configure('Warning.TLabel', 
                       font=('Arial', 10), 
                       foreground='#e67e22') # Sets the foreground color for the warning label.
        
        style.configure('Error.TLabel', 
                       font=('Arial', 10), 
                       foreground='#e74c3c') # Sets the foreground color for the error label.
    
    def create_header(self): # Creates the header section using ttk.Frame(). Self is the instance of the class on which the method is called.
        """Create application header"""
        header_frame = ttk.Frame(self.main_frame) # Creates a frame for the header section. ttk.Frame() is the container for the header section. Self.main_frame is the main frame of the application.
        header_frame.pack(fill=tk.X, pady=(0, 10)) # Packs the header frame into the main frame. fill=tk.X, to stretch the frame to fill the entire width of the main frame. pady=(0, 10), to add padding to 10 pixels to the top and bottom 
        
        # App title
        title_label = ttk.Label(header_frame, 
                               text="💰 Ajo Bitcoin Group Savings", 
                               style='Header.TLabel') # Sets the style for the title label. Header.TLabel is the style for the header label.
        title_label.pack(side=tk.LEFT) # Packs the title label to the left side of the header frame.
        
        # Sync status
        self.sync_status_label = ttk.Label(header_frame, 
                                          text="🔄 Offline Mode", 
                                          style='Warning.TLabel') # Sets the style for the sync status label. Warning.TLabel is the style for the warning label. Offline mode is the status of the sync status label 
        
        # Manual sync button
        sync_button = ttk.Button(header_frame, 
                                text="Sync Now", 
                                command=self.manual_sync) # Sets the command for the sync button. manual_sync is the function that will be called when the sync button is clicked. 
        sync_button.pack(side=tk.RIGHT, padx=(0, 10)) # Packs the sync button to the right side of the header frame. padx=(0, 10), to add padding to 10 pixels to the right 
    
    def create_notebook(self): # Creates the notebook section using ttk.Notebook(). Self is the instance of the class on which the method is called. notebook is used to create the tabs to separate the content and improve the user experience and ideal for offline and online sync 
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(self.main_frame) # Creates a notebook for the tabs. ttk.Notebook() is the container for the tabs. Self.main_frame is the main frame of the application.
        self.notebook.pack(fill=tk.BOTH, expand=True) # Packs the notebook into the main frame. fill=tk.BOTH, to stretch the notebook to fill the entire width and height of the main frame. expand=True, to allow the notebook to grow and fill the entire width and height of the main frame.
        
        # Create tabs
        self.create_dashboard_tab() # Creates the dashboard tab using ttk.Frame(). Self is the instance of the class on which the method is called. Dashboard tab is the main tab for the appliction 
        self.create_contributions_tab() # Creates the contributions tab using ttk.Frame(). Self is the instance of the class on which the method is called. Contributions tab is used to add new contributions and track the contributions of the members
        self.create_members_tab() # Creates the members tab. Enables the management of the members and their contributions
        self.create_payouts_tab() # Creates the payouts tab. Enables the management of the payouts and transactions 
        self.create_settings_tab() # Creates the settings tab. Configures the settings to improve usability and security.
        # self.create_admin_tab() # Creates the admin portal tab for comprehensive system management - REMOVED
    
    def create_dashboard_tab(self): # Defines the dashboard tab. For quick overview of the savings and transactions. Self is the instance of the class on which the method is called.
        """Create dashboard tab with savings overview"""
        dashboard_frame = ttk.Frame(self.notebook) # Creates a frame for the dashboard tab. ttk.Frame() is the container for the dashboard tab. Self.notebook is the notebook for the tabs. 
        self.notebook.add(dashboard_frame, text="📊 Dashboard") # Adds the dashboard tab to the notebook. text=
        
        # Summary section
        summary_frame = ttk.LabelFrame(dashboard_frame, text="Savings Summary", padding=10) # Creates a frame for the summary section. ttk.LabelFrame() is the container for the summary section. dashboard_frame is the frame for the dashboard tab. 
        summary_frame.pack(fill=tk.X, padx=10, pady=10) # Packs the summary frame into the dashboard frame. fill=tk.X, to stretch the frame to fill the entire width of the dashboard frame. padx=10, to add padding to 10 pixels to the left and right. pady=10, to add padding to 10 pixels to the top and bottom.
        
        # Total savings
        self.total_savings_label = ttk.Label(summary_frame, 
                                            text="Total Savings: 0.00", 
                                            style='Title.TLabel') # Sets the sytle for the total savings label. Title.TLabel is the style for the title label. 
        self.total_savings_label.pack(anchor=tk.W) # Packs the total savings label to the left side of the summary frame.
        
        # Member count
        self.member_count_label = ttk.Label(summary_frame, 
                                           text="Active Members: 0", 
                                           style='Title.TLabel') # Sets the style for the member count label. Title.TLabel is the style for the title label. 
        self.member_count_label.pack(anchor=tk.W) # Packs the member count label to the left side of the summary frame.
        
        # Recent activity
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity", padding=10) # Creates a frame for the recent activity section. ttk.LabelFrame() is the container for the recent activity section. dashboard_frame is the frame for the dashboard tab. 
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10) # Packs the recent activity frame into the dashboard frame. fill=tk.BOTH, to stretch the frame to fill the entire width and height of the dashboard frame. expand=True, to allow the frame to grow and fill the entire width and height of the dashboard frame. padx=10, to add padding to 10 pixels to the left and right. pady=10, to add padding to 10 pixels to the top and bottom.
        
        # Activity list
        self.activity_tree = ttk.Treeview(activity_frame, columns=('Date', 'Member', 'Amount', 'Type'), 
                                         show='headings', height=10) # Creates a treeview for the recent activity. ttk.Treeview() is the container for the recent activity. activity_frame is the frame for the recent activity section. 
        self.activity_tree.heading('Date', text='Date') # Sets the heading for the date column.
        self.activity_tree.heading('Member', text='Member') # Sets the heading for the member column.
        self.activity_tree.heading('Amount', text='Amount') # Sets the heading for the amount column.
        self.activity_tree.heading('Type', text='Type') # Sets the heading for the type column.
        
        self.activity_tree.column('Date', width=150) # Sets the width for the date column.
        self.activity_tree.column('Member', width=150) # Sets the width for the member column.
        self.activity_tree.column('Amount', width=100) # Sets the width for the amount column.
        self.activity_tree.column('Type', width=100) # Sets the width for the type column.
        
        self.activity_tree.pack(fill=tk.BOTH, expand=True) # Packs the recent activity tree into the recent activity frame. fill=tk.BOTH, to stretch the frame to fill the entire width and height of the recent activity frame. expand=True, to allow the frame to grow and fill the entire width and height of the recent activity frame.
        
        # Refresh button
        refresh_button = ttk.Button(dashboard_frame, # Creates a button for the refresh button. ttk.Button() is the container for the refresh button. dashboard_frame is the frame for the dashboard tab. 
                                   text="Refresh Dashboard", # Sets the text for the refresh button.
                                   command=self.refresh_dashboard) # Sets the command for the refresh button. refresh_dashboard is the function that will be called when the refresh button is clicked.
        refresh_button.pack(pady=10) # Packs the refresh button into the dashboard frame. pady=10, to add padding to 10 pixels to the top and bottom.
    
    def create_contributions_tab(self): # Defines the contributions tab. For adding new contributions. Self is the instance of the class on which the method is called.
        """Create contributions tab for adding new contributions"""
        contributions_frame = ttk.Frame(self.notebook) # Creates a frame for the contributions tab. ttk.Frame() is the container for the contributions tab. Self.notebook is the notebook for the tabs. 
        self.notebook.add(contributions_frame, text="💸 Add Contribution") # Adds the contributions tab to the notebook. text="💸 Add Contribution" is the text for the contributions tab.
        
        # Contribution form
        form_frame = ttk.LabelFrame(contributions_frame, text="New Contribution", padding=20) # Creates a frame for the contribution form. ttk.LabelFrame() is the container for the contribution form. contributions_frame is the frame for the contributions tab. 
        form_frame.pack(fill=tk.X, padx=20, pady=20) # Packs the contribution form into the contributions frame. fill=tk.X, to stretch the frame to fill the entire width of the contributions frame. padx=20, to add padding to 20 pixels to the left and right. pady=20, to add padding to 20 pixels to the top and bottom.
        
        # Member name
        ttk.Label(form_frame, text="Member Name:").grid(row=0, column=0, sticky=tk.W, pady=5) # Creates a label for the member name. ttk.Label() is the container for the member name. form_frame is the frame for the contribution form.
        self.member_name_entry = ttk.Entry(form_frame, width=30) # Creates an entry for the member name. ttk.Entry() is the container for the member name. form_frame is the frame for the contribution form.
        self.member_name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0)) # Packs the member name entry into the contribution form. row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0), to add padding to 10 pixels to the left and right.
        
        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky=tk.W, pady=5) # Creates a label for the amount. ttk.Label() is the container for the amount. form_frame is the frame for the contribution form.
        self.amount_entry = ttk.Entry(form_frame, width=30) # Creates an entry for the amount. ttk.Entry() is the container for the amount. form_frame is the frame for the contribution form.
        self.amount_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0)) # Packs the amount entry into the contribution form. row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0), to add padding to 10 pixels to the left and right.
        
        # Contribution type
        ttk.Label(form_frame, text="Type:").grid(row=2, column=0, sticky=tk.W, pady=5) # Creates a label for the contribution type. ttk.Label() is the container for the contribution type. form_frame is the frame for the contribution form.
        self.contribution_type = tk.StringVar(value="bitcoin")
        type_combo = ttk.Combobox(form_frame, textvariable=self.contribution_type, 
                                 values=["bitcoin", "usdt", "ugx"], width=27) # Creates a combobox for the contribution type. ttk.Combobox() is the container for the contribution type. form_frame is the frame for the contribution form.
        type_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0)) # Packs the contribution type combobox into the contribution form. row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0), to add padding to 10 pixels to the left and right.
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky=tk.W, pady=5) # Creates a label for the notes. ttk.Label() is the container for the notes. form_frame is the frame for the contribution form. Grid is used to position the label in the form frame.
        self.notes_text = scrolledtext.ScrolledText(form_frame, width=30, height=3) # Creates a scrolled text for the notes. scrolledtext.ScrolledText() is the container for the notes. form_frame is the frame for the contribution form.
        self.notes_text.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0)) # Packs the notes scrolled text into the contribution form. row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0), to add padding to 10 pixels to the left and right.
        
        # Submit button
        submit_button = ttk.Button(form_frame, 
                                  text="Add Contribution", 
                                  command=self.add_contribution) # Sets the command for the submit button. add_contribution is the function that will be called when the submit button is clicked.
        submit_button.grid(row=4, column=1, sticky=tk.W, pady=20, padx=(10, 0)) # Packs the submit button into the contribution form. row=4, column=1, sticky=tk.W, pady=20, padx=(10, 0), to add padding to 20 pixels to the top and bottom.
        
        # Bitcoin address display
        self.bitcoin_address_label = ttk.Label(form_frame, 
                                              text="", 
                                              style='Success.TLabel') # Sets the style for the bitcoin address label. Success.TLabel is the style for the success label.
        self.bitcoin_address_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5) # Packs the bitcoin address label into the contribution form. row=5, column=0, columnspan=2, sticky=tk.W, pady=5, to add padding to 5 pixels to the top and bottom.
    
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

# =====================
# Admin Interface (AdminUI)
# =====================
class AdminUI:
    """Admin interface for system administrators (full management)"""
    def __init__(self, app):
        from admin import AdminPortal  # Only import here
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.root = tk.Tk()
        self.root.title("Ajo - Bitcoin Group Savings App (Admin)")
        self.root.geometry("1100x750")
        self.root.configure(bg='#f0f0f0')
        self.setup_styling()
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.create_header()
        self.create_notebook()
        self.create_status_bar()
        self.message_queue = queue.Queue()
        self.root.after(100, self.check_message_queue)
        self.admin_portal = AdminPortal(app)
        self.admin_logged_in = False
        self.logger.info("Admin interface initialized")

    def setup_styling(self): # sets up the visual styling and appearance and icons, widgets, fonts, colors and layout. Self is the instance of the class on which the method is called 
        """Configure application styling"""
        style = ttk.Style() # Creates a style object for the GUI. Enhances the appearances 
        style.theme_use('clam') # Sets the theme for the GUI. clam is a theme for the GUI.
        
        # Configure colors
        style.configure('Header.TLabel', 
                       font=('Arial', 16, 'bold'), 
                       foreground='#2c3e50',
                       background='#ecf0f1') # Sets the background color for the header label. #ecf0f1 is a light grey color. Header label is the label for the header.
        
        style.configure('Title.TLabel', 
                       font=('Arial', 12, 'bold'), 
                       foreground='#34495e') # Sets the foreground color for the title label. Title label is the label for the title.
        
        style.configure('Success.TLabel', 
                       font=('Arial', 10), 
                       foreground='#27ae60') # Sets the foreground color for the success label. 
        
        style.configure('Warning.TLabel', 
                       font=('Arial', 10), 
                       foreground='#e67e22') # Sets the foreground color for the warning label.
        
        style.configure('Error.TLabel', 
                       font=('Arial', 10), 
                       foreground='#e74c3c') # Sets the foreground color for the error label.
    
    def create_header(self): # Creates the header section using ttk.Frame(). Self is the instance of the class on which the method is called.
        """Create application header"""
        header_frame = ttk.Frame(self.main_frame) # Creates a frame for the header section. ttk.Frame() is the container for the header section. Self.main_frame is the main frame of the application.
        header_frame.pack(fill=tk.X, pady=(0, 10)) # Packs the header frame into the main frame. fill=tk.X, to stretch the frame to fill the entire width of the main frame. pady=(0, 10), to add padding to 10 pixels to the top and bottom 
        
        # App title
        title_label = ttk.Label(header_frame, 
                               text="💰 Ajo Bitcoin Group Savings", 
                               style='Header.TLabel') # Sets the style for the title label. Header.TLabel is the style for the header label.
        title_label.pack(side=tk.LEFT) # Packs the title label to the left side of the header frame.
        
        # Sync status
        self.sync_status_label = ttk.Label(header_frame, 
                                          text="🔄 Offline Mode", 
                                          style='Warning.TLabel') # Sets the style for the sync status label. Warning.TLabel is the style for the warning label. Offline mode is the status of the sync status label 
        
        # Manual sync button
        sync_button = ttk.Button(header_frame, 
                                text="Sync Now", 
                                command=self.manual_sync) # Sets the command for the sync button. manual_sync is the function that will be called when the sync button is clicked. 
        sync_button.pack(side=tk.RIGHT, padx=(0, 10)) # Packs the sync button to the right side of the header frame. padx=(0, 10), to add padding to 10 pixels to the right 
    
    def create_notebook(self): # Creates the notebook section using ttk.Notebook(). Self is the instance of the class on which the method is called. notebook is used to create the tabs to separate the content and improve the user experience and ideal for offline and online sync 
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(self.main_frame) # Creates a notebook for the tabs. ttk.Notebook() is the container for the tabs. Self.main_frame is the main frame of the application.
        self.notebook.pack(fill=tk.BOTH, expand=True) # Packs the notebook into the main frame. fill=tk.BOTH, to stretch the notebook to fill the entire width and height of the main frame. expand=True, to allow the notebook to grow and fill the entire width and height of the main frame.
        
        # Create tabs
        self.create_dashboard_tab() # Creates the dashboard tab using ttk.Frame(). Self is the instance of the class on which the method is called. Dashboard tab is the main tab for the appliction 
        self.create_contributions_tab() # Creates the contributions tab using ttk.Frame(). Self is the instance of the class on which the method is called. Contributions tab is used to add new contributions and track the contributions of the members
        self.create_members_tab() # Creates the members tab. Enables the management of the members and their contributions
        self.create_payouts_tab() # Creates the payouts tab. Enables the management of the payouts and transactions 
        self.create_settings_tab() # Creates the settings tab. Configures the settings to improve usability and security.
        self.create_admin_tab() # Creates the admin portal tab for comprehensive system management
    
    def create_dashboard_tab(self): # Defines the dashboard tab. For quick overview of the savings and transactions. Self is the instance of the class on which the method is called.
        """Create dashboard tab with savings overview"""
        dashboard_frame = ttk.Frame(self.notebook) # Creates a frame for the dashboard tab. ttk.Frame() is the container for the dashboard tab. Self.notebook is the notebook for the tabs. 
        self.notebook.add(dashboard_frame, text="📊 Dashboard") # Adds the dashboard tab to the notebook. text=
        
        # Summary section
        summary_frame = ttk.LabelFrame(dashboard_frame, text="Savings Summary", padding=10) # Creates a frame for the summary section. ttk.LabelFrame() is the container for the summary section. dashboard_frame is the frame for the dashboard tab. 
        summary_frame.pack(fill=tk.X, padx=10, pady=10) # Packs the summary frame into the dashboard frame. fill=tk.X, to stretch the frame to fill the entire width of the dashboard frame. padx=10, to add padding to 10 pixels to the left and right. pady=10, to add padding to 10 pixels to the top and bottom.
        
        # Total savings
        self.total_savings_label = ttk.Label(summary_frame, 
                                            text="Total Savings: 0.00", 
                                            style='Title.TLabel') # Sets the sytle for the total savings label. Title.TLabel is the style for the title label. 
        self.total_savings_label.pack(anchor=tk.W) # Packs the total savings label to the left side of the summary frame.
        
        # Member count
        self.member_count_label = ttk.Label(summary_frame, 
                                           text="Active Members: 0", 
                                           style='Title.TLabel') # Sets the style for the member count label. Title.TLabel is the style for the title label. 
        self.member_count_label.pack(anchor=tk.W) # Packs the member count label to the left side of the summary frame.
        
        # Recent activity
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity", padding=10) # Creates a frame for the recent activity section. ttk.LabelFrame() is the container for the recent activity section. dashboard_frame is the frame for the dashboard tab. 
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10) # Packs the recent activity frame into the dashboard frame. fill=tk.BOTH, to stretch the frame to fill the entire width and height of the dashboard frame. expand=True, to allow the frame to grow and fill the entire width and height of the dashboard frame. padx=10, to add padding to 10 pixels to the left and right. pady=10, to add padding to 10 pixels to the top and bottom.
        
        # Activity list
        self.activity_tree = ttk.Treeview(activity_frame, columns=('Date', 'Member', 'Amount', 'Type'), 
                                         show='headings', height=10) # Creates a treeview for the recent activity. ttk.Treeview() is the container for the recent activity. activity_frame is the frame for the recent activity section. 
        self.activity_tree.heading('Date', text='Date') # Sets the heading for the date column.
        self.activity_tree.heading('Member', text='Member') # Sets the heading for the member column.
        self.activity_tree.heading('Amount', text='Amount') # Sets the heading for the amount column.
        self.activity_tree.heading('Type', text='Type') # Sets the heading for the type column.
        
        self.activity_tree.column('Date', width=150) # Sets the width for the date column.
        self.activity_tree.column('Member', width=150) # Sets the width for the member column.
        self.activity_tree.column('Amount', width=100) # Sets the width for the amount column.
        self.activity_tree.column('Type', width=100) # Sets the width for the type column.
        
        self.activity_tree.pack(fill=tk.BOTH, expand=True) # Packs the recent activity tree into the recent activity frame. fill=tk.BOTH, to stretch the frame to fill the entire width and height of the recent activity frame. expand=True, to allow the frame to grow and fill the entire width and height of the recent activity frame.
        
        # Refresh button
        refresh_button = ttk.Button(dashboard_frame, # Creates a button for the refresh button. ttk.Button() is the container for the refresh button. dashboard_frame is the frame for the dashboard tab. 
                                   text="Refresh Dashboard", # Sets the text for the refresh button.
                                   command=self.refresh_dashboard) # Sets the command for the refresh button. refresh_dashboard is the function that will be called when the refresh button is clicked.
        refresh_button.pack(pady=10) # Packs the refresh button into the dashboard frame. pady=10, to add padding to 10 pixels to the top and bottom.
    
    def create_contributions_tab(self): # Defines the contributions tab. For adding new contributions. Self is the instance of the class on which the method is called.
        """Create contributions tab for adding new contributions"""
        contributions_frame = ttk.Frame(self.notebook) # Creates a frame for the contributions tab. ttk.Frame() is the container for the contributions tab. Self.notebook is the notebook for the tabs. 
        self.notebook.add(contributions_frame, text="💸 Add Contribution") # Adds the contributions tab to the notebook. text="💸 Add Contribution" is the text for the contributions tab.
        
        # Contribution form
        form_frame = ttk.LabelFrame(contributions_frame, text="New Contribution", padding=20) # Creates a frame for the contribution form. ttk.LabelFrame() is the container for the contribution form. contributions_frame is the frame for the contributions tab. 
        form_frame.pack(fill=tk.X, padx=20, pady=20) # Packs the contribution form into the contributions frame. fill=tk.X, to stretch the frame to fill the entire width of the contributions frame. padx=20, to add padding to 20 pixels to the left and right. pady=20, to add padding to 20 pixels to the top and bottom.
        
        # Member name
        ttk.Label(form_frame, text="Member Name:").grid(row=0, column=0, sticky=tk.W, pady=5) # Creates a label for the member name. ttk.Label() is the container for the member name. form_frame is the frame for the contribution form.
        self.member_name_entry = ttk.Entry(form_frame, width=30) # Creates an entry for the member name. ttk.Entry() is the container for the member name. form_frame is the frame for the contribution form.
        self.member_name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0)) # Packs the member name entry into the contribution form. row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0), to add padding to 10 pixels to the left and right.
        
        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky=tk.W, pady=5) # Creates a label for the amount. ttk.Label() is the container for the amount. form_frame is the frame for the contribution form.
        self.amount_entry = ttk.Entry(form_frame, width=30) # Creates an entry for the amount. ttk.Entry() is the container for the amount. form_frame is the frame for the contribution form.
        self.amount_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0)) # Packs the amount entry into the contribution form. row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0), to add padding to 10 pixels to the left and right.
        
        # Contribution type
        ttk.Label(form_frame, text="Type:").grid(row=2, column=0, sticky=tk.W, pady=5) # Creates a label for the contribution type. ttk.Label() is the container for the contribution type. form_frame is the frame for the contribution form.
        self.contribution_type = tk.StringVar(value="bitcoin")
        type_combo = ttk.Combobox(form_frame, textvariable=self.contribution_type, 
                                 values=["bitcoin", "usdt", "ugx"], width=27) # Creates a combobox for the contribution type. ttk.Combobox() is the container for the contribution type. form_frame is the frame for the contribution form.
        type_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0)) # Packs the contribution type combobox into the contribution form. row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0), to add padding to 10 pixels to the left and right.
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky=tk.W, pady=5) # Creates a label for the notes. ttk.Label() is the container for the notes. form_frame is the frame for the contribution form. Grid is used to position the label in the form frame.
        self.notes_text = scrolledtext.ScrolledText(form_frame, width=30, height=3) # Creates a scrolled text for the notes. scrolledtext.ScrolledText() is the container for the notes. form_frame is the frame for the contribution form.
        self.notes_text.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0)) # Packs the notes scrolled text into the contribution form. row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0), to add padding to 10 pixels to the left and right.
        
        # Submit button
        submit_button = ttk.Button(form_frame, 
                                  text="Add Contribution", 
                                  command=self.add_contribution) # Sets the command for the submit button. add_contribution is the function that will be called when the submit button is clicked.
        submit_button.grid(row=4, column=1, sticky=tk.W, pady=20, padx=(10, 0)) # Packs the submit button into the contribution form. row=4, column=1, sticky=tk.W, pady=20, padx=(10, 0), to add padding to 20 pixels to the top and bottom.
        
        # Bitcoin address display
        self.bitcoin_address_label = ttk.Label(form_frame, 
                                              text="", 
                                              style='Success.TLabel') # Sets the style for the bitcoin address label. Success.TLabel is the style for the success label.
        self.bitcoin_address_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5) # Packs the bitcoin address label into the contribution form. row=5, column=0, columnspan=2, sticky=tk.W, pady=5, to add padding to 5 pixels to the top and bottom.
    
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
    
    def create_admin_tab(self):
        """Create admin portal tab for comprehensive system management"""
        admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(admin_frame, text="🔐 Admin Portal")
        
        # Admin login section
        login_frame = ttk.LabelFrame(admin_frame, text="Admin Authentication", padding=10)
        login_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.admin_username = ttk.Entry(login_frame, width=30)
        self.admin_username.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.admin_password = ttk.Entry(login_frame, width=30, show="*")
        self.admin_password.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Login button
        self.admin_login_button = ttk.Button(login_frame, text="Login", command=self.admin_login)
        self.admin_login_button.grid(row=2, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        
        # Logout button (initially hidden)
        self.admin_logout_button = ttk.Button(login_frame, text="Logout", command=self.admin_logout)
        
        # Admin status
        self.admin_status_label = ttk.Label(login_frame, text="Not logged in", style='Warning.TLabel')
        self.admin_status_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Admin content (initially hidden)
        self.admin_content_frame = ttk.Frame(admin_frame)
        
        # System overview section
        overview_frame = ttk.LabelFrame(self.admin_content_frame, text="System Overview", padding=10)
        overview_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # System statistics
        self.system_stats_text = scrolledtext.ScrolledText(overview_frame, width=80, height=8)
        self.system_stats_text.pack(fill=tk.BOTH, expand=True)
        
        # User management section
        users_frame = ttk.LabelFrame(self.admin_content_frame, text="User Management", padding=10)
        users_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Users tree
        self.users_tree = ttk.Treeview(users_frame, 
                                      columns=('ID', 'Name', 'Phone', 'Email', 'Active', 'Contributions', 'Last Activity'), 
                                      show='headings', height=10)
        self.users_tree.heading('ID', text='ID')
        self.users_tree.heading('Name', text='Name')
        self.users_tree.heading('Phone', text='Phone')
        self.users_tree.heading('Email', text='Email')
        self.users_tree.heading('Active', text='Active')
        self.users_tree.heading('Contributions', text='Total Contributions')
        self.users_tree.heading('Last Activity', text='Last Activity')
        
        self.users_tree.column('ID', width=50)
        self.users_tree.column('Name', width=150)
        self.users_tree.column('Phone', width=120)
        self.users_tree.column('Email', width=200)
        self.users_tree.column('Active', width=80)
        self.users_tree.column('Contributions', width=120)
        self.users_tree.column('Last Activity', width=150)
        
        self.users_tree.pack(fill=tk.BOTH, expand=True)
        
        # User management buttons
        user_buttons_frame = ttk.Frame(users_frame)
        user_buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(user_buttons_frame, text="Refresh Users", command=self.refresh_admin_users).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(user_buttons_frame, text="Toggle User Status", command=self.toggle_user_status).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(user_buttons_frame, text="Delete User", command=self.delete_admin_user).pack(side=tk.LEFT, padx=(0, 10))
        
        # Activity monitoring section
        activity_frame = ttk.LabelFrame(self.admin_content_frame, text="Activity Monitoring", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Activity tree
        self.activity_admin_tree = ttk.Treeview(activity_frame, 
                                               columns=('Type', 'ID', 'Member', 'Amount', 'Sub Type', 'Timestamp', 'Status'), 
                                               show='headings', height=8)
        self.activity_admin_tree.heading('Type', text='Type')
        self.activity_admin_tree.heading('ID', text='ID')
        self.activity_admin_tree.heading('Member', text='Member')
        self.activity_admin_tree.heading('Amount', text='Amount')
        self.activity_admin_tree.heading('Sub Type', text='Sub Type')
        self.activity_admin_tree.heading('Timestamp', text='Timestamp')
        self.activity_admin_tree.heading('Status', text='Status')
        
        self.activity_admin_tree.column('Type', width=100)
        self.activity_admin_tree.column('ID', width=50)
        self.activity_admin_tree.column('Member', width=150)
        self.activity_admin_tree.column('Amount', width=100)
        self.activity_admin_tree.column('Sub Type', width=100)
        self.activity_admin_tree.column('Timestamp', width=150)
        self.activity_admin_tree.column('Status', width=100)
        
        self.activity_admin_tree.pack(fill=tk.BOTH, expand=True)
        
        # Activity buttons
        activity_buttons_frame = ttk.Frame(activity_frame)
        activity_buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(activity_buttons_frame, text="Refresh Activities", command=self.refresh_admin_activities).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(activity_buttons_frame, text="Export Activity Log", command=self.export_activity_log).pack(side=tk.LEFT, padx=(0, 10))
        
        # System management section
        system_frame = ttk.LabelFrame(self.admin_content_frame, text="System Management", padding=10)
        system_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # System health
        health_frame = ttk.Frame(system_frame)
        health_frame.pack(fill=tk.X, pady=5)
        
        self.system_health_label = ttk.Label(health_frame, text="System Health: Checking...")
        self.system_health_label.pack(side=tk.LEFT)
        
        ttk.Button(health_frame, text="Check Health", command=self.check_system_health).pack(side=tk.RIGHT)
        
        # System actions
        actions_frame = ttk.Frame(system_frame)
        actions_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(actions_frame, text="Force Sync All", command=self.force_sync_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="Clear Old Data", command=self.clear_old_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="Export System Report", command=self.export_system_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="Export User Report", command=self.export_user_report).pack(side=tk.LEFT, padx=(0, 10))
    
    def admin_login(self):
        """Handle admin login"""
        try:
            username = self.admin_username.get().strip()
            password = self.admin_password.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter username and password")
                return
            
            if self.admin_portal.authenticate_admin(username, password):
                self.admin_logged_in = True
                self.admin_status_label.config(text=f"Logged in as: {username}", style='Success.TLabel')
                self.admin_login_button.grid_remove()
                self.admin_logout_button.grid(row=2, column=1, sticky=tk.W, pady=10, padx=(10, 0))
                self.admin_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Load initial data
                self.refresh_admin_data()
                messagebox.showinfo("Success", f"Welcome, {username}!")
            else:
                messagebox.showerror("Error", "Invalid username or password")
                
        except Exception as e:
            self.logger.error(f"Admin login error: {e}")
            messagebox.showerror("Error", f"Login failed: {str(e)}")
    
    def admin_logout(self):
        """Handle admin logout"""
        try:
            self.admin_portal.logout_admin()
            self.admin_logged_in = False
            self.admin_status_label.config(text="Not logged in", style='Warning.TLabel')
            self.admin_logout_button.grid_remove()
            self.admin_login_button.grid(row=2, column=1, sticky=tk.W, pady=10, padx=(10, 0))
            self.admin_content_frame.pack_forget()
            
            # Clear form
            self.admin_username.delete(0, tk.END)
            self.admin_password.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Logged out successfully")
            
        except Exception as e:
            self.logger.error(f"Admin logout error: {e}")
            messagebox.showerror("Error", f"Logout failed: {str(e)}")
    
    def refresh_admin_data(self):
        """Refresh all admin data"""
        try:
            self.refresh_system_stats()
            self.refresh_admin_users()
            self.refresh_admin_activities()
            self.check_system_health()
        except Exception as e:
            self.logger.error(f"Error refreshing admin data: {e}")
    
    def refresh_system_stats(self):
        """Refresh system statistics"""
        try:
            stats = self.admin_portal.get_system_statistics()
            
            # Clear existing text
            self.system_stats_text.delete(1.0, tk.END)
            
            # Format and display statistics
            stats_text = "=== SYSTEM STATISTICS ===\n\n"
            
            # Database stats
            db_stats = stats.get('database', {})
            total_contributions = db_stats.get('total_contributions', [0, 0])
            stats_text += f"Database:\n"
            stats_text += f"  Total Amount: {total_contributions[0]:.2f}\n"
            stats_text += f"  Total Transactions: {total_contributions[1]}\n"
            stats_text += f"  Active Members: {len(db_stats.get('member_contributions', []))}\n"
            stats_text += f"  Pending Payouts: {len(db_stats.get('pending_payouts', []))}\n\n"
            
            # Wallet stats
            wallet_stats = stats.get('wallet', {})
            stats_text += f"Wallet:\n"
            stats_text += f"  Wallet Exists: {'Yes' if wallet_stats.get('wallet_exists') else 'No'}\n"
            stats_text += f"  Address Count: {wallet_stats.get('address_count', 0)}\n"
            stats_text += f"  Balance: {wallet_stats.get('balance', 0)}\n\n"
            
            # API stats
            api_stats = stats.get('api', {})
            stats_text += f"API:\n"
            stats_text += f"  Online Status: {'Online' if api_stats.get('online') else 'Offline'}\n"
            stats_text += f"  Pending Transactions: {api_stats.get('pending_transactions', 0)}\n\n"
            
            # System info
            system_info = stats.get('system', {})
            admin_session = system_info.get('admin_session', {})
            stats_text += f"System:\n"
            stats_text += f"  Current Admin: {admin_session.get('current_admin', 'None')}\n"
            stats_text += f"  Admin Level: {admin_session.get('admin_level', 'None')}\n"
            stats_text += f"  Session Duration: {admin_session.get('session_duration', 'N/A')}\n"
            
            self.system_stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            self.logger.error(f"Error refreshing system stats: {e}")
    
    def refresh_admin_users(self):
        """Refresh admin users list"""
        try:
            # Clear existing items
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            # Get users from admin portal
            users = self.admin_portal.get_user_management_data()
            
            for user in users:
                self.users_tree.insert('', 'end', values=(
                    user['id'],
                    user['name'],
                    user['phone'] or 'N/A',
                    user['email'] or 'N/A',
                    'Yes' if user['is_active'] else 'No',
                    f"{user['total_contributions']:.2f}",
                    user['last_contribution'] or 'Never'
                ))
                
        except Exception as e:
            self.logger.error(f"Error refreshing admin users: {e}")
    
    def refresh_admin_activities(self):
        """Refresh admin activities list"""
        try:
            # Clear existing items
            for item in self.activity_admin_tree.get_children():
                self.activity_admin_tree.delete(item)
            
            # Get activities from admin portal
            activities = self.admin_portal.get_activity_log(limit=50)
            
            for activity in activities:
                self.activity_admin_tree.insert('', 'end', values=(
                    activity['type'],
                    activity['id'],
                    activity['member_name'],
                    f"{activity['amount']:.2f}",
                    activity['sub_type'],
                    activity['timestamp'][:19] if activity['timestamp'] else 'N/A',
                    activity['status']
                ))
                
        except Exception as e:
            self.logger.error(f"Error refreshing admin activities: {e}")
    
    def toggle_user_status(self):
        """Toggle user active status"""
        try:
            selection = self.users_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a user")
                return
            
            item = self.users_tree.item(selection[0])
            user_id = int(item['values'][0])
            current_status = item['values'][4] == 'Yes'
            
            # Confirm action
            action = "deactivate" if current_status else "activate"
            if not messagebox.askyesno("Confirm", f"Are you sure you want to {action} this user?"):
                return
            
            # Update status
            new_status = not current_status
            if self.admin_portal.update_user_status(user_id, new_status):
                self.refresh_admin_users()
                messagebox.showinfo("Success", f"User {'activated' if new_status else 'deactivated'} successfully")
            else:
                messagebox.showerror("Error", "Failed to update user status")
                
        except Exception as e:
            self.logger.error(f"Error toggling user status: {e}")
            messagebox.showerror("Error", f"Failed to toggle user status: {str(e)}")
    
    def delete_admin_user(self):
        """Delete admin user"""
        try:
            selection = self.users_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a user")
                return
            
            item = self.users_tree.item(selection[0])
            user_id = int(item['values'][0])
            user_name = item['values'][1]
            
            # Confirm deletion
            if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete user '{user_name}'?\n\nThis action cannot be undone."):
                return
            
            # Delete user
            if self.admin_portal.delete_user(user_id):
                self.refresh_admin_users()
                messagebox.showinfo("Success", f"User '{user_name}' deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete user. User may have contributions.")
                
        except Exception as e:
            self.logger.error(f"Error deleting admin user: {e}")
            messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def check_system_health(self):
        """Check system health"""
        try:
            health = self.admin_portal.get_system_health()
            
            # Update health label
            status = health['overall_status']
            if status == 'healthy':
                self.system_health_label.config(text="System Health: Healthy", style='Success.TLabel')
            elif status == 'degraded':
                self.system_health_label.config(text="System Health: Degraded", style='Warning.TLabel')
            else:
                self.system_health_label.config(text="System Health: Error", style='Error.TLabel')
            
            # Show detailed health info
            health_text = f"Overall Status: {status.upper()}\n\n"
            
            for component, info in health['components'].items():
                health_text += f"{component.title()}:\n"
                health_text += f"  Status: {info['status']}\n"
                health_text += f"  Message: {info['message']}\n\n"
            
            if health['issues']:
                health_text += "Issues:\n"
                for issue in health['issues']:
                    health_text += f"  - {issue}\n"
                health_text += "\n"
            
            if health['recommendations']:
                health_text += "Recommendations:\n"
                for rec in health['recommendations']:
                    health_text += f"  - {rec}\n"
            
            messagebox.showinfo("System Health", health_text)
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            messagebox.showerror("Error", f"Failed to check system health: {str(e)}")
    
    def force_sync_all(self):
        """Force sync all pending transactions"""
        try:
            if not messagebox.askyesno("Confirm", "Force sync all pending transactions?"):
                return
            
            if self.admin_portal.force_sync_all():
                messagebox.showinfo("Success", "Force sync completed successfully")
                self.refresh_system_stats()
            else:
                messagebox.showwarning("Warning", "Force sync failed or no transactions to sync")
                
        except Exception as e:
            self.logger.error(f"Error force syncing: {e}")
            messagebox.showerror("Error", f"Force sync failed: {str(e)}")
    
    def clear_old_data(self):
        """Clear old data"""
        try:
            days = simpledialog.askinteger("Clear Old Data", 
                                         "Enter number of days (data older than this will be deleted):",
                                         minvalue=1, maxvalue=365)
            if days is None:
                return
            
            if not messagebox.askyesno("Confirm", f"Delete data older than {days} days?"):
                return
            
            deleted_count = self.admin_portal.clear_old_data(days)
            messagebox.showinfo("Success", f"Cleared {deleted_count} old records")
            
        except Exception as e:
            self.logger.error(f"Error clearing old data: {e}")
            messagebox.showerror("Error", f"Failed to clear old data: {str(e)}")
    
    def export_activity_log(self):
        """Export activity log"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                exported_file = self.admin_portal.export_admin_report('activities', filename)
                if exported_file:
                    messagebox.showinfo("Success", f"Activity log exported to: {exported_file}")
                else:
                    messagebox.showerror("Error", "Failed to export activity log")
                    
        except Exception as e:
            self.logger.error(f"Error exporting activity log: {e}")
            messagebox.showerror("Error", f"Failed to export activity log: {str(e)}")
    
    def export_system_report(self):
        """Export system report"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                exported_file = self.admin_portal.export_admin_report('system', filename)
                if exported_file:
                    messagebox.showinfo("Success", f"System report exported to: {exported_file}")
                else:
                    messagebox.showerror("Error", "Failed to export system report")
                    
        except Exception as e:
            self.logger.error(f"Error exporting system report: {e}")
            messagebox.showerror("Error", f"Failed to export system report: {str(e)}")
    
    def export_user_report(self):
        """Export user report"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                exported_file = self.admin_portal.export_admin_report('users', filename)
                if exported_file:
                    messagebox.showinfo("Success", f"User report exported to: {exported_file}")
                else:
                    messagebox.showerror("Error", "Failed to export user report")
                    
        except Exception as e:
            self.logger.error(f"Error exporting user report: {e}")
            messagebox.showerror("Error", f"Failed to export user report: {str(e)}")
    
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