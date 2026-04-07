from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📈 ABC Аналіз Меню", callback_data="run_abc"))
    builder.row(types.InlineKeyboardButton(text="🛒 Список Закупівель", callback_data="shopping_list"))
    builder.row(types.InlineKeyboardButton(text="💰 Фінанси за День", callback_data="daily_finance"))
    builder.row(types.InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings"))
    return builder.as_markup()

def get_back_button():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    return builder.as_markup()
