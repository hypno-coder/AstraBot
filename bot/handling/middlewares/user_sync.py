from __future__ import annotations

import time
from enum import IntEnum
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from database.models import User


class SyncTTL(IntEnum):
    HOUR = 60 * 60
    HOURS_12 = 12 * 60 * 60
    HOURS_24 = 24 * 60 * 60

class UserSyncMiddleware(BaseMiddleware):
    def __init__(self, ttl_sec: SyncTTL = SyncTTL.HOUR, db_ctx_key: str = "db") -> None:
        self.db_ctx_key = db_ctx_key
        self.ttl = ttl_sec
        # локальный троттлер: {telegram_id: unix_ts_последнего_синка}
        self._sync_cache: dict[int, float] = {}
        self.logger = get_logger("UserSyncMiddleware")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        ctx_data: Dict[str, Any],
    ) -> Any:
        await self.logger.debug("UserSyncMiddleware begun")
        db: AsyncSession | None = ctx_data.get(self.db_ctx_key)
        if db is None:
            await self.logger.debug("UserSyncMiddleware Db is None")
            return await handler(event, ctx_data)

        fu = self._extract_from_user(event)
        if fu is not None:
            # троттлим профиль + last_seen_at в одном upsert'е
            await self._maybe_sync_user(
                db=db,
                tg_id=fu.id,
                username=getattr(fu, "username", None),
                lang=getattr(fu, "language_code", None),
                is_premium=bool(getattr(fu, "is_premium", False)),
            )


        await handler(event, ctx_data)
        await self.logger.debug("UserSyncMiddleware end")

        
    def _extract_from_user(self, ev: Update):
        if ev.message:               return ev.message.from_user
        if ev.edited_message:        return ev.edited_message.from_user
        if ev.callback_query:        return ev.callback_query.from_user
        if ev.inline_query:          return ev.inline_query.from_user
        if ev.chosen_inline_result:  return ev.chosen_inline_result.from_user
        if ev.shipping_query:        return ev.shipping_query.from_user
        if ev.pre_checkout_query:    return ev.pre_checkout_query.from_user
        if ev.poll_answer:           return ev.poll_answer.user
        if ev.my_chat_member:        return ev.my_chat_member.from_user
        if ev.chat_member:           return ev.chat_member.from_user
        return None

    async def _maybe_sync_user(
        self,
        db: AsyncSession,
        tg_id: int,
        username: Optional[str],
        lang: Optional[str],
        is_premium: bool,
    ):
        now = time.time()
        last = self._sync_cache.get(tg_id, 0)
        # if now - last < self.ttl.value:
        if now - last < 1:
            return
        self._sync_cache[tg_id] = now

        stmt = (
            insert(User)
            .values(
                telegram_id=tg_id,
                username=username,
                lang=(lang or "ru")[:8],
                is_premium=is_premium,
                last_seen_at=func.now(),
            )
            .on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_={
                    "username": username,
                    "lang": (lang or "ru")[:8],
                    "is_premium": is_premium,
                    "last_seen_at": func.now(),
                },
            )
        )
        await db.execute(stmt)
