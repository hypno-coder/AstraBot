from aiogram.types import CallbackQuery
from aiogram import F
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy import select
from bot.handling.states import Main_menu, Profile, AdminGroup, HoroscopeGroup, ReferralGroup
from .getters import get_main_menu_data

# Обработчики нажатий на кнопки (пример, здесь можно реализовать нужную логику)
async def on_horoscope(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Route to ask_dob if no zodiac_sign, else directly to horoscope view."""
    from database.models import User
    from sqlalchemy.ext.asyncio import AsyncSession
    db: AsyncSession = dialog_manager.middleware_data["db"]
    user = await db.scalar(select(User).where(User.id == callback.from_user.id))
    start_state = HoroscopeGroup.view if (user and user.zodiac_sign) else HoroscopeGroup.ask_dob
    await dialog_manager.start(start_state, mode=StartMode.NORMAL)



async def on_sonnik(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Вы выбрали 'Сонник'")


async def on_premium(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Вы выбрали 'Премиум функции'")


menu_window = Window(
    Format("{main_menu_prompt}"),
    Start(Format("{admin_btt}"), id="go_admin", state=AdminGroup.view, when="is_admin"),
    Start(Format("{profile_btt}"), id="go_profile", state=Profile.view),
    Button(Format("{horoscope_btt}"), id="horoscope", on_click=on_horoscope),
    Start(Format("{ref_btt}"), id="go_ref", state=ReferralGroup.view),
    Button(Format("{sonnik_btt}"), id="sonnik", on_click=on_sonnik),
    Button(Format("{premium_features_btt}"), id="premium", on_click=on_premium),
    state=Main_menu.start,
    getter=get_main_menu_data
)

dialog = Dialog(menu_window)
