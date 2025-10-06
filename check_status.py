"""
Check the status of the running bot.
"""

import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_bot_status():
    """Check if the bot is running and responding"""
    bot_token = "8212859489:AAFoxOz6XPo6LC929jV6BK9b_EpZa8bfooU"
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Get bot info
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        bot_info = data.get('result', {})
                        print("🤖 Bot Status: ✅ ACTIVE")
                        print(f"📛 Bot Name: {bot_info.get('first_name')}")
                        print(f"👤 Username: @{bot_info.get('username')}")
                        print(f"🆔 Bot ID: {bot_info.get('id')}")
                        print(f"✅ Can Join Groups: {bot_info.get('can_join_groups', False)}")
                        print(f"✅ Can Read All Group Messages: {bot_info.get('can_read_all_group_messages', False)}")
                        print(f"✅ Supports Inline Queries: {bot_info.get('supports_inline_queries', False)}")
                        print("\n🚀 Your Cross-Chain Swap Bot is ready!")
                        print("📱 Search for @SSmartSbot on Telegram to start using it!")
                        return True
                    else:
                        print(f"❌ Bot API Error: {data}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(check_bot_status())
