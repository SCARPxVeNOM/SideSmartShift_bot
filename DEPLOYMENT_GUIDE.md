# 🚀 Cross-Chain Swap Bot - Deployment Guide

## 📋 **Quick Start Options**

### **Option 1: Docker (Easiest)**
```bash
# Make script executable
chmod +x deploy.sh

# Deploy with Docker
./deploy.sh docker
```

### **Option 2: Cloud VPS (Recommended)**
```bash
# Choose your provider
./deploy.sh digitalocean  # For DigitalOcean
./deploy.sh aws          # For AWS EC2
```

### **Option 3: Heroku (Serverless)**
```bash
# Deploy to Heroku
./deploy.sh heroku
```

---

## 🏗️ **Detailed Deployment Methods**

### **1. DigitalOcean Droplet ($5/month)**

**Pros:** Simple, reliable, good documentation
**Cons:** Manual scaling

**Steps:**
1. Create DigitalOcean account
2. Create Ubuntu 20.04 droplet (1GB RAM minimum)
3. SSH into your server
4. Run the deployment commands from `deploy_digitalocean.md`

**Cost:** ~$5-10/month

### **2. AWS EC2 (Pay-as-you-go)**

**Pros:** Scalable, enterprise-grade, many services
**Cons:** More complex, can be expensive

**Steps:**
1. Create AWS account
2. Launch EC2 instance (t2.micro for free tier)
3. Follow `deploy_aws.md` instructions

**Cost:** $0-20/month (depending on instance type)

### **3. Docker Deployment (Any VPS)**

**Pros:** Consistent, portable, easy to manage
**Cons:** Requires Docker knowledge

**Steps:**
1. Install Docker on any Linux server
2. Run `docker-compose up -d`
3. Monitor with `docker-compose logs -f`

### **4. Heroku (Serverless)**

**Pros:** No server management, auto-scaling
**Cons:** More expensive, limited control

**Steps:**
1. Install Heroku CLI
2. Follow `deploy_heroku.md`
3. Scale with `heroku ps:scale worker=1`

**Cost:** $7+/month

---

## 🔧 **Production Setup**

### **Run Production Setup Script**
```bash
python setup_production.py
```

This creates:
- ✅ Production configuration
- ✅ Systemd service file
- ✅ Monitoring scripts
- ✅ Backup scripts
- ✅ Security configurations

### **Security Checklist**
- [ ] Change default passwords
- [ ] Configure firewall (UFW)
- [ ] Setup SSL certificates
- [ ] Enable log rotation
- [ ] Configure monitoring alerts
- [ ] Setup automated backups

---

## 📊 **Monitoring & Maintenance**

### **Health Monitoring**
```bash
# Check bot status
sudo systemctl status swap-bot

# View real-time logs
sudo journalctl -u swap-bot -f

# Run health check
./scripts/health_check.sh
```

### **Database Management**
```bash
# Backup database
./scripts/backup.sh

# View database
sqlite3 data/swap_bot.db
```

### **Performance Monitoring**
- Monitor CPU and memory usage
- Track API rate limits
- Monitor swap success rates
- Set up alerts for failures

---

## 💰 **Cost Comparison**

| Provider | Monthly Cost | Setup Time | Scalability | Best For |
|----------|-------------|------------|-------------|----------|
| DigitalOcean | $5-10 | 30 min | Manual | Small-Medium |
| AWS EC2 | $0-20 | 45 min | Auto | Enterprise |
| Heroku | $7+ | 15 min | Auto | Quick Start |
| Docker | Varies | 20 min | Manual | Developers |

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Bot not responding**
   ```bash
   # Check if running
   ps aux | grep python
   
   # Restart service
   sudo systemctl restart swap-bot
   ```

2. **Database errors**
   ```bash
   # Check permissions
   ls -la data/
   
   # Fix permissions
   sudo chown -R swapbot:swapbot data/
   ```

3. **API rate limits**
   ```bash
   # Check logs
   tail -f logs/swap_bot.log
   
   # Implement backoff in code
   ```

### **Log Locations**
- Application logs: `logs/swap_bot.log`
- System logs: `sudo journalctl -u swap-bot`
- Health check logs: `logs/health.log`

---

## 🔄 **Updates & Maintenance**

### **Updating the Bot**
```bash
# Pull latest changes
git pull origin main

# Restart service
sudo systemctl restart swap-bot
```

### **Database Migrations**
```bash
# Backup first
./scripts/backup.sh

# Run migrations (if any)
python database.py --migrate
```

### **Monitoring Commands**
```bash
# Check status
sudo systemctl status swap-bot

# View logs
sudo journalctl -u swap-bot -f

# Monitor resources
htop
```

---

## 📞 **Support**

- **Documentation:** This README and code comments
- **Logs:** Check `logs/` directory
- **Health:** Run `./scripts/health_check.sh`
- **Issues:** Check systemd logs with `sudo journalctl -u swap-bot`

---

## 🎯 **Next Steps After Deployment**

1. **Test the bot** by messaging @SSmartSbot
2. **Monitor performance** for 24-48 hours
3. **Set up alerts** for critical issues
4. **Configure backups** to run daily
5. **Scale resources** based on usage
6. **Add monitoring dashboards** (optional)

Your Cross-Chain Swap Bot is now ready for production! 🚀
