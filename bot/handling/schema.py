from typing import Awaitable

import structlog
from aiogram import Dispatcher
from aiogram_dialog import setup_dialogs, StartMode

from bot.handling.dialogs import main_dialog
from bot.handling.filters import ChatType, ChatTypeFilter
from bot.handling.handlers import start_router
from bot.handling.handlers import get_user_router

from bot.handling.middlewares import (
    DialogResetMiddleware,
    TranslatorRunnerMiddleware,
    DatabaseMiddleware,
)
from bot.handling.middlewares.logging import LoggingMiddleware
from bot.handling.states import Watermark, Main_menu

logger = structlog.getLogger('schema')


async def assemble(
        dispatcher_factory: Awaitable[Dispatcher]
) -> Dispatcher:
    dp = await dispatcher_factory
    setup_dialogs(dp)
    dp.update.middleware(LoggingMiddleware())
    t = TranslatorRunnerMiddleware()
    dp.message.middleware(t)
    dp.callback_query.middleware(t)
    db = DatabaseMiddleware('_db_session_maker')
    dp.message.middleware(db)
    dp.update.middleware(DialogResetMiddleware(init_state=Main_menu.start, mode=StartMode.RESET_STACK))
    dp.update.filter(ChatTypeFilter(ChatType.private))
    dp.include_router(main_dialog)
    dp.include_router(start_router)
    return dp
