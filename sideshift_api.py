"""
SideShift.ai API wrapper for cryptocurrency exchange operations.
Handles all API interactions including quotes, shifts, and status monitoring.
"""

import os
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json

logger = logging.getLogger(__name__)

class SideShiftAPI:
    """Handle SideShift API interactions"""
    
    def __init__(self, secret: str, affiliate_id: str, commission_rate: float = 0.005):
        self.base_url = "https://sideshift.ai/api/v2"
        self.secret = secret
        self.affiliate_id = affiliate_id
        self.commission_rate = commission_rate
        self.headers = {
            "x-sideshift-secret": secret,
            "Content-Type": "application/json"
        }
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, 
                           data: Dict = None, params: Dict = None,
                           user_ip: str = None) -> Dict:
        """Make HTTP request to SideShift API"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        
        if user_ip:
            headers["x-user-ip"] = user_ip
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                
                if response.status in [200, 201]:
                    return response_data
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    logger.error(f"API Error {response.status}: {error_msg}")
                    return {"error": error_msg, "status_code": response.status}
                    
        except asyncio.TimeoutError:
            logger.error("API request timeout")
            return {"error": "Request timeout"}
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e)}
    
    async def get_coins(self) -> List[Dict]:
        """Fetch available coins and networks"""
        result = await self._make_request("GET", "/coins")
        if "error" not in result:
            return result
        return []
    
    async def get_coin_icon(self, coin: str, network: str) -> str:
        """Get coin icon URL"""
        return f"{self.base_url}/coins/icon/{coin}-{network}"
    
    async def check_permissions(self, user_ip: str) -> bool:
        """Check if user can create shifts"""
        result = await self._make_request("GET", "/permissions", user_ip=user_ip)
        if "error" not in result:
            return result.get("createShift", False)
        return False
    
    async def get_pair_info(self, from_coin: str, to_coin: str, 
                           amount: Optional[float] = None) -> Dict:
        """Get pair exchange information"""
        params = {"affiliateId": self.affiliate_id}
        if amount:
            params["amount"] = amount
            
        result = await self._make_request(
            "GET", 
            f"/pair/{from_coin}/{to_coin}",
            params=params
        )
        return result if "error" not in result else {}
    
    async def get_pairs_info(self, pairs: List[str]) -> Dict:
        """Get information for multiple coin pairs"""
        params = {
            "affiliateId": self.affiliate_id,
            "pairs": ",".join(pairs)
        }
        
        result = await self._make_request("GET", "/pairs", params=params)
        return result if "error" not in result else {}
    
    async def request_quote(self, deposit_coin: str, deposit_network: str,
                           settle_coin: str, settle_network: str,
                           deposit_amount: str, user_ip: str) -> Dict:
        """Request a fixed rate quote"""
        data = {
            "depositCoin": deposit_coin,
            "depositNetwork": deposit_network,
            "settleCoin": settle_coin,
            "settleNetwork": settle_network,
            "depositAmount": deposit_amount,
            "settleAmount": None,
            "affiliateId": self.affiliate_id,
            "commissionRate": self.commission_rate
        }
        
        return await self._make_request("POST", "/quotes", data=data, user_ip=user_ip)
    
    async def create_fixed_shift(self, quote_id: str, settle_address: str,
                                refund_address: Optional[str] = None,
                                refund_memo: Optional[str] = None,
                                user_ip: str = None) -> Dict:
        """Create a fixed rate shift"""
        data = {
            "settleAddress": settle_address,
            "affiliateId": self.affiliate_id,
            "quoteId": quote_id,
            "commissionRate": self.commission_rate
        }
        
        if refund_address:
            data["refundAddress"] = refund_address
        if refund_memo:
            data["refundMemo"] = refund_memo
        
        return await self._make_request("POST", "/shifts/fixed", data=data, user_ip=user_ip)
    
    async def create_variable_shift(self, deposit_coin: str, deposit_network: str,
                                   settle_coin: str, settle_network: str,
                                   settle_address: str, 
                                   refund_address: Optional[str] = None,
                                   refund_memo: Optional[str] = None,
                                   user_ip: str = None) -> Dict:
        """Create a variable rate shift"""
        data = {
            "depositCoin": deposit_coin,
            "depositNetwork": deposit_network,
            "settleCoin": settle_coin,
            "settleNetwork": settle_network,
            "settleAddress": settle_address,
            "affiliateId": self.affiliate_id,
            "commissionRate": self.commission_rate
        }
        
        if refund_address:
            data["refundAddress"] = refund_address
        if refund_memo:
            data["refundMemo"] = refund_memo
        
        return await self._make_request("POST", "/shifts/variable", data=data, user_ip=user_ip)
    
    async def get_shift_status(self, shift_id: str) -> Dict:
        """Get shift status and details"""
        return await self._make_request("GET", f"/shifts/{shift_id}")
    
    async def get_multiple_shifts(self, shift_ids: List[str]) -> Dict:
        """Get multiple shifts status"""
        params = {"ids": ",".join(shift_ids)}
        return await self._make_request("GET", "/shifts", params=params)
    
    async def get_recent_shifts(self, limit: int = 10) -> List[Dict]:
        """Get recent completed shifts"""
        params = {"limit": min(limit, 100)}
        result = await self._make_request("GET", "/recent-shifts", params=params)
        return result if "error" not in result else []
    
    async def get_xai_stats(self) -> Dict:
        """Get XAI coin statistics"""
        return await self._make_request("GET", "/xai-stats")
    
    async def get_account_info(self) -> Dict:
        """Get account information"""
        return await self._make_request("GET", "/account")
    
    async def set_refund_address(self, shift_id: str, refund_address: str,
                                refund_memo: Optional[str] = None) -> Dict:
        """Set refund address for existing shift"""
        data = {"refundAddress": refund_address}
        if refund_memo:
            data["refundMemo"] = refund_memo
        
        return await self._make_request(
            "POST", 
            f"/shifts/{shift_id}/set-refund-address",
            data=data
        )
    
    async def cancel_order(self, shift_id: str) -> Dict:
        """Cancel an existing order"""
        data = {"shiftId": shift_id}
        return await self._make_request("POST", "/cancel-order", data=data)
    
    async def create_checkout(self, amount: str, coin: str, network: str,
                             description: str = None) -> Dict:
        """Create a checkout for merchant payments"""
        data = {
            "amount": amount,
            "coin": coin,
            "network": network,
            "affiliateId": self.affiliate_id
        }
        
        if description:
            data["description"] = description
        
        return await self._make_request("POST", "/checkout", data=data)
    
    async def get_checkout(self, checkout_id: str) -> Dict:
        """Get checkout information"""
        return await self._make_request("GET", f"/checkout/{checkout_id}")
    
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
    
    def get_coin_info(self, coins: List[Dict], coin_symbol: str, network: str = None) -> Dict:
        """Get detailed coin information"""
        for coin_data in coins:
            if coin_data["coin"].upper() == coin_symbol.upper():
                if network:
                    for net in coin_data["networks"]:
                        if net["name"] == network:
                            return {**coin_data, "selected_network": net}
                return coin_data
        return {}
    
    def validate_address(self, address: str, coin: str, network: str) -> bool:
        """Basic address validation (implement proper validation for production)"""
        if not address or len(address) < 10:
            return False
        
        # Add more specific validation based on coin/network
        # This is a basic implementation
        return True
    
    def calculate_estimated_fees(self, pair_info: Dict) -> Dict:
        """Calculate estimated fees for a swap"""
        fees = {
            "sending_fee": pair_info.get("sendingFee", "0"),
            "address_fee": pair_info.get("addressFee", "0"),
            "receiving_fee": pair_info.get("receivingFee", "0")
        }
        
        total_fee = 0
        for fee_type, fee_amount in fees.items():
            try:
                total_fee += float(fee_amount)
            except (ValueError, TypeError):
                pass
        
        fees["total_estimated_fee"] = str(total_fee)
        return fees
