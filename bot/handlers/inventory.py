from aiogram import Router, types, F
from modules.inventory import AsyncInventory, format_shopping_report
from bot.keyboards.main_menu import get_back_button
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "shopping_list")
async def show_shopping_list(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ <b>Отримую дані про залишки...</b>", parse_mode="HTML")
    
    inventory = AsyncInventory()
    items = await inventory.get_shopping_list()
    
    report_text = format_shopping_report(items)
    await callback.message.edit_text(report_text, reply_markup=get_back_button(), parse_mode="HTML")
