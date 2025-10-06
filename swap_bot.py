"""
Main Telegram bot implementation for cross-chain cryptocurrency swapping.
Handles user interactions, state management, and swap operations.
"""

import os
import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv

from sideshift_api import SideShiftAPI
from database import SwapDatabase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SwapBot:
    """Main bot logic for handling swap operations"""
    
    def __init__(self, sideshift_api: SideShiftAPI, database: SwapDatabase):
        self.api = sideshift_api
        self.db = database
        self.coins_cache = None
        self.cache_time = None
        self.user_sessions = {}  # In-memory session cache
    
    async def get_cached_coins(self) -> List[Dict]:
        """Get cached coins list (refresh every hour)"""
        if not self.coins_cache or (
            self.cache_time and datetime.now() - self.cache_time > timedelta(hours=1)
        ):
            async with self.api as api:
                self.coins_cache = await api.get_coins()
                self.cache_time = datetime.now()
        return self.coins_cache
    
    async def get_user_session(self, user_id: int) -> Dict:
        """Get or create user session"""
        # Try to get from database first
        session = await self.db.get_user_session(user_id)
        if not session:
            session = {
                "user_id": user_id,
                "state": "idle",
                "swap_type": None,
                "deposit_coin": None,
                "deposit_network": None,
                "settle_coin": None,
                "settle_network": None,
                "deposit_amount": None,
                "settle_address": None,
                "refund_address": None,
                "quote_id": None,
                "shift_id": None,
                "additional_data": {}
            }
        return session
    
    async def save_user_session(self, user_id: int, session: Dict):
        """Save user session to database"""
        await self.db.save_user_session(user_id, session)
    
    def format_coin_list(self, coins: List[Dict]) -> str:
        """Format coins for display"""
        unique_coins = set()
        for coin_data in coins:
            unique_coins.add(coin_data["coin"])
        
        sorted_coins = sorted(unique_coins)
        return "\n".join([f"• {coin}" for coin in sorted_coins[:20]])
    
    def get_networks_for_coin(self, coins: List[Dict], coin_symbol: str) -> List[str]:
        """Get available networks for a coin"""
        for coin_data in coins:
            if coin_data["coin"].upper() == coin_symbol.upper():
                return [network["name"] for network in coin_data["networks"]]
        return []
    
    def format_swap_status(self, status: str) -> str:
        """Format swap status with emoji"""
        status_emojis = {
            "waiting": "⏳ Waiting for deposit",
            "pending": "🔄 Deposit detected",
            "processing": "⚙️ Processing",
            "review": "👀 Under review",
            "settling": "📤 Settling",
            "settled": "✅ Completed",
            "refund": "🔙 Queued for refund",
            "refunding": "🔙 Refunding",
            "refunded": "✅ Refunded",
            "expired": "❌ Expired",
            "multiple": "📊 Multiple deposits"
        }
        return status_emojis.get(status, f"❓ {status}")
    
    async def validate_crypto_address(self, address: str, coin: str, network: str) -> bool:
        """Basic address validation"""
        if not address or len(address) < 10:
            return False
        
        # Add more specific validation based on coin/network
        # This is a basic implementation - enhance for production
        return True

