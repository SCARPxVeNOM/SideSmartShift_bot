# Deploy Cross-Chain Swap Bot on Render (FREE)

## Prerequisites
- GitHub account
- Render account (free)

## Steps

### 1. Prepare for Render
Create `render.yaml`:

```yaml
services:
  - type: worker
    name: swap-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python run_bot.py
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        value: 8212859489:AAFoxOz6XPo6LC929jV6BK9b_EpZa8bfooU
      - key: SIDESHIFT_SECRET
        value: a737abacea8b7a78e3aa0ef0f85acd8d
      - key: SIDESHIFT_AFFILIATE_ID
        value: ouG3iiiisS
      - key: COMMISSION_RATE
        value: 0.005
```

### 2. Deploy
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Select "Worker" type
6. Deploy!

## Cost: FREE
- 750 hours/month free
- Sleeps after 15 min of inactivity
- Perfect for bots!
