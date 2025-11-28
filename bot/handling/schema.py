from typing import Awaitable

import structlog
from aiogram import Dispatcher
from aiogram_dialog import StartMode, setup_dialogs

from bot.handling.dialogs import main_dialog
from bot.handling.filters import ChatType, ChatTypeFilter
from bot.handling.handlers import get_user_router, start_router, sub_router
from bot.handling.middlewares import (DatabaseMiddleware,
                                      DialogResetMiddleware, LoggingMiddleware,
                                      TranslatorRunnerMiddleware,
                                      UserSubscriptionMiddleware,
                                      UserSyncMiddleware)
from bot.handling.middlewares.user_sync import SyncTTL
from bot.handling.states import Main_menu, Watermark

logger = structlog.getLogger('schema')


async def assemble(
        dispatcher_factory: Awaitable[Dispatcher]
) -> Dispatcher:
    
    dp = await dispatcher_factory
    setup_dialogs(dp)

    # Миддлвари 
    dp.update.middleware(LoggingMiddleware())

    t = TranslatorRunnerMiddleware()
    dp.message.middleware(t)
    dp.callback_query.middleware(t)

    dp.update.middleware(DatabaseMiddleware("_db_session_maker"))  
    dp.my_chat_member.middleware(UserSubscriptionMiddleware())
    dp.update.middleware(UserSyncMiddleware(ttl_sec=SyncTTL.HOURS_12))
    dp.update.middleware(DialogResetMiddleware(init_state=Main_menu.start, mode=StartMode.RESET_STACK))


    # Глобальный фильтр
    dp.update.filter(ChatTypeFilter(ChatType.private))

    # Роутеры
    dp.include_router(main_dialog)
    dp.include_router(get_user_router)
    dp.include_router(start_router)
    dp.include_router(sub_router)

    return dp
