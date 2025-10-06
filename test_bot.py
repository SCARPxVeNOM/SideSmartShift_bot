"""
Test script to verify the bot is working.
"""

import asyncio
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot():
    """Test if the bot is responding"""
    bot_token = "8212859489:AAFoxOz6XPo6LC929jV6BK9b_EpZa8bfooU"
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Test bot info
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        bot_info = data.get('result', {})
                        logger.info(f"Bot is working! Bot name: {bot_info.get('first_name')}")
                        logger.info(f"Bot username: @{bot_info.get('username')}")
                        logger.info(f"Bot ID: {bot_info.get('id')}")
                        return True
                    else:
                        logger.error(f"Bot API error: {data}")
                        return False
                else:
                    logger.error(f"HTTP error: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Error testing bot: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bot())
