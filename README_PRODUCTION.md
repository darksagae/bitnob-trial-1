# Ajo Bitcoin Savings App - Production Ready

A comprehensive Bitcoin and Mobile Money group savings application for Uganda, optimized for real-world use with separate admin and user interfaces, commission tracking, and Bitnob API integration.

## 🚀 Features

### Core Functionality
- **Separate Admin & User Interfaces**: Independent Tkinter windows for different user roles
- **Mobile Money Integration**: Support for MTN, Airtel, and M-Pesa via Bitnob API
- **Commission System**: 1% commission on all transactions, tracked and transferable
- **Offline-First Design**: Full functionality without internet, with background sync
- **Modern GUI**: Clean, intuitive interface with modern styling

### Admin Features
- **Group Management**: Create, edit, and delete savings groups
- **Payout Management**: Approve and process payouts with commission tracking
- **User Management**: Manage user roles and account status
- **Commission Dashboard**: View and transfer earned commissions
- **System Monitoring**: Real-time system health and status

### User Features
- **Contribution Management**: Add contributions with automatic commission calculation
- **Personal Dashboard**: View savings summary and recent activity
- **Multiple Payment Methods**: Mobile money, Bitcoin, and USDT support

## 📁 File Structure

```
ajo/
├── main_new.py              # Main application entry point
├── database_new.py          # SQLite database management
├── api_new.py              # Bitnob API integration
├── ui_new.py               # Separate AdminUI and UserUI classes
├── config.py               # Application configuration
├── utils.py                # Utility functions and helpers
├── requirements_new.txt    # Production dependencies
├── ajo.db                  # SQLite database (created automatically)
├── logs/                   # Application logs
├── backups/                # Database backups
├── exports/                # Data exports
└── assets/                 # Application assets
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Setup Instructions

1. **Clone or download the project**
   ```bash
   # If using git
   git clone <repository-url>
   cd ajo
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv ajo_env
   
   # Windows
   ajo_env\Scripts\activate
   
   # macOS/Linux
   source ajo_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements_new.txt
   ```

4. **Configure API settings**
   - Edit `config.py`
   - Replace `YOUR_BITNOB_API_KEY_HERE` with your actual Bitnob API key
   - Set `API_MOCK_MODE = False` for production use

5. **Run the application**
   ```bash
   python main_new.py
   ```

## 🔐 Default Login Credentials

### Demo Mode (Default)
- **Admin**: `admin` / `admin123`
- **User**: `user` / `user123`

### Production Setup
1. Change default passwords after first login
2. Create additional admin users as needed
3. Set up proper user accounts for your organization

## 💰 Commission System

The app automatically calculates and tracks a 1% commission on all transactions:

- **Contributions**: 1% commission deducted from contribution amount
- **Payouts**: 1% commission deducted from payout amount
- **Tracking**: All commissions stored in database with transfer status
- **Transfer**: Admins can transfer accumulated commissions to their Bitnob wallet

### Commission Example
- User contributes 100,000 UGX
- Net contribution: 99,000 UGX (1,000 UGX commission)
- Commission stored for admin transfer

## 🌐 Bitnob API Integration

### Supported Payment Methods
- **Mobile Money**: MTN, Airtel, M-Pesa Uganda
- **Cryptocurrency**: Bitcoin, USDT (TRC20)
- **API Features**: Payment processing, status checking, balance inquiry

### Configuration
```python
# In config.py
BITNOB_API_KEY = "your_actual_api_key_here"
API_MOCK_MODE = False  # Set to True for offline development
```

### API Endpoints Used
- Account balance: `/v1/account/balance`
- Mobile money transfer: `/v1/transfers/sendmobilemoney`
- Bitcoin transfer: `/v1/transfers/sendbitcoin`
- USDT transfer: `/v1/transfers/sendusdt`
- Transaction status: `/v1/transfers/{id}`

## 📊 Database Schema

### Core Tables
- **users**: User accounts and authentication
- **groups**: Savings groups
- **group_members**: Group membership (many-to-many)
- **contributions**: User contributions with commission tracking
- **payouts**: Payout requests and processing
- **commissions**: Commission tracking and transfer status
- **settings**: Application configuration

### Key Features
- **Foreign Key Constraints**: Data integrity
- **Indexes**: Optimized query performance
- **Soft Deletes**: Data preservation
- **Audit Trail**: Timestamps on all records

## 🔧 Configuration

### Main Configuration (`config.py`)
```python
# Commission rate
COMMISSION_RATE = 0.01  # 1%

