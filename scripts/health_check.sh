#!/bin/bash
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
