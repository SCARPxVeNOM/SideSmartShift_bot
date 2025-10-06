# 🚀 Deploy Cross-Chain Swap Bot to Render (FREE)

## ✅ **Your Bot is Ready!**

Your Cross-Chain Swap Bot is now prepared for Render deployment with all the necessary files:

- ✅ **render.yaml** - Render configuration
- ✅ **requirements.txt** - Python dependencies  
- ✅ **run_bot.py** - Main bot script
- ✅ **All core files** - Complete bot implementation

---

## 🎯 **Deployment Steps**

### **Step 1: Create GitHub Repository**
1. Go to [GitHub.com](https://github.com) and sign in
2. Click "New repository"
3. Name it: `cross-chain-swap-bot`
4. Make it **Public** (required for free Render)
5. Click "Create repository"

### **Step 2: Push Your Code**
```bash
# Add your GitHub repo as remote
git remote add origin https://github.com/YOUR_USERNAME/cross-chain-swap-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### **Step 3: Deploy on Render**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Select your `cross-chain-swap-bot` repo
6. Configure:
   - **Name**: `swap-bot`
   - **Type**: **Worker** (not Web Service)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run_bot.py`

### **Step 4: Set Environment Variables**
In Render dashboard, add these environment variables:
- `TELEGRAM_BOT_TOKEN`: `8212859489:AAFoxOz6XPo6LC929jV6BK9b_EpZa8bfooU`
- `SIDESHIFT_SECRET`: `a737abacea8b7a78e3aa0ef0f85acd8d`
- `SIDESHIFT_AFFILIATE_ID`: `ouG3iiiisS`
- `COMMISSION_RATE`: `0.005`

### **Step 5: Deploy!**
Click "Create Web Service" and Render will:
- Install dependencies
- Start your bot
- Keep it running 24/7

---

## 🎉 **After Deployment**

Your bot will be live at: `@SSmartSbot`

**Test it by:**
1. Opening Telegram
2. Searching for `@SSmartSbot`
3. Sending `/start`

---

## 📊 **Render Free Tier Benefits**

- ✅ **750 hours/month** (31 days = 744 hours)
- ✅ **Always running** (no sleep)
- ✅ **Automatic restarts** if it crashes
- ✅ **Logs and monitoring**
- ✅ **Zero cost** forever!

---

## 🔧 **Troubleshooting**

### **If deployment fails:**
1. Check logs in Render dashboard
2. Verify environment variables are set
3. Make sure all files are pushed to GitHub

### **If bot doesn't respond:**
1. Check Render logs
2. Verify Telegram token is correct
3. Restart the service in Render

---

## 🎯 **Next Steps**

1. **Deploy now** following the steps above
2. **Test thoroughly** with small amounts
3. **Monitor performance** in Render dashboard
4. **Scale up** if needed (upgrade to paid plan)

Your Cross-Chain Swap Bot is production-ready! 🚀
