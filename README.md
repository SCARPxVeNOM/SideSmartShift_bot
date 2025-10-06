# SideSmartShift_Bot
 🔄 Cross-Chain Swap Bot for Telegram

A powerful Telegram bot that enables users to perform cross-chain cryptocurrency swaps directly through Telegram using the SideShift.ai API. The bot supports both fixed-rate and variable-rate swaps across multiple blockchains.

## ✨ Features

- **🔄 Cross-Chain Swaps**: Swap cryptocurrencies across different blockchains
- **🔒 Fixed Rate Swaps**: Lock in exchange rates for 15 minutes
- **📊 Variable Rate Swaps**: Get market rates when deposit is received (7-day validity)
- **📱 Telegram Integration**: Intuitive interface with inline keyboards
- **📊 Real-time Monitoring**: Track swap status and receive updates
- **📈 Price Alerts**: Set up alerts for price changes (coming soon)
- **📋 Swap History**: View your complete swap history
- **📊 Statistics**: Track your trading statistics
- **🛡️ Address Validation**: Basic crypto address validation
- **💾 SQLite Database**: Persistent storage for users and swaps

## 🚀 Supported Blockchains

The bot supports all cryptocurrencies and networks available on SideShift.ai, including:

- **Bitcoin** (BTC) - Bitcoin, Lightning Network
- **Ethereum** (ETH) - Ethereum, Polygon, BSC, Arbitrum, Optimism
- **Litecoin** (LTC) - Litecoin
- **Dogecoin** (DOGE) - Dogecoin
- **And many more...**

## 📋 Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- SideShift.ai API credentials
- Git (for deployment)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/teleswap.git
cd teleswap
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
# Production Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
SIDESHIFT_SECRET=your_sideshift_secret_here
SIDESHIFT_AFFILIATE_ID=your_affiliate_id_here
COMMISSION_RATE=0.005
DATABASE_PATH=swap_bot.db
LOG_LEVEL=INFO
MONITOR_INTERVAL=60
TRACK_INTERVAL=300
HEALTH_CHECK_INTERVAL=300
MAX_SWAP_AMOUNT=10000.0
MIN_SWAP_AMOUNT=0.001
ADDRESS_VALIDATION_ENABLED=true
```

### 4. Get API Credentials

#### Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token to your `.env` file

#### SideShift.ai Credentials
1. Visit [SideShift.ai](https://sideshift.ai)
2. Create an account and get your API credentials
3. Add your secret and affiliate ID to the `.env` file

## 🚀 Running the Bot

### Local Development

```bash
# Run the simplified version (recommended)
python run_bot.py

# Or run the full application with monitoring
python main.py
```

### Production Deployment

#### Option 1: Render (Free Tier)
1. Push your code to GitHub
2. Connect your repository to [Render](https://render.com)
3. Create a new Web Service
4. Set environment variables in Render dashboard
5. Deploy!

#### Option 2: Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "worker: python run_bot.py" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### Option 3: VPS/Cloud Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run as a service
nohup python run_bot.py > bot.log 2>&1 &
```

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and main menu |
| `/swap` | Start a new cross-chain swap |
| `/status` | Check current swap status |
| `/history` | View your swap history |
| `/rates` | Check exchange rates |
| `/alerts` | Manage price alerts |
| `/stats` | View your trading statistics |
| `/cancel` | Cancel current operation |
| `/help` | Show help information |

## 🔄 How to Use

### 1. Start a Swap
1. Send `/swap` to the bot
2. Choose between **Fixed Rate** or **Variable Rate**
3. Enter the coin symbol you want to swap FROM (e.g., `BTC`)
4. Select the network for the deposit coin
5. Enter the coin symbol you want to receive (e.g., `ETH`)
6. Select the network for the settlement coin
7. Enter the amount to swap (for fixed rate) or destination address (for variable rate)
8. Provide your destination address
9. Optionally provide a refund address
10. Confirm the swap details

### 2. Fixed vs Variable Rate

**Fixed Rate:**
- Rate is locked for 15 minutes
- You know exactly what you'll receive
- Must send exact amount within time limit
- Best for: Predictable swaps

**Variable Rate:**
- Rate determined when deposit is received
- Valid for 7 days
- Can send any amount within min/max limits
- Best for: Flexible timing

### 3. Track Your Swap
- Use `/status` to check current swap status
- Visit the SideShift.ai tracking URL provided
- Receive automatic updates when status changes

## 🏗️ Project Structure

```
teleswap/
├── main.py                 # Main application entry point
├── run_bot.py             # Simplified bot runner
├── swap_bot.py            # Telegram bot logic
├── sideshift_api.py       # SideShift.ai API wrapper
├── database.py            # Database operations
├── monitor.py             # Background monitoring
├── config.py              # Configuration management
├── utils.py               # Utility functions
├── test_bot.py            # Bot testing script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── swap_bot.db           # SQLite database (created on first run)
```

## 🔧 Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Required |
| `SIDESHIFT_SECRET` | SideShift.ai API secret | Required |
| `SIDESHIFT_AFFILIATE_ID` | Your affiliate ID | Required |
| `COMMISSION_RATE` | Commission rate (0.005 = 0.5%) | 0.005 |
| `DATABASE_PATH` | SQLite database file path | swap_bot.db |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `MONITOR_INTERVAL` | Swap monitoring interval (seconds) | 60 |
| `TRACK_INTERVAL` | Price tracking interval (seconds) | 300 |
| `HEALTH_CHECK_INTERVAL` | Health check interval (seconds) | 300 |
| `MAX_SWAP_AMOUNT` | Maximum swap amount | 10000.0 |
| `MIN_SWAP_AMOUNT` | Minimum swap amount | 0.001 |
| `ADDRESS_VALIDATION_ENABLED` | Enable address validation | true |

## 🛡️ Security Features

- **Environment Variables**: All sensitive data stored in `.env` file
- **Address Validation**: Basic crypto address format validation
- **Input Sanitization**: All user inputs are validated
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Built-in rate limiting for API calls

## 📊 Database Schema

The bot uses SQLite with the following tables:

- **users**: User information and preferences
- **swaps**: Swap history and status
- **price_alerts**: Price alert configurations
- **user_sessions**: Temporary user session data

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if the bot token is correct
   - Ensure the bot is running and not conflicting with other instances
   - Check logs for error messages

2. **Swap creation fails**
   - Verify SideShift.ai API credentials
   - Check if the coin pair is supported
   - Ensure addresses are valid

3. **Database errors**
   - Check file permissions for the database file
   - Ensure the database directory exists

### Logs

Check the log files for detailed error information:
- `swap_bot.log` - Main application logs
- Console output for real-time debugging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This bot is for educational and personal use. Cryptocurrency trading involves risk. Always:

- Double-check addresses before sending funds
- Verify swap details before confirming
- Keep your API credentials secure
- Test with small amounts first

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/teleswap/issues)
- **SideShift.ai Support**: [help@sideshift.ai](mailto:help@sideshift.ai)
- **Telegram**: Contact the bot owner

## 🙏 Acknowledgments

- [SideShift.ai](https://sideshift.ai) for the excellent API
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram library
- The open-source community for inspiration and tools

---

**Made with ❤️ for the crypto community**
