from typing import Any
from datetime import datetime, date

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from database.models import User, Gender
from bot.handling.states.profile import Profile

async def save_fio(message: Message, message_input: MessageInput, dialog_manager: DialogManager):
    db: AsyncSession = dialog_manager.middleware_data["db"]
    await db.execute(update(User).where(User.id == message.from_user.id).values(fio=message.text))
    await dialog_manager.switch_to(Profile.view)

async def save_city(message: Message, message_input: MessageInput, dialog_manager: DialogManager):
    db: AsyncSession = dialog_manager.middleware_data["db"]
    await db.execute(update(User).where(User.id == message.from_user.id).values(birth_city=message.text))
    await dialog_manager.switch_to(Profile.view)

async def save_time(message: Message, message_input: MessageInput, dialog_manager: DialogManager):
    i18n = dialog_manager.middleware_data["i18n"]
    try:
        t = datetime.strptime(message.text.strip(), "%H:%M").time()
        db: AsyncSession = dialog_manager.middleware_data["db"]
        await db.execute(update(User).where(User.id == message.from_user.id).values(birth_time=t))
        await dialog_manager.switch_to(Profile.view)
    except ValueError:
        await message.answer(i18n.error_time_format())

async def save_coords(message: Message, message_input: MessageInput, dialog_manager: DialogManager):
    i18n = dialog_manager.middleware_data["i18n"]
    try:
        parts = message.text.replace(",", " ").split()
        if len(parts) != 2:
            raise ValueError
        lat, lon = map(float, parts)
        db: AsyncSession = dialog_manager.middleware_data["db"]
        await db.execute(update(User).where(User.id == message.from_user.id).values(birth_lat=lat, birth_lon=lon))
        await dialog_manager.switch_to(Profile.view)
    except ValueError:
        await message.answer(i18n.error_coords_format())

async def on_timezone_selected(callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    from .getters import TIMEZONE_MAPPING
    iana_tz = TIMEZONE_MAPPING.get(item_id)
    if iana_tz:
        db: AsyncSession = dialog_manager.middleware_data["db"]
        await db.execute(update(User).where(User.id == callback.from_user.id).values(timezone=iana_tz))
    await dialog_manager.switch_to(Profile.view)

async def on_gender_selected(callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    db: AsyncSession = dialog_manager.middleware_data["db"]
    await db.execute(update(User).where(User.id == callback.from_user.id).values(gender=Gender(item_id)))
    await dialog_manager.switch_to(Profile.view)

async def on_date_selected(callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, selected_date: date):
    db: AsyncSession = dialog_manager.middleware_data["db"]
    await db.execute(update(User).where(User.id == callback.from_user.id).values(birthday=selected_date))
    await dialog_manager.switch_to(Profile.view)
