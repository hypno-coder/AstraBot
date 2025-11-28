from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict 

from aiogram import BaseMiddleware
from aiogram.types import  ChatMemberUpdated, TelegramObject
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from database.models import User


class UserSubscriptionMiddleware(BaseMiddleware):

    def __init__(self, db_ctx_key: str = "db"):
        self.db_ctx_key = db_ctx_key
        self.logger = get_logger("UserSubscriptionMiddleware")

    async def __call__(
            self, 
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: ChatMemberUpdated, 
            ctx_data: Dict[str, Any]
    ):
        await self.logger.debug("UserSubscriptionMiddleware begun")
        db: AsyncSession | None = ctx_data.get(self.db_ctx_key)
        
        if db is None:
            await self.logger.debug("UserSubscriptionMiddleware Db is None")
            return await handler(event, ctx_data)
            
        if event.chat and event.chat.type == "private":
            status = event.new_chat_member.status
            tg_id = event.chat.id
            if status == "member":
                await db.execute(update(User).where(User.telegram_id == tg_id)
                                .values(is_subscribed=True, unsubscribed_at=func.now()))
            elif status == "kicked":
                await db.execute(update(User).where(User.telegram_id == tg_id)
                                .values(is_subscribed=False, unsubscribed_at=func.now()))
        await handler(event, ctx_data)
        await self.logger.debug("UserSubscriptionMiddleware end")
