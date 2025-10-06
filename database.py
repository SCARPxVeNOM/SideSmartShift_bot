"""
Database module for storing swap history, user data, and price alerts.
Uses SQLite for data persistence with proper indexing and relationships.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import asyncio
import aiosqlite

logger = logging.getLogger(__name__)

class SwapDatabase:
    """Handle database operations for swap history and user data"""
    
    def __init__(self, db_path: str = "swap_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_swaps INTEGER DEFAULT 0,
                    total_volume_usd REAL DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    language_code TEXT DEFAULT 'en',
                    timezone TEXT DEFAULT 'UTC'
                )
            """)
            
            # Swaps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS swaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    shift_id TEXT UNIQUE,
                    swap_type TEXT,
                    deposit_coin TEXT,
                    deposit_network TEXT,
                    settle_coin TEXT,
                    settle_network TEXT,
                    deposit_amount TEXT,
                    settle_amount TEXT,
                    rate TEXT,
                    status TEXT,
                    deposit_address TEXT,
                    deposit_memo TEXT,
                    settle_address TEXT,
                    refund_address TEXT,
                    refund_memo TEXT,
                    deposit_hash TEXT,
                    settle_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    commission_earned REAL DEFAULT 0,
                    error_message TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Price alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    from_coin TEXT,
                    from_network TEXT,
                    to_coin TEXT,
                    to_network TEXT,
                    target_rate REAL,
                    alert_type TEXT, -- 'above' or 'below'
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_at TIMESTAMP,
                    message_sent BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # User sessions table (for state management)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id INTEGER PRIMARY KEY,
                    state TEXT DEFAULT 'idle',
                    swap_type TEXT,
                    deposit_coin TEXT,
                    deposit_network TEXT,
                    settle_coin TEXT,
                    settle_network TEXT,
                    deposit_amount TEXT,
                    settle_address TEXT,
                    refund_address TEXT,
                    quote_id TEXT,
                    shift_id TEXT,
                    session_data TEXT, -- JSON for additional data
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Rate history table (for tracking price changes)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rate_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_coin TEXT,
                    from_network TEXT,
                    to_coin TEXT,
                    to_network TEXT,
                    rate REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_swaps_user_id ON swaps(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_swaps_shift_id ON swaps(shift_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_swaps_status ON swaps(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_swaps_created_at ON swaps(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON price_alerts(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_active ON price_alerts(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_history_timestamp ON rate_history(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_history_pair ON rate_history(from_coin, to_coin)")
            
            conn.commit()
    
    async def add_user(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None,
                      language_code: str = 'en') -> bool:
        """Add or update user"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, language_code, last_seen) 
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (user_id, username, first_name, last_name, language_code))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    async def update_user_activity(self, user_id: int) -> bool:
        """Update user's last seen timestamp"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    UPDATE users SET last_seen = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                """, (user_id,))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
            return False
    
    async def save_swap(self, user_id: int, shift_data: Dict) -> bool:
        """Save swap transaction"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT OR REPLACE INTO swaps 
                    (user_id, shift_id, swap_type, deposit_coin, deposit_network,
                     settle_coin, settle_network, deposit_amount, settle_amount,
                     rate, status, deposit_address, deposit_memo, settle_address, 
                     refund_address, refund_memo, expires_at, commission_earned)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    shift_data.get('id'),
                    shift_data.get('type'),
                    shift_data.get('depositCoin'),
                    shift_data.get('depositNetwork'),
                    shift_data.get('settleCoin'),
                    shift_data.get('settleNetwork'),
                    shift_data.get('depositAmount'),
                    shift_data.get('settleAmount'),
                    shift_data.get('rate'),
                    shift_data.get('status', 'waiting'),
                    shift_data.get('depositAddress'),
                    shift_data.get('depositMemo'),
                    shift_data.get('settleAddress'),
                    shift_data.get('refundAddress'),
                    shift_data.get('refundMemo'),
                    shift_data.get('expiresAt'),
                    shift_data.get('commissionEarned', 0)
                ))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving swap: {e}")
            return False
    
    async def update_swap_status(self, shift_id: str, status: str, 
                                deposit_hash: str = None, settle_hash: str = None,
                                error_message: str = None) -> bool:
        """Update swap status"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    UPDATE swaps 
                    SET status = ?, deposit_hash = ?, settle_hash = ?, 
                        error_message = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE shift_id = ?
                """, (status, deposit_hash, settle_hash, error_message, shift_id))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating swap status: {e}")
            return False
    
    async def get_user_swaps(self, user_id: int, limit: int = 10, 
                           status_filter: str = None) -> List[Dict]:
        """Get user's swap history"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.cursor()
                
                query = """
                    SELECT * FROM swaps 
                    WHERE user_id = ?
                """
                params = [user_id]
                
                if status_filter:
                    query += " AND status = ?"
                    params.append(status_filter)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                await cursor.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user swaps: {e}")
            return []
    
    async def get_active_swaps(self) -> List[Dict]:
        """Get all active swaps for monitoring"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.cursor()
                await cursor.execute("""
                    SELECT s.*, u.username, u.first_name 
                    FROM swaps s
                    JOIN users u ON s.user_id = u.user_id
                    WHERE s.status IN ('waiting', 'pending', 'processing', 'settling')
                    ORDER BY s.created_at DESC
                """)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting active swaps: {e}")
            return []
    
    async def get_swap_by_shift_id(self, shift_id: str) -> Optional[Dict]:
        """Get specific swap by shift ID"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.cursor()
                await cursor.execute("""
                    SELECT * FROM swaps WHERE shift_id = ?
                """, (shift_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting swap by shift ID: {e}")
            return None
    
    async def save_user_session(self, user_id: int, session_data: Dict) -> bool:
        """Save user session state"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT OR REPLACE INTO user_sessions 
                    (user_id, state, swap_type, deposit_coin, deposit_network,
                     settle_coin, settle_network, deposit_amount, settle_address,
                     refund_address, quote_id, shift_id, session_data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    user_id,
                    session_data.get('state', 'idle'),
                    session_data.get('swap_type'),
                    session_data.get('deposit_coin'),
                    session_data.get('deposit_network'),
                    session_data.get('settle_coin'),
                    session_data.get('settle_network'),
                    session_data.get('deposit_amount'),
                    session_data.get('settle_address'),
                    session_data.get('refund_address'),
                    session_data.get('quote_id'),
                    session_data.get('shift_id'),
                    json.dumps(session_data.get('additional_data', {}))
                ))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving user session: {e}")
            return False
    
    async def get_user_session(self, user_id: int) -> Optional[Dict]:
        """Get user session state"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.cursor()
                await cursor.execute("""
                    SELECT * FROM user_sessions WHERE user_id = ?
                """, (user_id,))
                row = await cursor.fetchone()
                
                if row:
                    session_data = dict(row)
                    # Parse additional data JSON
                    try:
                        session_data['additional_data'] = json.loads(session_data.get('session_data', '{}'))
                    except json.JSONDecodeError:
                        session_data['additional_data'] = {}
                    return session_data
                return None
        except Exception as e:
            logger.error(f"Error getting user session: {e}")
            return None
    
    async def clear_user_session(self, user_id: int) -> bool:
        """Clear user session"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    DELETE FROM user_sessions WHERE user_id = ?
                """, (user_id,))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error clearing user session: {e}")
            return False
    
    async def add_price_alert(self, user_id: int, from_coin: str, from_network: str,
                             to_coin: str, to_network: str, target_rate: float, 
                             alert_type: str) -> bool:
        """Add price alert"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT INTO price_alerts 
                    (user_id, from_coin, from_network, to_coin, to_network, 
                     target_rate, alert_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, from_coin, from_network, to_coin, to_network, 
                      target_rate, alert_type))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding price alert: {e}")
            return False
    
    async def get_user_alerts(self, user_id: int) -> List[Dict]:
        """Get user's price alerts"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.cursor()
                await cursor.execute("""
                    SELECT * FROM price_alerts 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY created_at DESC
                """, (user_id,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            return []
    
    async def get_active_alerts(self) -> List[Dict]:
        """Get all active price alerts"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.cursor()
                await cursor.execute("""
                    SELECT * FROM price_alerts 
                    WHERE is_active = 1
                """)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def deactivate_alert(self, alert_id: int) -> bool:
        """Deactivate a triggered alert"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    UPDATE price_alerts 
                    SET is_active = 0, triggered_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (alert_id,))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deactivating alert: {e}")
            return False
    
    async def save_rate_history(self, from_coin: str, from_network: str,
                               to_coin: str, to_network: str, rate: float) -> bool:
        """Save rate history for tracking"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT INTO rate_history 
                    (from_coin, from_network, to_coin, to_network, rate)
                    VALUES (?, ?, ?, ?, ?)
                """, (from_coin, from_network, to_coin, to_network, rate))
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving rate history: {e}")
            return False
    
    async def get_rate_history(self, from_coin: str, to_coin: str, 
                              hours: int = 24) -> List[Dict]:
        """Get rate history for a pair"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.cursor()
                await cursor.execute("""
                    SELECT * FROM rate_history 
                    WHERE from_coin = ? AND to_coin = ? 
                    AND timestamp > datetime('now', '-{} hours')
                    ORDER BY timestamp DESC
                """.format(hours), (from_coin, to_coin))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting rate history: {e}")
            return []
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.cursor()
                
                # Get swap statistics
                await cursor.execute("""
                    SELECT 
                        COUNT(*) as total_swaps,
                        COUNT(CASE WHEN status = 'settled' THEN 1 END) as completed_swaps,
                        COUNT(CASE WHEN status IN ('waiting', 'pending', 'processing', 'settling') THEN 1 END) as active_swaps,
                        COUNT(CASE WHEN status = 'refunded' THEN 1 END) as refunded_swaps,
                        SUM(CASE WHEN status = 'settled' THEN CAST(deposit_amount AS REAL) ELSE 0 END) as total_volume
                    FROM swaps 
                    WHERE user_id = ?
                """, (user_id,))
                
                stats = dict(await cursor.fetchone())
                
                # Get recent swaps
                await cursor.execute("""
                    SELECT deposit_coin, settle_coin, status, created_at, deposit_amount, settle_amount
                    FROM swaps 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """, (user_id,))
                
                stats['recent_swaps'] = [dict(row) for row in await cursor.fetchall()]
                
                return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    async def get_bot_stats(self) -> Dict:
        """Get overall bot statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.cursor()
                
                # Get overall statistics
                await cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT user_id) as total_users,
                        COUNT(*) as total_swaps,
                        COUNT(CASE WHEN status = 'settled' THEN 1 END) as completed_swaps,
                        COUNT(CASE WHEN status IN ('waiting', 'pending', 'processing', 'settling') THEN 1 END) as active_swaps,
                        SUM(commission_earned) as total_commission
                    FROM swaps
                """)
                
                stats = dict(await cursor.fetchone())
                
                # Get top trading pairs
                await cursor.execute("""
                    SELECT 
                        deposit_coin || '-' || settle_coin as pair,
                        COUNT(*) as swap_count
                    FROM swaps 
                    WHERE status = 'settled'
                    GROUP BY deposit_coin, settle_coin
                    ORDER BY swap_count DESC
                    LIMIT 10
                """)
                
                stats['top_pairs'] = [dict(row) for row in await cursor.fetchall()]
                
                return stats
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            return {}
    
    async def cleanup_old_data(self, days: int = 30) -> bool:
        """Clean up old data to keep database size manageable"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                # Clean up old rate history
                await conn.execute("""
                    DELETE FROM rate_history 
                    WHERE timestamp < datetime('now', '-{} days')
                """.format(days))
                
                # Clean up old user sessions
                await conn.execute("""
                    DELETE FROM user_sessions 
                    WHERE updated_at < datetime('now', '-7 days')
                """)
                
                await conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False
