# Cross-Chain Swap Bot for Telegram

A comprehensive Telegram bot for cross-chain cryptocurrency swapping using the SideShift.ai API. This bot allows users to exchange cryptocurrencies across different blockchains directly through Telegram with support for both fixed and variable rate swaps.

## Features

### Core Functionality
- 🔄 **Cross-chain swaps** using SideShift.ai API
- 🔒 **Fixed rate swaps** (15-minute rate guarantee)
- 📊 **Variable rate swaps** (7-day validity)
- 💰 **Commission earning** for bot operators
- 📱 **User-friendly Telegram interface**

### Advanced Features
- 📈 **Price monitoring** and alerts
- 📊 **Swap history** and statistics
- 🔔 **Real-time notifications** for status updates
- 🛡️ **Address validation** and security checks
- 💾 **SQLite database** for data persistence
- 🔄 **Background monitoring** of active swaps

### Supported Operations
- Create and manage cryptocurrency swaps
- Track swap status in real-time
- View trading history and statistics
- Set up price alerts
- Monitor multiple blockchain networks

## Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from @BotFather)
- SideShift.ai account and API credentials

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd teleswap
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   
   # SideShift.ai API Configuration
   SIDESHIFT_SECRET=your_sideshift_secret_here
   SIDESHIFT_AFFILIATE_ID=your_affiliate_id_here
   
   # Optional Configuration
   COMMISSION_RATE=0.005
   DATABASE_PATH=swap_bot.db
   MONITOR_INTERVAL=60
   TRACK_INTERVAL=300
   ```

4. **Get API credentials**
   - Create a Telegram bot via [@BotFather](https://t.me/BotFather)
   - Sign up at [SideShift.ai](https://sideshift.ai/account)
   - Copy your Private Key and Affiliate ID

## Usage

### Starting the Bot
```bash
python main.py
```

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and main menu |
| `/swap` | Start a new cryptocurrency swap |
| `/status` | Check current swap status |
| `/history` | View swap history |
| `/rates` | Check exchange rates |
| `/alerts` | Manage price alerts |
| `/stats` | View trading statistics |
| `/help` | Show help information |
| `/cancel` | Cancel current operation |

### Swap Process

1. **Choose swap type**: Fixed rate (15 min) or Variable rate (7 days)
2. **Select source coin**: Choose the cryptocurrency to swap from
3. **Select source network**: Choose the blockchain network
4. **Select destination coin**: Choose the cryptocurrency to receive
5. **Select destination network**: Choose the target blockchain
6. **Enter amount** (fixed rate only): Specify the exact amount to swap
7. **Provide addresses**: Enter destination and optional refund addresses
8. **Confirm and send**: Receive deposit address and transaction details

## Architecture

### Core Components

- **`main.py`**: Application entry point and orchestration
- **`swap_bot.py`**: Main Telegram bot logic and command handlers
- **`sideshift_api.py`**: SideShift.ai API wrapper
- **`database.py`**: SQLite database operations
- **`monitor.py`**: Background monitoring and notifications

### Database Schema

- **`users`**: User information and statistics
- **`swaps`**: Swap transaction records
- **`price_alerts`**: User-configured price alerts
- **`user_sessions`**: Temporary user session state
- **`rate_history`**: Historical price data

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Required |
| `SIDESHIFT_SECRET` | SideShift API secret | Required |
| `SIDESHIFT_AFFILIATE_ID` | SideShift affiliate ID | Required |
| `COMMISSION_RATE` | Commission rate (0.0-0.02) | 0.005 |
| `DATABASE_PATH` | SQLite database path | swap_bot.db |
| `MONITOR_INTERVAL` | Swap monitoring interval (seconds) | 60 |
| `TRACK_INTERVAL` | Price tracking interval (seconds) | 300 |

### Commission Structure

The bot supports commission earning through SideShift.ai:
- Default commission: 0.5%
- Configurable range: 0% to 2%
- Commission embedded in exchange rates
- Automatic payout based on thresholds

## Security Considerations

### Production Deployment

1. **IP Address Handling**: Implement proper user IP detection
2. **Address Validation**: Add comprehensive crypto address validation
3. **Rate Limiting**: Implement API rate limiting (5 shifts/min, 20 quotes/min)
4. **Error Handling**: Add robust error handling and logging
5. **Data Encryption**: Encrypt sensitive data in database

### Security Best Practices

- Keep API credentials secure
- Validate all user inputs
- Implement transaction limits
- Monitor for suspicious activity
- Regular security audits

## Monitoring and Maintenance

### Background Tasks

- **Swap Monitoring**: Checks active swap statuses every minute
- **Price Tracking**: Monitors price changes for alerts
- **Health Checks**: System health monitoring every 5 minutes
- **Database Cleanup**: Automatic cleanup of old data

### Logging

- Application logs: `swap_bot.log`
- Error tracking and debugging
- Performance monitoring
- User activity logging

## API Integration

### SideShift.ai API Features

- Fixed and variable rate swaps
- Real-time exchange rates
- Multi-network support
- Commission management
- Status tracking
- Refund handling

### Supported Networks

- Bitcoin (BTC)
- Ethereum (ETH)
- Arbitrum
- Polygon
- BSC (Binance Smart Chain)
- And many more...

## Development

### Project Structure
```
teleswap/
├── main.py                 # Application entry point
├── swap_bot.py            # Telegram bot implementation
├── sideshift_api.py       # SideShift API wrapper
├── database.py            # Database operations
├── monitor.py             # Background monitoring
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
└── swap_bot.log          # Application logs
```

### Adding New Features

1. **New Commands**: Add handlers in `swap_bot.py`
2. **API Endpoints**: Extend `sideshift_api.py`
3. **Database Changes**: Update schema in `database.py`
4. **Monitoring**: Add tasks in `monitor.py`

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check token and network connection
2. **API errors**: Verify SideShift credentials
3. **Database errors**: Check file permissions and disk space
4. **Swap failures**: Verify addresses and amounts

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## Support

- **SideShift.ai Support**: help@sideshift.ai
- **Telegram Support**: Contact bot operator
- **Documentation**: SideShift.ai API docs
- **Issues**: Report via GitHub issues

## License

This project is for educational and commercial use. Please ensure compliance with local regulations regarding cryptocurrency trading and bot operations.

## Disclaimer

This bot is provided as-is. Users are responsible for:
- Verifying all transaction details
- Understanding cryptocurrency risks
- Complying with local regulations
- Securing their private keys and addresses

The bot operators are not responsible for any financial losses or technical issues.
