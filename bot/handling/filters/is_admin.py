from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User
from bot.config import BotConfig

class IsAdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, bot_config: BotConfig, db: AsyncSession, **kwargs) -> bool:
        if event.from_user.id == bot_config.owner_id:
            return True
        user = await db.scalar(select(User).where(User.id == event.from_user.id))
        return bool(user and user.is_admin)
