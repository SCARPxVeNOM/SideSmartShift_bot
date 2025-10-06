#!/bin/bash

# Cross-Chain Swap Bot Deployment Script
# Usage: ./deploy.sh [digitalocean|aws|docker|heroku]

set -e

DEPLOYMENT_TYPE=${1:-docker}

echo "🚀 Deploying Cross-Chain Swap Bot using: $DEPLOYMENT_TYPE"

case $DEPLOYMENT_TYPE in
    "digitalocean")
        echo "📋 DigitalOcean Deployment"
        echo "1. Create a DigitalOcean Droplet (Ubuntu 20.04)"
        echo "2. Run these commands on your server:"
        echo ""
        echo "sudo apt update && sudo apt upgrade -y"
        echo "sudo apt install python3 python3-pip python3-venv git -y"
        echo "git clone <your-repo-url> /opt/swap-bot"
        echo "cd /opt/swap-bot"
        echo "python3 -m venv venv"
        echo "source venv/bin/activate"
        echo "pip install -r requirements.txt"
        echo "sudo npm install -g pm2"
        echo "pm2 start ecosystem.config.js"
        echo "pm2 save"
        echo "pm2 startup"
        ;;
    
    "aws")
        echo "📋 AWS EC2 Deployment"
        echo "1. Launch EC2 instance (Ubuntu 20.04)"
        echo "2. Run these commands on your server:"
        echo ""
        echo "sudo apt update && sudo apt upgrade -y"
        echo "sudo apt install python3 python3-pip python3-venv git -y"
        echo "git clone <your-repo-url> /home/ubuntu/swap-bot"
        echo "cd /home/ubuntu/swap-bot"
        echo "python3 -m venv venv"
        echo "source venv/bin/activate"
        echo "pip install -r requirements.txt"
        echo "sudo npm install -g pm2"
        echo "pm2 start run_bot.py --name swap-bot --interpreter python3"
        echo "pm2 save"
        echo "pm2 startup"
        ;;
    
    "docker")
        echo "🐳 Docker Deployment"
        echo "Building and starting containers..."
        
        # Create necessary directories
        mkdir -p data logs
        
        # Build and start
        docker-compose up -d
        
        echo "✅ Bot deployed with Docker!"
        echo "📊 View logs: docker-compose logs -f"
        echo "🛑 Stop bot: docker-compose down"
        ;;
    
    "heroku")
        echo "☁️ Heroku Deployment"
        echo "Prerequisites:"
        echo "1. Install Heroku CLI"
        echo "2. Login: heroku login"
        echo "3. Create app: heroku create your-bot-name"
        echo ""
        echo "Setting environment variables..."
        heroku config:set TELEGRAM_BOT_TOKEN=8212859489:AAFoxOz6XPo6LC929jV6BK9b_EpZa8bfooU
        heroku config:set SIDESHIFT_SECRET=a737abacea8b7a78e3aa0ef0f85acd8d
        heroku config:set SIDESHIFT_AFFILIATE_ID=ouG3iiiisS
        heroku config:set COMMISSION_RATE=0.005
        
        echo "Deploying..."
        git add .
        git commit -m "Deploy bot to Heroku" || true
        git push heroku main
        
        echo "Scaling worker..."
        heroku ps:scale worker=1
        
        echo "✅ Bot deployed to Heroku!"
        echo "📊 View logs: heroku logs --tail"
        ;;
    
    *)
        echo "❌ Invalid deployment type: $DEPLOYMENT_TYPE"
        echo "Usage: ./deploy.sh [digitalocean|aws|docker|heroku]"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment completed!"
echo "📱 Your bot should be running. Test it by messaging @SSmartSbot on Telegram"
