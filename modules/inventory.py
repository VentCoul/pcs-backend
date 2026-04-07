import asyncio
import logging
from typing import List, Dict, Any
from core.api.poster_control import PosterControlAPI
from bot.keyboards.main_menu import get_main_menu

logger = logging.getLogger("InventoryModule")

class AsyncInventory:
    def __init__(self):
        self.api = PosterControlAPI()

    async def get_shopping_list(self) -> List[Dict[str, Any]]:
        """Отримує список інгредієнтів, які потрібно закупити."""
        leftovers = await self.api.get_leftovers()
        shopping_list = []
        
        if not leftovers:
            return []

        for item in leftovers:
            current = float(item.get('leftover', 0))
            limit = float(item.get('min_limit', 0))
            
            if limit > 0 and current < limit:
                shopping_list.append({
                    "name": item.get('ingredient_name', 'Невідомо'),
                    "current": round(current, 2),
                    "needed": round(limit, 2),
                    "to_buy": round(limit - current, 2),
                    "unit": item.get('unit', '')
                })
        
        return shopping_list

def format_shopping_report(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "✅ <b>Всі запаси в нормі.</b> Закуповувати нічого не потрібно."

    report = "🛒 <b>СПИСОК ЗАКУПІВЕЛЬ (Poster)</b>\n"
    report += "------------------------------------------\n"
    for i, item in enumerate(items, 1):
        report += (f"{i}. <b>{item['name']}</b>:\n"
                  f"   📉 Залишок: {item['current']} {item['unit']} (Мін: {item['needed']})\n"
                  f"   ➕ ТРЕБА КУПИТИ: <b>{item['to_buy']} {item['unit']}</b>\n\n")
    
    report += "------------------------------------------\n"
    report += "🦾 <i>PCS Inventory Engine</i>"
    return report
