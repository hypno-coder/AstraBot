from typing import Any
from datetime import date

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from database.models import User
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
    # stay on same window — getter will re-run with new period


async def on_partner_gender_selected(
    callback: CallbackQuery, widget: Any,
    dialog_manager: DialogManager, item_id: str
):
    dialog_manager.dialog_data["partner_gender"] = item_id
    await dialog_manager.switch_to(HoroscopeGroup.compatibility_zodiac)


async def on_partner_zodiac_selected(
    callback: CallbackQuery, widget: Any,
    dialog_manager: DialogManager, item_id: str
):
    dialog_manager.dialog_data["partner_zodiac"] = item_id
    await dialog_manager.switch_to(HoroscopeGroup.compatibility_result)
