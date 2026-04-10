from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Const, Format
from bot.handling.states import Main_menu, Profile, AdminGroup
from .getters import get_main_menu_data

# Обработчики нажатий на кнопки (пример, здесь можно реализовать нужную логику)
async def on_horoscope(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Вы выбрали 'Гороскоп'")


async def on_compatibility(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Вы выбрали 'Совместимость'")


async def on_sonnik(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Вы выбрали 'Сонник'")


async def on_premium(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Вы выбрали 'Премиум функции'")


menu_window = Window(
    Format("{main_menu_prompt}"),
    Start(Format("{admin_btt}"), id="go_admin", state=AdminGroup.view, when="is_admin"),
    Start(Format("{profile_btt}"), id="go_profile", state=Profile.view),
    Button(Format("{horoscope_btt}"), id="horoscope", on_click=on_horoscope),
    Button(Format("{compatibility_btt}"), id="compatibility", on_click=on_compatibility),
    Button(Format("{sonnik_btt}"), id="sonnik", on_click=on_sonnik),
    Button(Format("{premium_features_btt}"), id="premium", on_click=on_premium),
    state=Main_menu.start,
    getter=get_main_menu_data
)

dialog = Dialog(menu_window)
