"""
Main entry point for the Cross-Chain Swap Bot.
Handles application startup, monitoring, and graceful shutdown.
"""

import os
import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from telegram.ext import Application

from sideshift_api import SideShiftAPI
from database import SwapDatabase
from swap_bot import SwapBot
from monitor import SwapMonitor, PriceTracker, HealthChecker

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('swap_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SwapBotApplication:
    """Main application class"""
    
    def __init__(self):
        self.app: Optional[Application] = None
        self.swap_bot: Optional[SwapBot] = None
        self.monitor: Optional[SwapMonitor] = None
        self.price_tracker: Optional[PriceTracker] = None
        self.health_checker: Optional[HealthChecker] = None
        self.running = False
    
    async def initialize(self):
        """Initialize all components"""
        try:
            # Load configuration
            config = self._load_config()
            
            # Initialize API and database
            sideshift_api = SideShiftAPI(
                secret=config['SIDESHIFT_SECRET'],
                affiliate_id=config['SIDESHIFT_AFFILIATE_ID'],
                commission_rate=config['COMMISSION_RATE']
            )
            
            database = SwapDatabase(config['DATABASE_PATH'])
            
            # Initialize bot
            self.swap_bot = SwapBot(sideshift_api, database)
            
            # Initialize monitoring
            self.monitor = SwapMonitor(sideshift_api, database, check_interval=config['MONITOR_INTERVAL'])
            self.price_tracker = PriceTracker(sideshift_api, database, track_interval=config['TRACK_INTERVAL'])
            self.health_checker = HealthChecker(sideshift_api, database)
            
            # Create Telegram application
            self.app = Application.builder().token(config['TELEGRAM_BOT_TOKEN']).build()
            self.app.bot_data['swap_bot'] = self.swap_bot
            
            # Set up monitoring with bot reference
            self.monitor.bot_app = self.app
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            return False
    
    def _load_config(self) -> dict:
        """Load configuration from environment variables"""
        config = {
            'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
            'SIDESHIFT_SECRET': os.getenv('SIDESHIFT_SECRET'),
            'SIDESHIFT_AFFILIATE_ID': os.getenv('SIDESHIFT_AFFILIATE_ID'),
            'COMMISSION_RATE': float(os.getenv('COMMISSION_RATE', '0.005')),
            'DATABASE_PATH': os.getenv('DATABASE_PATH', 'swap_bot.db'),
            'MONITOR_INTERVAL': int(os.getenv('MONITOR_INTERVAL', '60')),
            'TRACK_INTERVAL': int(os.getenv('TRACK_INTERVAL', '300')),
            'HEALTH_CHECK_INTERVAL': int(os.getenv('HEALTH_CHECK_INTERVAL', '300')),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'MAX_SWAP_AMOUNT': float(os.getenv('MAX_SWAP_AMOUNT', '10000.0')),
            'MIN_SWAP_AMOUNT': float(os.getenv('MIN_SWAP_AMOUNT', '0.001')),
            'ADDRESS_VALIDATION_ENABLED': os.getenv('ADDRESS_VALIDATION_ENABLED', 'true').lower() == 'true'
        }
        
        # Validate required environment variables
        required_vars = ['TELEGRAM_BOT_TOKEN', 'SIDESHIFT_SECRET', 'SIDESHIFT_AFFILIATE_ID']
        missing_vars = [var for var in required_vars if not config[var]]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return config
    
    async def start(self):
        """Start the application"""
        if not await self.initialize():
            logger.error("Failed to initialize application")
            return False
        
        try:
            # Start monitoring
            await self.monitor.start_monitoring()
            await self.price_tracker.start_tracking()
            
            # Start health checking
            asyncio.create_task(self._health_check_loop())
            
            # Start Telegram bot
            logger.info("Starting Telegram bot...")
            self.running = True
            
            # Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Run the bot
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            
            # Keep running
            try:
                while self.running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
            
        except Exception as e:
            logger.error(f"Error starting application: {e}")
            return False
    
    async def stop(self):
        """Stop the application gracefully"""
        if not self.running:
            return
        
        logger.info("Stopping application...")
        self.running = False
        
        try:
            # Stop monitoring
            if self.monitor:
                await self.monitor.stop_monitoring()
            
            if self.price_tracker:
                await self.price_tracker.stop_tracking()
            
            # Stop Telegram bot
            if self.app:
                await self.app.updater.stop()
                await self.app.stop()
                await self.app.shutdown()
            
            logger.info("Application stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping application: {e}")
    
    async def _health_check_loop(self):
        """Periodic health check loop"""
        while self.running:
            try:
                health = await self.health_checker.check_health()
                
                if not await self.health_checker.is_healthy():
                    logger.warning(f"Health check failed: {health}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point"""
    app = SwapBotApplication()
    
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    # Set up proper event loop for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)
