import aiohttp
import logging
from typing import Optional, Dict, Any, List
from core.config import settings

logger = logging.getLogger("PosterControlAPI")

class PosterControlAPI:
    def __init__(self):
        self.account = settings.poster_account
        self.token = settings.poster_token
        self.base_url = f"https://{self.account}.joinposter.com/api"

    async def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}/{endpoint}"
        all_params = {"token": self.token}
        if params:
            all_params.update(params)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, params=all_params, timeout=30) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if isinstance(data, dict) and 'error' in data:
                        logger.error(f"Poster API Error: {data['error']}")
                        return None
                        
                    return data.get('response') if isinstance(data, dict) and 'response' in data else data
            except Exception as e:
                logger.error(f"API Connection Error ({endpoint}): {e}")
                return None

    async def get_leftovers(self) -> List[Dict[str, Any]]:
        """Отримує залишки інгредієнтів."""
        return await self._request("GET", "storage.getStorageLeftovers") or []

    async def get_transactions(self, date_from: str, date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """Отримує список транзакцій за період."""
        params = {"date_from": date_from}
        if date_to:
            params["date_to"] = date_to
        return await self._request("GET", "dash.getTransactions", params) or []
    
    async def get_menu_products(self) -> List[Dict[str, Any]]:
        """Отримує всі товари меню."""
        return await self._request("GET", "menu.getProducts") or []
        
    async def get_transaction_products(self, transaction_id: int) -> List[Dict[str, Any]]:
        """Отримує список товарів у конкретному чеку."""
        return await self._request("GET", "dash.getTransactionProducts", {"transaction_id": transaction_id}) or []