# API settings
BITNOB_API_BASE_URL = "https://api.bitnob.co"
BITNOB_API_KEY = "your_api_key"

# GUI settings
GUI_THEME = "clam"
GUI_COLORS = {...}

# Validation rules
MIN_CONTRIBUTION_AMOUNT = 1000  # 1,000 UGX
MAX_CONTRIBUTION_AMOUNT = 10000000  # 10M UGX
```

### Development Settings
```python
DEBUG_MODE = True
DEMO_MODE = True  # Creates demo data
API_MOCK_MODE = True  # Simulates API calls
```

## 🚀 Production Deployment

### 1. Environment Setup
```bash
# Production environment
python -m venv ajo_prod
source ajo_prod/bin/activate  # or ajo_prod\Scripts\activate on Windows
pip install -r requirements_new.txt
```

### 2. Configuration
```python
# In config.py
DEBUG_MODE = False
DEMO_MODE = False
API_MOCK_MODE = False
BITNOB_API_KEY = "your_production_api_key"
```

### 3. Database Setup
- Database created automatically on first run
- Backup regularly using the admin interface
- Monitor logs in `logs/app.log`

### 4. Security Considerations
- Change default passwords
- Secure API key storage
- Regular database backups
- Monitor access logs

## 📈 Usage Examples

### Admin Workflow
1. **Login** as admin
2. **Create Groups** for different savings purposes
3. **Manage Users** and assign to groups
4. **Approve Payouts** as requested by users
5. **Transfer Commissions** to your Bitnob wallet
6. **Monitor System** health and performance

### User Workflow
1. **Login** as user
2. **View Dashboard** with savings summary
3. **Add Contributions** to your groups
4. **Track Activity** and commission payments
5. **Request Payouts** when needed

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure all dependencies installed
pip install -r requirements_new.txt
```

**2. Database Errors**
```bash
# Check database file permissions
# Ensure write access to project directory
```

**3. API Connection Issues**
```bash
# Check internet connection
# Verify API key in config.py
# Set API_MOCK_MODE = True for offline testing
```

**4. GUI Issues**
```bash
# Ensure tkinter is available
python -c "import tkinter; print('tkinter available')"
```

### Log Files
- **Application logs**: `logs/app.log`
- **Error details**: Check log level in config.py
- **Debug mode**: Set `DEBUG_MODE = True` for verbose logging

## 🔄 Updates and Maintenance

### Regular Maintenance
1. **Database Backups**: Use admin interface or manual backup
2. **Log Rotation**: Monitor log file sizes
3. **API Key Rotation**: Update Bitnob API keys as needed
4. **User Management**: Regular review of user accounts

### Future Enhancements
- **Multi-language Support**: Localization for different regions
- **Advanced Reporting**: Detailed analytics and reports
- **Mobile App**: Companion mobile application
- **Blockchain Integration**: Direct blockchain transactions

## 📞 Support

### Documentation
- **API Documentation**: [Bitnob API Docs](https://docs.bitnob.com/)
- **Python tkinter**: [Official Documentation](https://docs.python.org/3/library/tkinter.html)

### Issues and Questions
- Check log files for error details
- Verify configuration settings
- Test with demo mode first
- Contact development team for support

## 📄 License

This project is developed for the Bitnob Uganda Hackathon and is intended for educational and commercial use in Uganda.

---

**Ajo Bitcoin Savings App** - Empowering group savings with modern technology for Uganda's financial inclusion. 