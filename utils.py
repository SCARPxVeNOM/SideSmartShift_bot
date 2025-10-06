"""
Utility functions for the Cross-Chain Swap Bot.
Common helper functions, validators, and formatters.
"""

import re
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import asyncio

logger = logging.getLogger(__name__)

class AddressValidator:
    """Cryptocurrency address validation utilities"""
    
    # Basic address patterns for common cryptocurrencies
    ADDRESS_PATTERNS = {
        'BTC': r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$',
        'ETH': r'^0x[a-fA-F0-9]{40}$',
        'LTC': r'^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$',
        'DOGE': r'^D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}$',
        'BCH': r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bitcoincash:[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{42}$',
        'XRP': r'^r[0-9a-zA-Z]{24,34}$',
        'ADA': r'^addr1[a-z0-9]{98}$',
        'DOT': r'^1[0-9a-zA-Z]{47}$',
        'SOL': r'^[1-9A-HJ-NP-Za-km-z]{32,44}$',
        'MATIC': r'^0x[a-fA-F0-9]{40}$',
        'AVAX': r'^0x[a-fA-F0-9]{40}$',
        'BNB': r'^0x[a-fA-F0-9]{40}$',
        'TRX': r'^T[A-Za-z1-9]{33}$',
    }
    
    @classmethod
    def validate_address(cls, address: str, coin: str) -> bool:
        """Validate cryptocurrency address format"""
        if not address or not coin:
            return False
        
        coin_upper = coin.upper()
        pattern = cls.ADDRESS_PATTERNS.get(coin_upper)
        
        if not pattern:
            # For unknown coins, do basic validation
            return len(address) >= 10 and len(address) <= 100
        
        return bool(re.match(pattern, address))
    
    @classmethod
    def validate_btc_address(cls, address: str) -> bool:
        """Validate Bitcoin address (legacy, segwit, bech32)"""
        if not address:
            return False
        
        # Legacy addresses (1...)
        if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return True
        
        # Bech32 addresses (bc1...)
        if re.match(r'^bc1[a-z0-9]{39,59}$', address):
            return True
        
        return False
    
    @classmethod
    def validate_eth_address(cls, address: str) -> bool:
        """Validate Ethereum address"""
        if not address:
            return False
        
        # Check format
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return False
        
        # Check if it's a valid checksum
        return cls._is_valid_eth_checksum(address)
    
    @classmethod
    def _is_valid_eth_checksum(cls, address: str) -> bool:
        """Validate Ethereum address checksum"""
        try:
            # Remove 0x prefix
            addr = address[2:].lower()
            
            # Calculate keccak256 hash
            hash_bytes = hashlib.sha3_256(addr.encode()).digest()
            hash_str = hash_bytes.hex()
            
            # Check each character
            for i, char in enumerate(addr):
                if char.isalpha():
                    if hash_str[i] >= '8' and address[i].isupper():
                        continue
                    elif hash_str[i] < '8' and address[i].islower():
                        continue
                    else:
                        return False
            
            return True
        except Exception:
            return False

class AmountValidator:
    """Amount validation utilities"""
    
    @staticmethod
    def validate_amount(amount_str: str, min_amount: float = 0.001, max_amount: float = 10000.0) -> Tuple[bool, Optional[float]]:
        """Validate swap amount"""
        try:
            amount = float(amount_str)
            
            if amount <= 0:
                return False, None
            
            if amount < min_amount:
                return False, None
            
            if amount > max_amount:
                return False, None
            
            return True, amount
            
        except (ValueError, TypeError):
            return False, None
    
    @staticmethod
    def format_amount(amount: float, precision: int = 8) -> str:
        """Format amount with appropriate precision"""
        if amount == 0:
            return "0"
        
        # Remove trailing zeros
        formatted = f"{amount:.{precision}f}".rstrip('0').rstrip('.')
        return formatted

class TimeFormatter:
    """Time formatting utilities"""
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    
    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            return timestamp
    
    @staticmethod
    def get_time_until_expiry(expires_at: str) -> str:
        """Get time until expiry"""
        try:
            expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            now = datetime.utcnow()
            
            if expires <= now:
                return "Expired"
            
            diff = expires - now
            return TimeFormatter.format_duration(int(diff.total_seconds()))
        except Exception:
            return "Unknown"

class TextFormatter:
    """Text formatting utilities"""
    
    @staticmethod
    def truncate_address(address: str, start_chars: int = 6, end_chars: int = 4) -> str:
        """Truncate address for display"""
        if len(address) <= start_chars + end_chars:
            return address
        
        return f"{address[:start_chars]}...{address[-end_chars:]}"
    
    @staticmethod
    def format_coin_pair(from_coin: str, to_coin: str) -> str:
        """Format coin pair for display"""
        return f"{from_coin.upper()}/{to_coin.upper()}"
    
    @staticmethod
    def format_swap_summary(swap: Dict[str, Any]) -> str:
        """Format swap summary for display"""
        status_emoji = {
            "waiting": "⏳",
            "pending": "🔄",
            "processing": "⚙️",
            "settling": "📤",
            "settled": "✅",
            "refunded": "🔙",
            "expired": "❌"
        }.get(swap.get('status', ''), '❓')
        
        return (
            f"{status_emoji} {swap.get('deposit_coin', 'N/A')} → "
            f"{swap.get('settle_coin', 'N/A')} ({swap.get('status', 'unknown')})"
        )
    
    @staticmethod
    def format_rate(rate: float, precision: int = 6) -> str:
        """Format exchange rate"""
        if rate == 0:
            return "0"
        
        # Use scientific notation for very small rates
        if rate < 0.000001:
            return f"{rate:.2e}"
        
        return f"{rate:.{precision}f}".rstrip('0').rstrip('.')

class RateCalculator:
    """Rate calculation utilities"""
    
    @staticmethod
    def calculate_commission(amount: float, commission_rate: float) -> float:
        """Calculate commission amount"""
        return amount * commission_rate
    
    @staticmethod
    def calculate_net_amount(amount: float, commission_rate: float) -> float:
        """Calculate net amount after commission"""
        return amount * (1 - commission_rate)
    
    @staticmethod
    def calculate_slippage(expected_rate: float, actual_rate: float) -> float:
        """Calculate slippage percentage"""
        if expected_rate == 0:
            return 0
        
        return abs((actual_rate - expected_rate) / expected_rate) * 100

class RetryHandler:
    """Retry mechanism for API calls"""
    
    @staticmethod
    async def retry_async(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """Retry async function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = delay * (backoff ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
    
    @staticmethod
    def retry_sync(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """Retry sync function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = delay * (backoff ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                import time
                time.sleep(wait_time)

class ErrorHandler:
    """Error handling utilities"""
    
    @staticmethod
    def format_api_error(error: Dict[str, Any]) -> str:
        """Format API error for user display"""
        if isinstance(error, dict):
            message = error.get('message', 'Unknown error')
            code = error.get('code', '')
            
            if code:
                return f"{message} (Code: {code})"
            return message
        
        return str(error)
    
    @staticmethod
    def is_retryable_error(error: Exception) -> bool:
        """Check if error is retryable"""
        retryable_errors = (
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
            aiohttp.ClientError
        )
        
        return isinstance(error, retryable_errors)
    
    @staticmethod
    def log_error(error: Exception, context: str = ""):
        """Log error with context"""
        logger.error(f"Error in {context}: {error}", exc_info=True)

class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_swap_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate swap data"""
        errors = []
        
        required_fields = ['deposit_coin', 'deposit_network', 'settle_coin', 'settle_network']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate amounts
        if 'deposit_amount' in data and data['deposit_amount']:
            try:
                amount = float(data['deposit_amount'])
                if amount <= 0:
                    errors.append("Deposit amount must be positive")
            except (ValueError, TypeError):
                errors.append("Invalid deposit amount format")
        
        # Validate addresses
        if 'settle_address' in data and data['settle_address']:
            if not AddressValidator.validate_address(
                data['settle_address'], 
                data.get('settle_coin', '')
            ):
                errors.append("Invalid settle address format")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        return sanitized[:1000]

class CacheManager:
    """Simple cache management"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check if expired
        if datetime.now().timestamp() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        self.cache[key] = value
        self.timestamps[key] = datetime.now().timestamp()
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.timestamps.clear()
    
    def cleanup_expired(self):
        """Remove expired entries"""
        now = datetime.now().timestamp()
        expired_keys = [
            key for key, timestamp in self.timestamps.items()
            if now - timestamp > self.ttl
        ]
        
        for key in expired_keys:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
