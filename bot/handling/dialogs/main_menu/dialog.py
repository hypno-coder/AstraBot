from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const  # или Format, если нужны динамические переводы

from bot.handling.states import Main_menu 


# Обработчики нажатий на кнопки (пример, здесь можно реализовать нужную логику)
async def on_horoscope(callback: CallbackQuery, button, dialog_manager):
    await callback.answer("Вы выбрали 'Гороскоп'")


async def on_compatibility(callback: CallbackQuery, button, dialog_manager):
    await callback.answer("Вы выбрали 'Совместимость'")


async def on_sonnik(callback: CallbackQuery, button, dialog_manager):
    await callback.answer("Вы выбрали 'Сонник'")


async def on_premium(callback: CallbackQuery, button, dialog_manager):
    await callback.answer("Вы выбрали 'Премиум функции'")


menu_window = Window(
    Const("Выберите опцию:"),
    Button(Const("Гороскоп"), id="horoscope", on_click=on_horoscope),
    Button(Const("Совместимость"), id="compatibility", on_click=on_compatibility),
    Button(Const("Сонник"), id="sonnik", on_click=on_sonnik),
    Button(Const("Премиум функции"), id="premium", on_click=on_premium),
    state=Main_menu.start,
)


dialog = Dialog(menu_window)
