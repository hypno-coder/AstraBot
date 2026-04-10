from typing import Any
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database.models import User

async def on_lang_toggle(callback: CallbackQuery, button: Any, dialog_manager: DialogManager):
    db: AsyncSession = dialog_manager.middleware_data["db"]
    user = await db.scalar(select(User).where(User.id == callback.from_user.id))
    
    if user:
        new_lang = "en" if user.language_code == "ru" else "ru"
        await db.execute(update(User).where(User.id == user.id).values(language_code=new_lang))
        
        # Manually swap the translator for the rest of this event (to instantly refresh the dialog)
        hub = dialog_manager.middleware_data.get("_translator_hub")
        if hub:
            dialog_manager.middleware_data["i18n"] = hub.get_translator_by_locale(new_lang)

async def dummy_action(callback: CallbackQuery, button: Any, dialog_manager: DialogManager):
    # Dummy handler for buttons that would do nothing or show "under construction"
    await callback.answer("Action acknowledged.", show_alert=False)
