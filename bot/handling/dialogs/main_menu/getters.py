from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User

async def get_main_menu_data(dialog_manager: DialogManager, **kwargs):
    db: AsyncSession = dialog_manager.middleware_data["db"]
    user = await db.scalar(select(User).where(User.id == dialog_manager.event.from_user.id))
    
    is_admin = bool(user and user.is_admin)
    
    # Check config
    bot_config = dialog_manager.middleware_data.get("bot_config")
    if bot_config and dialog_manager.event.from_user.id == bot_config.owner_id:
        is_admin = True

    i18n = dialog_manager.middleware_data["i18n"]
    return {
        "is_admin": is_admin,
        "admin_btt": i18n.admin_btt()
    }
