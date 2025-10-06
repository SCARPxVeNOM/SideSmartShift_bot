"""
Simplified entry point for the Cross-Chain Swap Bot.
"""

import os
import asyncio
import logging
import sys
from datetime import datetime

from sideshift_api import SideShiftAPI
from database import SwapDatabase
from swap_bot import SwapBot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point"""
    try:
        # Hardcoded credentials
        TELEGRAM_TOKEN = "8212859489:AAFoxOz6XPo6LC929jV6BK9b_EpZa8bfooU"
        SIDESHIFT_SECRET = "a737abacea8b7a78e3aa0ef0f85acd8d"
        SIDESHIFT_AFFILIATE_ID = "ouG3iiiisS"
        COMMISSION_RATE = 0.005
        DATABASE_PATH = "swap_bot.db"
        
        logger.info("Initializing Cross-Chain Swap Bot...")
        
        # Initialize API and database
        sideshift_api = SideShiftAPI(SIDESHIFT_SECRET, SIDESHIFT_AFFILIATE_ID, COMMISSION_RATE)
        database = SwapDatabase(DATABASE_PATH)
        swap_bot = SwapBot(sideshift_api, database)
        
        # Create and run the bot
        from telegram.ext import Application
        
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        application.bot_data['swap_bot'] = swap_bot
        
        # Add handlers
        from swap_bot import (
            start, swap, handle_callback, handle_message, status, 
            history, rates, alerts, stats, cancel, help_command, error_handler
        )
        from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("swap", swap))
        application.add_handler(CommandHandler("status", status))
        application.add_handler(CommandHandler("history", history))
        application.add_handler(CommandHandler("rates", rates))
        application.add_handler(CommandHandler("alerts", alerts))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("cancel", cancel))
        application.add_handler(CommandHandler("help", help_command))
        
        # Add callback and message handlers
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        logger.info("Bot initialized successfully. Starting polling...")
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
        
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise

if __name__ == "__main__":
    # Set up proper event loop for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot failed: {e}")
        sys.exit(1)
