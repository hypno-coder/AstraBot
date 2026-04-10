from typing import Any
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button


async def on_invite(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Send the invite link as a regular message so the user can copy/share it."""
    invite_link = dialog_manager.dialog_data.get("invite_link") or ""
    # Fallback: read from getter result stored in middleware
    if not invite_link:
        from aiogram_dialog import DialogManager
        bot = dialog_manager.middleware_data["bot"]
        bi = await bot.get_me()
        invite_link = f"https://t.me/{bi.username}?start={callback.from_user.id}"

    await callback.message.answer(
        f"🔗 Ваша реферальная ссылка:\n\n<code>{invite_link}</code>\n\n"
        "Поделитесь ей с друзьями! Когда они запустят бота — вам засчитается приглашение.",
        parse_mode="HTML"
    )
    await callback.answer()
