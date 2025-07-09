# 💰 Ajo - Bitcoin Group Savings App for Uganda

**Bitnob Hackathon Entry - Empowering Uganda through Bitcoin-based group savings**

Ajo is a comprehensive Bitcoin-based group savings application designed specifically for Uganda's traditional Ajo savings culture, integrated with Bitnob's Bitcoin and mobile money services.

## 🌟 Features

### 💾 Offline-First Design
- **Local SQLite Database**: Store all savings data locally with encryption
- **Offline Bitcoin Address Generation**: Generate Bitcoin addresses without internet
- **Encrypted Data Storage**: Secure sensitive information using AES encryption
- **Offline Transaction Queue**: Queue transactions for sync when online

### 🏦 Bitnob Integration
- **Bitcoin Transactions**: Send and receive Bitcoin via Bitnob API
- **USDT Support**: Handle USDT transfers on TRC20 network
- **Mobile Money Payouts**: Process M-Pesa, Airtel Money, and MTN Mobile Money
- **Real-time Exchange Rates**: Get live currency conversion rates
- **Webhook Support**: Real-time transaction notifications

### 👥 Group Savings Management
- **Member Management**: Add and track group members
- **Contribution Tracking**: Record Bitcoin, USDT, and UGX contributions
- **Savings Summary**: Comprehensive dashboard with analytics
- **Payout Processing**: Distribute savings via mobile money
- **Report Generation**: Export savings reports to CSV

### 🖥️ User-Friendly Interface
- **Intuitive Tkinter GUI**: Easy-to-use interface for non-technical users
- **Tabbed Interface**: Organized sections for different functions
- **Real-time Status**: Online/offline status indicators
- **Background Sync**: Automatic data synchronization

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ajo-bitcoin-savings
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

### Manual Installation

If you prefer to install dependencies manually:

```bash
pip install bitcoinlib==0.6.0
pip install pycryptodome==3.19.0
pip install requests==2.31.0
```

## 📁 Project Structure

```
ajo_app/
├── main.py           # Application entry point and orchestrator
├── database.py       # SQLite database with encryption
├── wallet.py         # Bitcoin wallet management
├── api.py            # Bitnob API integration
├── ui.py             # Tkinter user interface
├── requirements.txt  # Python dependencies
├── README.md         # This file
├── demo.py           # Demo script for testing
├── logs/             # Application logs
├── wallets/          # Bitcoin wallet files
└── backups/          # Database backups
```

## 🔧 Configuration

### Bitnob API Setup

1. **Get API Key**: Sign up at [Bitnob](https://bitnob.com) and get your API key
2. **Configure API**: Open the app and go to Settings → API Settings
3. **Enter API Key**: Paste your Bitnob API key and save

### Database Configuration

The app uses SQLite by default. Database files are stored locally:
- **Main Database**: `ajo_savings.db`
- **Wallet Database**: `wallets/bitcoinlib.db`
- **Backups**: `backups/` directory

## 💡 Usage Guide

### Getting Started

1. **Launch the App**: Run `python main.py`
2. **Add Members**: Go to Members tab and add group members
3. **Record Contributions**: Use the Add Contribution tab to record savings
4. **Monitor Progress**: Check the Dashboard for savings summary
5. **Process Payouts**: Use the Payouts tab for mobile money distributions

### Adding Contributions

1. Navigate to "💸 Add Contribution" tab
2. Enter member name
3. Specify amount
4. Choose contribution type (Bitcoin, USDT, or UGX)
5. Add optional notes
6. Click "Add Contribution"

For Bitcoin contributions, a unique address will be generated automatically.

### Processing Payouts

1. Go to "💳 Payouts" tab
2. Enter member name
3. Specify amount in UGX
4. Enter phone number
5. Select mobile money provider
6. Click "Process Payout"

### Exporting Reports

1. Navigate to "⚙️ Settings" tab
2. Click "Export Savings Report"
3. Choose save location
4. Report will be saved as CSV file

## 🔒 Security Features

- **AES Encryption**: All sensitive data is encrypted before storage
- **Secure Key Management**: Bitcoin wallet keys are stored securely
- **Offline Operation**: Core functionality works without internet
- **Data Validation**: Input validation and sanitization
- **Error Handling**: Comprehensive error handling and logging

## 🌍 Uganda-Specific Features

### Mobile Money Integration
- **M-Pesa Uganda**: Primary mobile money provider
- **Airtel Money**: Alternative mobile money option
- **MTN Mobile Money**: Third mobile money provider
- **UGX Support**: Native Ugandan Shilling support

### Cultural Adaptation
- **Ajo Tradition**: Designed around traditional group savings culture
- **Offline Capability**: Works in areas with limited internet
- **Local Currency**: Full UGX support with Bitcoin/USDT options
- **Community Focus**: Group-based savings management

## 🧪 Testing and Demo

### Demo Mode

The app includes a demo mode for testing without real API keys:

```bash
python demo.py
```

This will:
- Create sample data
- Demonstrate all features
- Show offline functionality
- Test UI components

### Sample Data

Demo mode creates:
- 5 sample members
- 10 sample contributions
- 3 sample payouts
- Bitcoin addresses for testing

## 📊 API Integration

### Bitnob API Endpoints Used

- `GET /v1/user` - User information
- `GET /v1/accounts/balance` - Account balance
- `GET /v1/rates` - Exchange rates
- `POST /v1/addresses/bitcoin` - Generate Bitcoin addresses
- `POST /v1/transactions/bitcoin` - Send Bitcoin
- `POST /v1/transactions/mobile-money` - Mobile money payouts
- `POST /v1/transactions/usdt` - USDT transfers

### Webhook Support

Configure webhooks for real-time notifications:
- Transaction completions
- Payment confirmations
- Error notifications

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Errors**: Check file permissions and disk space
   ```bash
   # Backup and recreate database
   python -c "from database import AjoDatabase; AjoDatabase().backup_database()"
   ```

3. **API Connection Issues**: Verify internet connection and API key
   ```bash
   # Test API connection
   python -c "from api import BitnobAPI; print(BitnobAPI().is_online())"
   ```

4. **Wallet Issues**: Check wallet directory permissions
   ```bash
   # Recreate wallet
   rm -rf wallets/
   python main.py
   ```

### Logs

Check application logs in the `logs/` directory:
```bash
tail -f logs/ajo_$(date +%Y%m%d).log
```

## 🤝 Contributing

### For Hackathon Judges

This project demonstrates:

1. **Technical Depth**: Bitcoin integration, encryption, offline capabilities
2. **Local Impact**: Uganda-specific mobile money and cultural adaptation
3. **Innovation**: Combining traditional Ajo with modern Bitcoin technology
4. **User Experience**: Intuitive interface for non-technical users
5. **Scalability**: Modular design for future enhancements

### Development Setup

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is created for Bitnob's Uganda Hackathon. All rights reserved.

## 🙏 Acknowledgments

- **Bitnob Team**: For providing the API and hackathon opportunity
- **Bitcoin Community**: For the underlying technology
- **Uganda Tech Community**: For inspiration and cultural insights
- **Open Source Contributors**: For the libraries used in this project

## 📞 Support

For hackathon-related questions:
- **Email**: [Your Email]
- **GitHub**: [Your GitHub]
- **Bitnob**: [Bitnob Support](https://bitnob.com/support)

---

**Built with ❤️ for Uganda's financial inclusion through Bitcoin technology** 