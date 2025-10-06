"""
Monitoring module for tracking swap statuses, price alerts, and automated notifications.
Handles background tasks for monitoring active swaps and sending alerts.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiohttp

from sideshift_api import SideShiftAPI
from database import SwapDatabase

logger = logging.getLogger(__name__)

class SwapMonitor:
    """Monitor active swaps and handle status updates"""
    
    def __init__(self, sideshift_api: SideShiftAPI, database: SwapDatabase, 
                 bot_application=None, check_interval: int = 60):
        self.api = sideshift_api
        self.db = database
        self.bot_app = bot_application
        self.check_interval = check_interval
        self.running = False
        self.monitor_task = None
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        if self.running:
            logger.warning("Monitoring is already running")
            return
        
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Swap monitoring started")
    
    async def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Swap monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await self._check_active_swaps()
                await self._check_price_alerts()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_active_swaps(self):
        """Check status of all active swaps"""
        active_swaps = await self.db.get_active_swaps()
        
        if not active_swaps:
            return
        
        logger.info(f"Checking {len(active_swaps)} active swaps")
        
        for swap in active_swaps:
            try:
                await self._update_swap_status(swap)
            except Exception as e:
                logger.error(f"Error updating swap {swap['shift_id']}: {e}")
    
    async def _update_swap_status(self, swap: Dict):
        """Update individual swap status"""
        shift_id = swap['shift_id']
        
        async with self.api as api:
            shift_data = await api.get_shift_status(shift_id)
        
        if not shift_data or "error" in shift_data:
            logger.error(f"Failed to get status for shift {shift_id}")
            return
        
        old_status = swap['status']
        new_status = shift_data['status']
        
        if old_status != new_status:
            logger.info(f"Status change for {shift_id}: {old_status} → {new_status}")
            
            # Update database
            await self.db.update_swap_status(
                shift_id=shift_id,
                status=new_status,
                deposit_hash=shift_data.get('depositHash'),
                settle_hash=shift_data.get('settleHash'),
                error_message=shift_data.get('errorMessage')
            )
            
            # Send notification to user
            await self._notify_user_status_change(swap, new_status, shift_data)
    
    async def _notify_user_status_change(self, swap: Dict, new_status: str, shift_data: Dict):
        """Send notification to user about status change"""
        if not self.bot_app:
            return
        
        user_id = swap['user_id']
        status_emojis = {
            "pending": "🔄",
            "processing": "⚙️",
            "settling": "📤",
            "settled": "✅",
            "refund": "🔙",
            "refunded": "✅",
            "expired": "❌"
        }
        
        emoji = status_emojis.get(new_status, "📊")
        status_text = f"{emoji} Status: {new_status.upper()}"
        
        message = (
            f"*Swap Status Update*\n\n"
            f"🆔 Shift ID: `{swap['shift_id']}`\n"
            f"💱 Pair: {swap['deposit_coin']} → {swap['settle_coin']}\n"
            f"{status_text}\n"
        )
        
        if new_status == "settled":
            message += f"🎉 *Swap completed successfully!*\n"
            if shift_data.get('settleHash'):
                message += f"🔗 Settlement TX: `{shift_data['settleHash'][:16]}...`\n"
        
        elif new_status == "refunded":
            message += f"💰 *Refund processed*\n"
            if shift_data.get('refundHash'):
                message += f"🔗 Refund TX: `{shift_data['refundHash'][:16]}...`\n"
        
        elif new_status == "expired":
            message += f"⏰ *Swap expired*\n"
        
        try:
            await self.bot_app.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")
    
    async def _check_price_alerts(self):
        """Check price alerts and send notifications"""
        alerts = await self.db.get_active_alerts()
        
        if not alerts:
            return
        
        logger.info(f"Checking {len(alerts)} price alerts")
        
        for alert in alerts:
            try:
                await self._check_single_alert(alert)
            except Exception as e:
                logger.error(f"Error checking alert {alert['id']}: {e}")
    
    async def _check_single_alert(self, alert: Dict):
        """Check individual price alert"""
        from_coin = alert['from_coin']
        from_network = alert['from_network']
        to_coin = alert['to_coin']
        to_network = alert['to_network']
        target_rate = alert['target_rate']
        alert_type = alert['alert_type']
        
        # Get current rate
        async with self.api as api:
            pair_info = await api.get_pair_info(
                f"{from_coin}-{from_network}",
                f"{to_coin}-{to_network}"
            )
        
        if "error" in pair_info or "rate" not in pair_info:
            logger.error(f"Failed to get rate for {from_coin}-{to_coin}")
            return
        
        current_rate = float(pair_info['rate'])
        triggered = False
        
        if alert_type == "above" and current_rate >= target_rate:
            triggered = True
        elif alert_type == "below" and current_rate <= target_rate:
            triggered = True
        
        if triggered:
            await self._trigger_price_alert(alert, current_rate)
    
    async def _trigger_price_alert(self, alert: Dict, current_rate: float):
        """Trigger price alert notification"""
        user_id = alert['user_id']
        from_coin = alert['from_coin']
        to_coin = alert['to_coin']
        target_rate = alert['target_rate']
        alert_type = alert['alert_type']
        
        # Deactivate alert
        await self.db.deactivate_alert(alert['id'])
        
        # Send notification
        if not self.bot_app:
            return
        
        message = (
            f"🚨 *Price Alert Triggered!*\n\n"
            f"💱 Pair: {from_coin} → {to_coin}\n"
            f"📊 Current Rate: {current_rate:.6f}\n"
            f"🎯 Target Rate: {target_rate:.6f} ({alert_type})\n\n"
            f"Use /swap to start a trade!"
        )
        
        try:
            await self.bot_app.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send price alert to user {user_id}: {e}")

class PriceTracker:
    """Track price changes and save to database"""
    
    def __init__(self, sideshift_api: SideShiftAPI, database: SwapDatabase, 
                 track_interval: int = 300):
        self.api = sideshift_api
        self.db = database
        self.track_interval = track_interval
        self.running = False
        self.track_task = None
        self.tracked_pairs = set()
    
    async def start_tracking(self):
        """Start price tracking"""
        if self.running:
            logger.warning("Price tracking is already running")
            return
        
        self.running = True
        self.track_task = asyncio.create_task(self._track_loop())
        logger.info("Price tracking started")
    
    async def stop_tracking(self):
        """Stop price tracking"""
        self.running = False
        if self.track_task:
            self.track_task.cancel()
            try:
                await self.track_task
            except asyncio.CancelledError:
                pass
        logger.info("Price tracking stopped")
    
    async def add_tracked_pair(self, from_coin: str, from_network: str, 
                              to_coin: str, to_network: str):
        """Add a pair to track"""
        pair_key = f"{from_coin}-{from_network}-{to_coin}-{to_network}"
        self.tracked_pairs.add(pair_key)
        logger.info(f"Added pair to tracking: {pair_key}")
    
    async def _track_loop(self):
        """Main tracking loop"""
        while self.running:
            try:
                await self._track_prices()
                await asyncio.sleep(self.track_interval)
            except Exception as e:
                logger.error(f"Error in price tracking loop: {e}")
                await asyncio.sleep(self.track_interval)
    
    async def _track_prices(self):
        """Track prices for all monitored pairs"""
        if not self.tracked_pairs:
            return
        
        logger.info(f"Tracking prices for {len(self.tracked_pairs)} pairs")
        
        for pair_key in self.tracked_pairs:
            try:
                from_coin, from_network, to_coin, to_network = pair_key.split('-')
                await self._track_single_pair(from_coin, from_network, to_coin, to_network)
            except Exception as e:
                logger.error(f"Error tracking pair {pair_key}: {e}")
    
    async def _track_single_pair(self, from_coin: str, from_network: str,
                                to_coin: str, to_network: str):
        """Track price for a single pair"""
        async with self.api as api:
            pair_info = await api.get_pair_info(
                f"{from_coin}-{from_network}",
                f"{to_coin}-{to_network}"
            )
        
        if "error" not in pair_info and "rate" in pair_info:
            rate = float(pair_info['rate'])
            await self.db.save_rate_history(
                from_coin, from_network, to_coin, to_network, rate
            )

class NotificationManager:
    """Manage different types of notifications"""
    
    def __init__(self, bot_application=None):
        self.bot_app = bot_application
    
    async def send_swap_notification(self, user_id: int, message: str):
        """Send swap-related notification"""
        if not self.bot_app:
            return
        
        try:
            await self.bot_app.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")
    
    async def send_admin_notification(self, message: str):
        """Send notification to admin users"""
        # Implement admin notification logic
        pass
    
    async def send_broadcast_message(self, message: str, user_ids: List[int] = None):
        """Send broadcast message to multiple users"""
        if not self.bot_app or not user_ids:
            return
        
        for user_id in user_ids:
            try:
                await self.bot_app.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
                await asyncio.sleep(0.1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to send broadcast to user {user_id}: {e}")

class HealthChecker:
    """Check system health and API status"""
    
    def __init__(self, sideshift_api: SideShiftAPI, database: SwapDatabase):
        self.api = sideshift_api
        self.db = database
        self.last_health_check = None
    
    async def check_health(self) -> Dict:
        """Perform comprehensive health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "api_status": "unknown",
            "database_status": "unknown",
            "active_swaps": 0,
            "errors": []
        }
        
        # Check API status
        try:
            async with self.api as api:
                account_info = await api.get_account_info()
            if "error" not in account_info:
                health_status["api_status"] = "healthy"
            else:
                health_status["api_status"] = "error"
                health_status["errors"].append(f"API error: {account_info.get('error')}")
        except Exception as e:
            health_status["api_status"] = "error"
            health_status["errors"].append(f"API exception: {e}")
        
        # Check database status
        try:
            active_swaps = await self.db.get_active_swaps()
            health_status["database_status"] = "healthy"
            health_status["active_swaps"] = len(active_swaps)
        except Exception as e:
            health_status["database_status"] = "error"
            health_status["errors"].append(f"Database error: {e}")
        
        self.last_health_check = health_status
        return health_status
    
    async def is_healthy(self) -> bool:
        """Check if system is healthy"""
        health = await self.check_health()
        return (health["api_status"] == "healthy" and 
                health["database_status"] == "healthy")
