"""
Configuration management for the Cross-Chain Swap Bot.
Handles environment variables, default values, and configuration validation.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class BotConfig:
    """Bot configuration class"""
    
    # Required configuration
    telegram_bot_token: str
    sideshift_secret: str
    sideshift_affiliate_id: str
    
    # Optional configuration with defaults
    commission_rate: float = 0.005
    database_path: str = "swap_bot.db"
    monitor_interval: int = 60
    track_interval: int = 300
    health_check_interval: int = 300
    log_level: str = "INFO"
    
    # API configuration
    api_timeout: int = 30
    max_retries: int = 3
    rate_limit_delay: float = 1.0
    
    # Database configuration
    db_cleanup_days: int = 30
    max_session_age_hours: int = 24
    
    # Monitoring configuration
    max_active_swaps_check: int = 100
    price_alert_cooldown_minutes: int = 5
    
    # Security configuration
    max_swap_amount: float = 10000.0
    min_swap_amount: float = 0.001
    address_validation_enabled: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values"""
        # Validate required fields
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.sideshift_secret:
            raise ValueError("SIDESHIFT_SECRET is required")
        if not self.sideshift_affiliate_id:
            raise ValueError("SIDESHIFT_AFFILIATE_ID is required")
        
        # Validate numeric ranges
        if not 0.0 <= self.commission_rate <= 0.02:
            raise ValueError("COMMISSION_RATE must be between 0.0 and 0.02")
        
        if self.monitor_interval < 10:
            raise ValueError("MONITOR_INTERVAL must be at least 10 seconds")
        
        if self.track_interval < 60:
            raise ValueError("TRACK_INTERVAL must be at least 60 seconds")
        
        if self.max_swap_amount <= self.min_swap_amount:
            raise ValueError("MAX_SWAP_AMOUNT must be greater than MIN_SWAP_AMOUNT")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_log_levels}")

def load_config() -> BotConfig:
    """Load configuration from environment variables"""
    try:
        config = BotConfig(
            # Required configuration
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            sideshift_secret=os.getenv("SIDESHIFT_SECRET", ""),
            sideshift_affiliate_id=os.getenv("SIDESHIFT_AFFILIATE_ID", ""),
            
            # Optional configuration
            commission_rate=float(os.getenv("COMMISSION_RATE", "0.005")),
            database_path=os.getenv("DATABASE_PATH", "swap_bot.db"),
            monitor_interval=int(os.getenv("MONITOR_INTERVAL", "60")),
            track_interval=int(os.getenv("TRACK_INTERVAL", "300")),
            health_check_interval=int(os.getenv("HEALTH_CHECK_INTERVAL", "300")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            
            # API configuration
            api_timeout=int(os.getenv("API_TIMEOUT", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            rate_limit_delay=float(os.getenv("RATE_LIMIT_DELAY", "1.0")),
            
            # Database configuration
            db_cleanup_days=int(os.getenv("DB_CLEANUP_DAYS", "30")),
            max_session_age_hours=int(os.getenv("MAX_SESSION_AGE_HOURS", "24")),
            
            # Monitoring configuration
            max_active_swaps_check=int(os.getenv("MAX_ACTIVE_SWAPS_CHECK", "100")),
            price_alert_cooldown_minutes=int(os.getenv("PRICE_ALERT_COOLDOWN_MINUTES", "5")),
            
            # Security configuration
            max_swap_amount=float(os.getenv("MAX_SWAP_AMOUNT", "10000.0")),
            min_swap_amount=float(os.getenv("MIN_SWAP_AMOUNT", "0.001")),
            address_validation_enabled=os.getenv("ADDRESS_VALIDATION_ENABLED", "true").lower() == "true"
        )
        
        logger.info("Configuration loaded successfully")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def get_database_url(config: BotConfig) -> str:
    """Get database URL from configuration"""
    return f"sqlite:///{config.database_path}"

def get_logging_config(config: BotConfig) -> Dict[str, Any]:
    """Get logging configuration"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": config.log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": config.log_level,
                "formatter": "detailed",
                "filename": "swap_bot.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {
                "level": config.log_level,
                "handlers": ["console", "file"],
                "propagate": False
            }
        }
    }

def validate_environment() -> bool:
    """Validate that all required environment variables are set"""
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "SIDESHIFT_SECRET",
        "SIDESHIFT_AFFILIATE_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    return True

def print_config_summary(config: BotConfig):
    """Print configuration summary (without sensitive data)"""
    logger.info("Configuration Summary:")
    logger.info(f"  Database: {config.database_path}")
    logger.info(f"  Commission Rate: {config.commission_rate:.1%}")
    logger.info(f"  Monitor Interval: {config.monitor_interval}s")
    logger.info(f"  Track Interval: {config.track_interval}s")
    logger.info(f"  Log Level: {config.log_level}")
    logger.info(f"  Max Swap Amount: {config.max_swap_amount}")
    logger.info(f"  Min Swap Amount: {config.min_swap_amount}")

# Global configuration instance
_config: Optional[BotConfig] = None

def get_config() -> BotConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config

def reload_config() -> BotConfig:
    """Reload configuration from environment"""
    global _config
    _config = load_config()
    return _config