# Bot command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    bot = context.bot_data.get('swap_bot')
    
    # Add user to database
    await bot.db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )
    
    welcome_msg = (
        "🔄 *Welcome to Cross-Chain Swap Bot!*\n\n"
        "I can help you swap cryptocurrencies across different blockchains using SideShift.ai\n\n"
        "📝 *Available Commands:*\n"
        "• /swap - Start a new swap\n"
        "• /status - Check swap status\n"
        "• /history - View swap history\n"
        "• /rates - Check exchange rates\n"
        "• /alerts - Manage price alerts\n"
        "• /stats - View your statistics\n"
        "• /help - Show help information\n"
        "• /cancel - Cancel current operation\n\n"
        "💡 Choose between Fixed Rate (15 min guarantee) or Variable Rate (7 days validity)\n\n"
        "⚠️ *Important:* Always verify addresses and amounts before confirming!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔄 Start Swap", callback_data="start_swap")],
        [InlineKeyboardButton("📊 Check Rates", callback_data="check_rates")],
        [InlineKeyboardButton("📈 My History", callback_data="view_history")],
        [InlineKeyboardButton("❓ Help", callback_data="show_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def swap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /swap command"""
    keyboard = [
        [
            InlineKeyboardButton("🔒 Fixed Rate", callback_data="swap_fixed"),
            InlineKeyboardButton("📊 Variable Rate", callback_data="swap_variable")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "*Choose swap type:*\n\n"
        "🔒 *Fixed Rate*: Rate locked for 15 minutes\n"
        "📊 *Variable Rate*: Market rate when deposit received",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks"""
    query = update.callback_query
    await query.answer()
    
    bot = context.bot_data.get('swap_bot')
    user_id = query.from_user.id
    session = await bot.get_user_session(user_id)
    
    # Handle main menu callbacks
    if query.data == "start_swap":
        await swap(update, context)
        return
    elif query.data == "check_rates":
        await rates(update, context)
        return
    elif query.data == "view_history":
        await history(update, context)
        return
    elif query.data == "show_help":
        await help_command(update, context)
        return
    
    # Handle swap type selection
    if query.data.startswith("swap_"):
        swap_type = query.data.split("_")[1]
        session["swap_type"] = swap_type
        session["state"] = "awaiting_deposit_coin"
        await bot.save_user_session(user_id, session)
        
        coins = await bot.get_cached_coins()
        coin_list = bot.format_coin_list(coins)
        
        await query.edit_message_text(
            f"*Swap Type:* {swap_type.title()}\n\n"
            f"Please enter the *coin symbol* you want to swap FROM:\n\n"
            f"Available coins:\n{coin_list}\n\n"
            f"Example: BTC",
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Handle network selection
    elif query.data.startswith("network_"):
        parts = query.data.split("_")
        network_type = parts[1]  # "deposit" or "settle"
        network = "_".join(parts[2:])  # Handle networks with underscores
        
        if network_type == "deposit":
            session["deposit_network"] = network
            session["state"] = "awaiting_settle_coin"
            await bot.save_user_session(user_id, session)
            
            coins = await bot.get_cached_coins()
            coin_list = bot.format_coin_list(coins)
            
            await query.edit_message_text(
                f"✅ Deposit: {session['deposit_coin']} on {network}\n\n"
                f"Now enter the *coin symbol* you want to receive:\n\n"
                f"Available coins:\n{coin_list}\n\n"
                f"Example: ETH",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif network_type == "settle":
            session["settle_network"] = network
            await bot.save_user_session(user_id, session)
            
            if session["swap_type"] == "fixed":
                session["state"] = "awaiting_amount"
                await bot.save_user_session(user_id, session)
                await query.edit_message_text(
                    f"✅ From: {session['deposit_coin']} ({session['deposit_network']})\n"
                    f"✅ To: {session['settle_coin']} ({session['settle_network']})\n\n"
                    f"Enter the *amount* of {session['deposit_coin']} to swap:",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                # For variable rate, get min/max info
                async with bot.api as api:
                    pair_info = await api.get_pair_info(
                        f"{session['deposit_coin']}-{session['deposit_network']}",
                        f"{session['settle_coin']}-{session['settle_network']}"
                    )
                
                if "error" not in pair_info:
                    session["state"] = "awaiting_settle_address"
                    await bot.save_user_session(user_id, session)
                    await query.edit_message_text(
                        f"✅ From: {session['deposit_coin']} ({session['deposit_network']})\n"
                        f"✅ To: {session['settle_coin']} ({session['settle_network']})\n\n"
                        f"📊 *Current Rate:* {pair_info.get('rate', 'N/A')}\n"
                        f"📉 *Min:* {pair_info.get('min', 'N/A')} {session['deposit_coin']}\n"
                        f"📈 *Max:* {pair_info.get('max', 'N/A')} {session['deposit_coin']}\n\n"
                        f"Enter your {session['settle_coin']} *destination address*:",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await query.edit_message_text(
                        f"❌ Error getting pair info: {pair_info.get('error', 'Unknown error')}"
                    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages based on user state"""
    bot = context.bot_data.get('swap_bot')
    user_id = update.message.from_user.id
    session = await bot.get_user_session(user_id)
    text = update.message.text.strip()
    
    # Update user activity
    await bot.db.update_user_activity(user_id)
    
    if session["state"] == "awaiting_deposit_coin":
        session["deposit_coin"] = text.upper()
        coins = await bot.get_cached_coins()
        networks = bot.get_networks_for_coin(coins, session["deposit_coin"])
        
        if networks:
            keyboard = []
            for i in range(0, len(networks), 2):
                row = []
                row.append(InlineKeyboardButton(
                    networks[i],
                    callback_data=f"network_deposit_{networks[i]}"
                ))
                if i + 1 < len(networks):
                    row.append(InlineKeyboardButton(
                        networks[i + 1],
                        callback_data=f"network_deposit_{networks[i + 1]}"
                    ))
                keyboard.append(row)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"Select network for {session['deposit_coin']}:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f"❌ Coin '{text}' not found. Please enter a valid coin symbol."
            )
    
    elif session["state"] == "awaiting_settle_coin":
        session["settle_coin"] = text.upper()
        coins = await bot.get_cached_coins()
        networks = bot.get_networks_for_coin(coins, session["settle_coin"])
        
        if networks:
            keyboard = []
            for i in range(0, len(networks), 2):
                row = []
                row.append(InlineKeyboardButton(
                    networks[i],
                    callback_data=f"network_settle_{networks[i]}"
                ))
                if i + 1 < len(networks):
                    row.append(InlineKeyboardButton(
                        networks[i + 1],
                        callback_data=f"network_settle_{networks[i + 1]}"
                    ))
                keyboard.append(row)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"Select network for {session['settle_coin']}:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f"❌ Coin '{text}' not found. Please enter a valid coin symbol."
            )
    
    elif session["state"] == "awaiting_amount":
        try:
            amount = float(text)
            session["deposit_amount"] = str(amount)
            await bot.save_user_session(user_id, session)
            
            # Request quote for fixed rate
            await update.message.reply_text("⏳ Requesting quote...")
            
            # Get user IP (in production, you'd get the actual IP)
            user_ip = "1.1.1.1"  # Placeholder - implement proper IP detection
            
            async with bot.api as api:
                quote = await api.request_quote(
                    session["deposit_coin"],
                    session["deposit_network"],
                    session["settle_coin"],
                    session["settle_network"],
                    session["deposit_amount"],
                    user_ip
                )
            
            if "error" not in quote:
                session["quote_id"] = quote["id"]
                session["state"] = "awaiting_settle_address"
                await bot.save_user_session(user_id, session)
                
                await update.message.reply_text(
                    f"✅ *Quote received!*\n\n"
                    f"💱 *Exchange:* {quote['depositAmount']} {session['deposit_coin']} → "
                    f"{quote['settleAmount']} {session['settle_coin']}\n"
                    f"📊 *Rate:* {quote['rate']}\n"
                    f"⏱ *Valid until:* {quote['expiresAt']}\n\n"
                    f"Enter your {session['settle_coin']} *destination address*:",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    f"❌ Error requesting quote: {quote['error']}\n\n"
                    f"Please try again with /swap"
                )
                session["state"] = "idle"
                await bot.save_user_session(user_id, session)
        except ValueError:
            await update.message.reply_text(
                "❌ Please enter a valid number"
            )
    
    elif session["state"] == "awaiting_settle_address":
        if await bot.validate_crypto_address(text, session["settle_coin"], session["settle_network"]):
            session["settle_address"] = text
            session["state"] = "awaiting_refund_address"
            await bot.save_user_session(user_id, session)
            
            await update.message.reply_text(
                f"Enter your {session['deposit_coin']} *refund address* "
                f"(or type 'skip' to continue without):",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                f"❌ Invalid address format. Please enter a valid {session['settle_coin']} address."
            )
    
    elif session["state"] == "awaiting_refund_address":
        if text.lower() != 'skip':
            if await bot.validate_crypto_address(text, session["deposit_coin"], session["deposit_network"]):
                session["refund_address"] = text
            else:
                await update.message.reply_text(
                    f"❌ Invalid refund address format. Please enter a valid {session['deposit_coin']} address or type 'skip'."
                )
                return
        
        # Create the shift
        await update.message.reply_text("⏳ Creating swap...")
        
        user_ip = "1.1.1.1"  # Placeholder - implement proper IP detection
        
        async with bot.api as api:
            if session["swap_type"] == "fixed":
                shift = await api.create_fixed_shift(
                    session["quote_id"],
                    session["settle_address"],
                    session.get("refund_address"),
                    user_ip=user_ip
                )
            else:
                shift = await api.create_variable_shift(
                    session["deposit_coin"],
                    session["deposit_network"],
                    session["settle_coin"],
                    session["settle_network"],
                    session["settle_address"],
                    session.get("refund_address"),
                    user_ip=user_ip
                )
        
        if "error" not in shift:
            session["shift_id"] = shift["id"]
            session["state"] = "swap_created"
            await bot.save_user_session(user_id, session)
            
            # Save swap to database
            await bot.db.save_swap(user_id, shift)
            
            deposit_address = shift["depositAddress"]
            deposit_memo = shift.get("depositMemo", "")
            
            message = (
                f"✅ *Swap Created Successfully!*\n\n"
                f"🆔 *Shift ID:* `{shift['id']}`\n"
                f"💱 *Type:* {session['swap_type'].title()}\n\n"
            )
            
            if session["swap_type"] == "fixed":
                message += (
                    f"📥 *Send exactly:* `{shift['depositAmount']}` {session['deposit_coin']}\n"
                    f"📤 *You'll receive:* `{shift['settleAmount']}` {session['settle_coin']}\n"
                    f"⏱ *Valid until:* {shift['expiresAt']}\n\n"
                )
            else:
                message += (
                    f"📉 *Min deposit:* `{shift['depositMin']}` {session['deposit_coin']}\n"
                    f"📈 *Max deposit:* `{shift['depositMax']}` {session['deposit_coin']}\n"
                    f"⏱ *Valid for:* 7 days\n\n"
                )
            
            message += (
                f"📍 *Send {session['deposit_coin']} to:*\n"
                f"`{deposit_address}`\n"
            )
            
            if deposit_memo:
                message += f"\n⚠️ *MEMO Required:* `{deposit_memo}`\n"
            
            message += (
                f"\n🔗 *Track at:* https://sideshift.ai/orders/{shift['id']}\n\n"
                f"Use /status to check the swap status"
            )
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(
                f"❌ Error creating swap: {shift['error']}\n\n"
                f"Please try again with /swap"
            )
        
        session["state"] = "idle"
        await bot.save_user_session(user_id, session)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check swap status"""
    bot = context.bot_data.get('swap_bot')
    user_id = update.message.from_user.id
    session = await bot.get_user_session(user_id)
    
    if session.get("shift_id"):
        async with bot.api as api:
            shift_data = await api.get_shift_status(session["shift_id"])
        
        if shift_data and "error" not in shift_data:
            status_text = bot.format_swap_status(shift_data["status"])
            
            message = (
                f"{status_text}\n\n"
                f"🆔 *Shift ID:* `{shift_data['id']}`\n"
                f"💱 *Pair:* {shift_data['depositCoin']} → {shift_data['settleCoin']}\n"
            )
            
            if shift_data.get("depositAmount"):
                message += f"📥 *Deposited:* {shift_data['depositAmount']} {shift_data['depositCoin']}\n"
            
            if shift_data.get("settleAmount"):
                message += f"📤 *To receive:* {shift_data['settleAmount']} {shift_data['settleCoin']}\n"
            
            if shift_data.get("depositHash"):
                message += f"🔗 *Deposit TX:* `{shift_data['depositHash'][:16]}...`\n"
            
            if shift_data.get("settleHash"):
                message += f"🔗 *Settlement TX:* `{shift_data['settleHash'][:16]}...`\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Could not fetch swap status")
    else:
        await update.message.reply_text(
            "No active swap found. Start a new swap with /swap"
        )

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View swap history"""
    bot = context.bot_data.get('swap_bot')
    user_id = update.message.from_user.id
    
    swaps = await bot.db.get_user_swaps(user_id, limit=10)
    
    if not swaps:
        await update.message.reply_text(
            "📊 No swap history found. Start your first swap with /swap"
        )
        return
    
    message = "📊 *Your Swap History:*\n\n"
    
    for i, swap in enumerate(swaps[:5], 1):  # Show last 5 swaps
        status_emoji = "✅" if swap["status"] == "settled" else "⏳"
        message += (
            f"{i}. {status_emoji} {swap['deposit_coin']} → {swap['settle_coin']}\n"
            f"   Status: {swap['status']}\n"
            f"   Amount: {swap['deposit_amount']} {swap['deposit_coin']}\n"
            f"   Date: {swap['created_at'][:10]}\n\n"
        )
    
    if len(swaps) > 5:
        message += f"... and {len(swaps) - 5} more swaps"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check exchange rates"""
    await update.message.reply_text(
        "Enter pair to check (e.g., 'BTC ETH' or 'btc-bitcoin eth-ethereum'):"
    )
    context.user_data['awaiting_rate_check'] = True

async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage price alerts"""
    bot = context.bot_data.get('swap_bot')
    user_id = update.message.from_user.id
    
    user_alerts = await bot.db.get_user_alerts(user_id)
    
    if not user_alerts:
        message = (
            "📈 *Price Alerts*\n\n"
            "No active alerts. To create an alert:\n"
            "1. Use /rates to check current rates\n"
            "2. Set up alerts for price changes\n\n"
            "This feature will be available soon!"
        )
    else:
        message = "📈 *Your Price Alerts:*\n\n"
        for alert in user_alerts:
            message += (
                f"• {alert['from_coin']} → {alert['alert_coin']}\n"
                f"  Alert when {alert['alert_type']} {alert['target_rate']}\n\n"
            )
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View user statistics"""
    bot = context.bot_data.get('swap_bot')
    user_id = update.message.from_user.id
    
    stats = await bot.db.get_user_stats(user_id)
    
    if not stats:
        await update.message.reply_text(
            "📊 No statistics available yet. Start trading to see your stats!"
        )
        return
    
    message = (
        f"📊 *Your Statistics*\n\n"
        f"🔄 Total Swaps: {stats.get('total_swaps', 0)}\n"
        f"✅ Completed: {stats.get('completed_swaps', 0)}\n"
        f"⏳ Active: {stats.get('active_swaps', 0)}\n"
        f"🔙 Refunded: {stats.get('refunded_swaps', 0)}\n"
        f"💰 Total Volume: {stats.get('total_volume', 0):.4f}\n\n"
    )
    
    if stats.get('recent_swaps'):
        message += "*Recent Swaps:*\n"
        for swap in stats['recent_swaps'][:3]:
            status_emoji = "✅" if swap["status"] == "settled" else "⏳"
            message += (
                f"• {status_emoji} {swap['deposit_coin']} → {swap['settle_coin']}\n"
            )
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    bot = context.bot_data.get('swap_bot')
    user_id = update.message.from_user.id
    
    await bot.db.clear_user_session(user_id)
    
    await update.message.reply_text(
        "✅ Operation cancelled. Use /swap to start a new swap."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    help_text = (
        "*📚 How to use the Swap Bot:*\n\n"
        "*1. Start a swap:*\n"
        "   • Use /swap command\n"
        "   • Choose Fixed or Variable rate\n"
        "   • Select coins and networks\n"
        "   • Enter amounts and addresses\n\n"
        "*2. Fixed vs Variable:*\n"
        "   • Fixed: Rate locked for 15 min\n"
        "   • Variable: Market rate at deposit\n\n"
        "*3. Important:*\n"
        "   • Always double-check addresses\n"
        "   • Include MEMO if required\n"
        "   • Save your Shift ID\n\n"
        "*4. Commands:*\n"
        "   • /status - Check swap status\n"
        "   • /history - View past swaps\n"
        "   • /rates - Check exchange rates\n"
        "   • /stats - View statistics\n"
        "   • /cancel - Cancel operation\n\n"
        "*5. Support:*\n"
        "   • Email: help@sideshift.ai\n"
        "   • Track: sideshift.ai/orders/YOUR_ID"
    )
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again or contact support."
        )

def main():
    """Start the bot"""
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    SIDESHIFT_SECRET = os.getenv('SIDESHIFT_SECRET')
    SIDESHIFT_AFFILIATE_ID = os.getenv('SIDESHIFT_AFFILIATE_ID')
    COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.005"))
    DATABASE_PATH = os.getenv("DATABASE_PATH", "swap_bot.db")
    
    # Validate required environment variables
    if not all([TELEGRAM_TOKEN, SIDESHIFT_SECRET, SIDESHIFT_AFFILIATE_ID]):
        logger.error("Missing required environment variables. Please check your .env file.")
        return
    
    # Initialize API and database
    sideshift_api = SideShiftAPI(SIDESHIFT_SECRET, SIDESHIFT_AFFILIATE_ID, COMMISSION_RATE)
    database = SwapDatabase(DATABASE_PATH)
    swap_bot = SwapBot(sideshift_api, database)
    
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Store bot instance in context
    application.bot_data['swap_bot'] = swap_bot
    
    # Add handlers
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
    
    # Start bot
    logger.info("Starting Cross-Chain Swap Bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
