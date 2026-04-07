from aiogram import Router, types, F
from aiogram.filters import CommandStart
from core.database.models import async_session, User
from sqlalchemy import select
import logging

from bot.keyboards.main_menu import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    async with async_session() as session:
        # Check if user exists
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            new_user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name
            )
            session.add(new_user)
            await session.commit()
            logger.info(f"New user registered: {message.from_user.id}")
    
    await message.answer(
        f"🦾 <b>Вітаю у Poster Control System (PCS), {message.from_user.first_name}!</b>\n\n"
        "Вас вітає фінальна версія системи керування бізнесом. "
        "Ядро: <i>aiogram 3 (Async)</i>.\n\n"
        "Оберіть дію в меню:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🦾 <b>Головне меню PCS</b>\nОберіть потрібний розділ аналітики:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
