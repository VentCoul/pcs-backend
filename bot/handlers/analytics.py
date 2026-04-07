from aiogram import Router, types, F
from modules.analytics import AsyncAnalytics
from modules.gemini_expert import AsyncGeminiExpert
from bot.keyboards.main_menu import get_back_button
import logging

router = Router()
logger = logging.getLogger(__name__)

async def format_abc_report(results: dict) -> str:
    if not results:
        return "⚠️ Недостатньо даних для аналізу."
    
    # 1. Готуємо дані для Gemini (топ-3 з кожної категорії)
    items_to_analyze = []
    categories_keys = ["STARS", "PLOWHORSES", "PUZZLES", "DOGS"]
    for cat_key in categories_keys:
        for item in results.get(cat_key, [])[:3]:
            items_to_analyze.append({
                'id': item['id'],
                'name': item['name'],
                'cat': cat_key,
                'qty': item['qty'],
                'profit': item['profit']
            })

    # 2. Отримуємо поради від Gemini
    expert = AsyncGeminiExpert()
    advices = await expert.get_batch_advice(items_to_analyze)
    
    # 3. Формуємо текстовий звіт
    report = "📈 <b>АНАЛІТИКА ТА ПОРАДИ ШІ (30 днів)</b>\n"
    report += "------------------------------------------\n"
    
    mapping = [
        ("💎 STARS (Лідери)", "STARS"),
        ("🛒 PLOWHORSES (Маст-хев)", "PLOWHORSES"),
        ("⭐ PUZZLES (Потенціал)", "PUZZLES"),
        ("📉 DOGS (Слабкі)", "DOGS")
    ]
    
    for title, key in mapping:
        report += f"\n<b>{title}:</b>\n"
        items = results.get(key, [])
        if not items:
            report += "   <i>(Порожньо)</i>\n"
        else:
            for i, item in enumerate(items[:3], 1):
                unit = "кг" if item['weight_flag'] else "шт."
                qty = item['qty']
                if item['weight_flag']: qty = round(qty/1000, 2)
                
                advice = advices.get(str(item['id']), "Аналізуйте динаміку.")
                
                report += f"   {i}. <b>{item['name']}</b>\n"
                report += f"      Прибуток: <b>{int(item['profit'])} ₴</b> | Порада: <i>{advice}</i>\n"
    
    report += "\n------------------------------------------\n"
    report += "🦾 <b>AI Assistant (Jarvis PCS Expert)</b>"
    return report

@router.callback_query(F.data == "run_abc")
async def run_abc_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ <b>Зачекайте...</b> Аналізую дані та запитую поради у ШІ.", parse_mode="HTML")
    
    analytics = AsyncAnalytics()
    results = await analytics.run_abc_analysis(days=30)
    
    report_text = await format_abc_report(results)
    await callback.message.edit_text(report_text, reply_markup=get_back_button(), parse_mode="HTML")
