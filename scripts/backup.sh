#!/bin/bash
# Backup script for Cross-Chain Swap Bot

BACKUP_DIR="/opt/swap-bot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="swap_bot_backup_$DATE.tar.gz"

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE"     /opt/swap-bot/data     /opt/swap-bot/logs     /opt/swap-bot/.env.production

# Keep only last 7 days of backups
find $BACKUP_DIR -name "swap_bot_backup_*.tar.gz" -mtime +7 -delete

echo "$(date): Backup created: $BACKUP_FILE" >> /opt/swap-bot/logs/backup.log
