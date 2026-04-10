from typing import Any
from datetime import datetime, date

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter

from database.models import User, Gender
from bot.handling.states.profile import Profile

async def save_fio(message: Message, message_input: MessageInput, dialog_manager: DialogManager):
    db: AsyncSession = dialog_manager.middleware_data["db"]
    await db.execute(update(User).where(User.id == message.from_user.id).values(fio=message.text))
    await dialog_manager.switch_to(Profile.view)

async def save_city(message: Message, message_input: MessageInput, dialog_manager: DialogManager):
    i18n = dialog_manager.middleware_data["i18n"]
    city_name = message.text.strip()
    
    async with Nominatim(
        user_agent="Astrabot/1.0",
        adapter_factory=AioHTTPAdapter,
    ) as geolocator:
        location = await geolocator.geocode(city_name, language="ru")
        
        if location:
            dialog_manager.dialog_data["address"] = location.address
            dialog_manager.dialog_data["lat"] = location.latitude
            dialog_manager.dialog_data["lon"] = location.longitude
            dialog_manager.dialog_data["city_name"] = city_name
            await dialog_manager.switch_to(Profile.confirm_city)
        else:
            await message.answer(i18n.error_city_not_found())

async def on_city_confirmed(callback: CallbackQuery, button: Any, dialog_manager: DialogManager):
    db: AsyncSession = dialog_manager.middleware_data["db"]
    lat = dialog_manager.dialog_data["lat"]
    lon = dialog_manager.dialog_data["lon"]
    city = dialog_manager.dialog_data["city_name"]
    await db.execute(update(User).where(User.id == callback.from_user.id).values(birth_city=city, birth_lat=lat, birth_lon=lon))
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
    from bot.services.zodiac import calculate_zodiac
    zodiac = calculate_zodiac(selected_date)
    await db.execute(
        update(User)
        .where(User.id == callback.from_user.id)
        .values(birthday=selected_date, zodiac_sign=zodiac)
    )
    await dialog_manager.switch_to(Profile.view)
