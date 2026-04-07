from typing import List, Dict, Any, Optional
import asyncio
import google.generativeai as genai
import json
import logging
from core.config import settings
from core.database.models import async_session, AICache
from sqlalchemy import select
from datetime import datetime, timedelta

logger = logging.getLogger("GeminiExpert")

class AsyncGeminiExpert:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None

    async def get_cached_advice(self, product_id: str) -> Optional[str]:
        async with async_session() as session:
            stmt = select(AICache).where(AICache.product_id == product_id)
            result = await session.execute(stmt)
            cache = result.scalar_one_or_none()
            
            if cache and (datetime.now() - cache.updated_at < timedelta(hours=24)):
                return cache.advice
        return None

    async def save_cache(self, product_id: str, advice: str, category: str):
        async with async_session() as session:
            stmt = select(AICache).where(AICache.product_id == product_id)
            result = await session.execute(stmt)
            cache = result.scalar_one_or_none()
            
            if cache:
                cache.advice = advice
                cache.category = category
                cache.updated_at = datetime.now()
            else:
                new_cache = AICache(product_id=product_id, advice=advice, category=category)
                session.add(new_cache)
            await session.commit()

    async def get_batch_advice(self, items: List[Dict[str, Any]]) -> Dict[str, str]:
        if not self.model:
            return {item['id']: "Налаштуйте Gemini API Key" for item in items}

        results = {}
        to_query = []

        for item in items:
            cached = await self.get_cached_advice(item['id'])
            if cached:
                results[item['id']] = cached
            else:
                to_query.append(item)

        if not to_query:
            return results

        items_desc = ""
        for i, item in enumerate(to_query):
            items_desc += f"{i+1}. ID:{item['id']} | {item['name']} | Клас:{item['cat']} | Продано:{item['qty']} | Прибуток:{int(item['profit'])} грн\n"

        prompt = f"""
        Ти - професійний ресторанний консультант. Проаналізуй товари кав'ярні:
        {items_desc}
        
        Дай ОДНУ дуже коротку та практичну пораду для кожного товару (до 10 слів). 
        Використовуй терміни: маржа, фудкост, чек, допродажі.
        Відповідь надай ТІЛЬКИ у форматі JSON: {{"ID": "порада", ...}}
        Мова: українська.
        """

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
            
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            ai_advices = json.loads(text)

            for item in to_query:
                pid = str(item['id'])
                advice = ai_advices.get(pid, ai_advices.get(str(item['id']), "Аналізуйте динаміку."))
                results[pid] = advice
                await self.save_cache(pid, advice, item['cat'])

        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            for item in to_query:
                results[item['id']] = "Аналізуйте залишки та ціни."

        return results
