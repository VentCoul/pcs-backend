import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from core.config import settings
from core.database.models import init_db
from bot.handlers import start, analytics, inventory

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize Database
    await init_db()
    
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Register routers
    dp.include_router(start.router)
    dp.include_router(analytics.router)
    dp.include_router(inventory.router)
    
    print("🦾 Poster Control System (PCS) Activated. Listening for commands...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
