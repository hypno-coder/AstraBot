from typing import Any
from datetime import date

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from database.models import User, Gender
from bot.handling.states.horoscope import HoroscopeGroup
from bot.services.zodiac import calculate_zodiac


async def on_dob_selected(
    callback: CallbackQuery, widget: Any,
    dialog_manager: DialogManager, selected_date: date
):
    """Save birthday, calculate zodiac, save to DB, switch to horoscope view."""
    db: AsyncSession = dialog_manager.middleware_data["db"]
    zodiac = calculate_zodiac(selected_date)
    await db.execute(
        update(User)
        .where(User.id == callback.from_user.id)
        .values(birthday=selected_date, zodiac_sign=zodiac)
    )
    await dialog_manager.switch_to(HoroscopeGroup.view)


async def on_period_selected(
    callback: CallbackQuery, widget: Any,
    dialog_manager: DialogManager, item_id: str
):
    """Update period in dialog_data to re-render the horoscope."""
    dialog_manager.dialog_data["period"] = item_id


async def on_compat_clicked(
    callback: CallbackQuery, widget: Any,
    dialog_manager: DialogManager
):
    """Entry to compatibility: check if user's gender is set, otherwise ask."""
    from sqlalchemy import select
    db: AsyncSession = dialog_manager.middleware_data["db"]
    user = await db.scalar(select(User).where(User.id == callback.from_user.id))
    if user and user.gender and user.gender.value in ("MALE", "FEMALE"):
        # gender already known — skip to zodiac selection
        dialog_manager.dialog_data["user_gender"] = user.gender.value.lower()
        await dialog_manager.switch_to(HoroscopeGroup.compatibility_zodiac)
    else:
        await dialog_manager.switch_to(HoroscopeGroup.ask_own_gender)


async def on_own_gender_selected(
    callback: CallbackQuery, widget: Any,
    dialog_manager: DialogManager, item_id: str
):
    """Save user's own gender to DB, then proceed to partner zodiac selection."""
    db: AsyncSession = dialog_manager.middleware_data["db"]
    await db.execute(
        update(User)
        .where(User.id == callback.from_user.id)
        .values(gender=Gender(item_id.upper()))
    )
    dialog_manager.dialog_data["user_gender"] = item_id  # "male" or "female"
    await dialog_manager.switch_to(HoroscopeGroup.compatibility_zodiac)


async def on_partner_zodiac_selected(
    callback: CallbackQuery, widget: Any,
    dialog_manager: DialogManager, item_id: str
):
    dialog_manager.dialog_data["partner_zodiac"] = item_id
    await dialog_manager.switch_to(HoroscopeGroup.compatibility_result)
