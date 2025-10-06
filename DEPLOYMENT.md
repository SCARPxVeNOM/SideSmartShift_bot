# Production Deployment Instructions

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
