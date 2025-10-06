"""
Production setup script for Cross-Chain Swap Bot
Configures security, monitoring, and optimization for production deployment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the result"""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - Failed: {e.stderr}")
        return False

def setup_production():
    """Setup production environment"""
    logger.info("🚀 Setting up Cross-Chain Swap Bot for production...")
    
    # 1. Create production directory structure
    logger.info("📁 Creating directory structure...")
    directories = [
        "logs",
        "data", 
        "backups",
        "monitoring",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # 2. Create production configuration
    logger.info("⚙️ Creating production configuration...")
    
    production_config = """# Production Configuration
TELEGRAM_BOT_TOKEN=8212859489:AAFoxOz6XPo6LC929jV6BK9b_EpZa8bfooU
SIDESHIFT_SECRET=a737abacea8b7a78e3aa0ef0f85acd8d
SIDESHIFT_AFFILIATE_ID=ouG3iiiisS
COMMISSION_RATE=0.005
DATABASE_PATH=/opt/swap-bot/data/swap_bot.db
LOG_LEVEL=INFO
MONITOR_INTERVAL=60
TRACK_INTERVAL=300
HEALTH_CHECK_INTERVAL=300
MAX_SWAP_AMOUNT=10000.0
MIN_SWAP_AMOUNT=0.001
ADDRESS_VALIDATION_ENABLED=true
"""
    
    with open(".env.production", "w") as f:
        f.write(production_config)
    
    # 3. Create systemd service file
    logger.info("🔧 Creating systemd service...")
    
    service_content = """[Unit]
Description=Cross-Chain Swap Bot
After=network.target

[Service]
Type=simple
User=swapbot
Group=swapbot
WorkingDirectory=/opt/swap-bot
Environment=PATH=/opt/swap-bot/venv/bin
ExecStart=/opt/swap-bot/venv/bin/python run_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open("swap-bot.service", "w") as f:
        f.write(service_content)
    
    # 4. Create monitoring script
    logger.info("📊 Creating monitoring script...")
    
    monitoring_script = """#!/bin/bash
# Health check script for Cross-Chain Swap Bot

BOT_TOKEN="8212859489:AAFoxOz6XPo6LC929jV6BK9b_EpZa8bfooU"
LOG_FILE="/opt/swap-bot/logs/health.log"

check_bot() {
    response=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe")
    if echo "$response" | grep -q '"ok":true'; then
        echo "$(date): Bot is healthy" >> $LOG_FILE
        return 0
    else
        echo "$(date): Bot health check failed" >> $LOG_FILE
        return 1
    fi
}

check_database() {
    if [ -f "/opt/swap-bot/data/swap_bot.db" ]; then
        echo "$(date): Database exists" >> $LOG_FILE
        return 0
    else
        echo "$(date): Database not found" >> $LOG_FILE
        return 1
    fi
}

check_process() {
    if pgrep -f "run_bot.py" > /dev/null; then
        echo "$(date): Bot process is running" >> $LOG_FILE
        return 0
    else
        echo "$(date): Bot process not found" >> $LOG_FILE
        return 1
    fi
}

# Run all checks
check_bot && check_database && check_process
"""
    
    with open("scripts/health_check.sh", "w") as f:
        f.write(monitoring_script)
    
    os.chmod("scripts/health_check.sh", 0o755)
    
    # 5. Create backup script
    logger.info("💾 Creating backup script...")
    
    backup_script = """#!/bin/bash
# Backup script for Cross-Chain Swap Bot

BACKUP_DIR="/opt/swap-bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="swap_bot_backup_$DATE.tar.gz"

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    /opt/swap-bot/data \
    /opt/swap-bot/logs \
    /opt/swap-bot/.env.production

# Keep only last 7 days of backups
find $BACKUP_DIR -name "swap_bot_backup_*.tar.gz" -mtime +7 -delete

echo "$(date): Backup created: $BACKUP_FILE" >> /opt/swap-bot/logs/backup.log
"""
    
    with open("scripts/backup.sh", "w") as f:
        f.write(backup_script)
    
    os.chmod("scripts/backup.sh", 0o755)
    
    # 6. Create deployment instructions
    logger.info("📋 Creating deployment instructions...")
    
    instructions = """# Production Deployment Instructions

## 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv git curl -y

# Create user
sudo useradd -m -s /bin/bash swapbot
sudo usermod -aG sudo swapbot
```

## 2. Deploy Application
```bash
# Clone repository
sudo git clone <your-repo-url> /opt/swap-bot
sudo chown -R swapbot:swapbot /opt/swap-bot

# Switch to user
sudo su - swapbot
cd /opt/swap-bot

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure Service
```bash
# Copy service file
sudo cp swap-bot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable swap-bot
sudo systemctl start swap-bot

# Check status
sudo systemctl status swap-bot
```

## 4. Setup Monitoring
```bash
# Add to crontab for health checks
crontab -e

# Add this line:
*/5 * * * * /opt/swap-bot/scripts/health_check.sh

# Add daily backups
0 2 * * * /opt/swap-bot/scripts/backup.sh
```

## 5. Security
```bash
# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Setup log rotation
sudo nano /etc/logrotate.d/swap-bot
```

## 6. Monitoring Commands
```bash
# Check bot status
sudo systemctl status swap-bot

# View logs
sudo journalctl -u swap-bot -f

# Check health
/opt/swap-bot/scripts/health_check.sh

# View bot logs
tail -f /opt/swap-bot/logs/swap_bot.log
```
"""
    
    with open("DEPLOYMENT.md", "w") as f:
        f.write(instructions)
    
    logger.info("✅ Production setup completed!")
    logger.info("📋 See DEPLOYMENT.md for detailed instructions")
    logger.info("🚀 Your bot is ready for production deployment!")

if __name__ == "__main__":
    setup_production()
