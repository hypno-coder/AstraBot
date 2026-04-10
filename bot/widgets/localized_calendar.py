"""
Localized Calendar widget for aiogram-dialog.
Overrides _init_views to inject locale-aware Text objects for:
  - Days view: header, weekday abbreviations, prev/next month nav buttons
  - Months view: month name grid cells (month_text, this_month_text)
Language is read from middleware_data["user_language"] at render time.
"""
from __future__ import annotations

from datetime import date
from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView,
    CalendarMonthView,
    CalendarScope,
    CalendarScopeView,
    CalendarYearsView,
)
from aiogram_dialog.widgets.text import Text

# ──────────────────────────────────────────────
# Data tables
# ──────────────────────────────────────────────
_MONTHS_RU = [
    "Январь", "Февраль", "Март", "Апрель",
    "Май", "Июнь", "Июль", "Август",
    "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]
_MONTHS_EN = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December",
]
_WEEKDAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
_WEEKDAYS_EN = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def _lang(manager: DialogManager) -> str:
    return manager.middleware_data.get("user_language", "ru")


def _month_name(d: date, manager: DialogManager) -> str:
    months = _MONTHS_RU if _lang(manager) == "ru" else _MONTHS_EN
    return months[d.month - 1]


# ──────────────────────────────────────────────
# Days-view Text classes
# ──────────────────────────────────────────────

class _DaysHeaderText(Text):
    """🗓 Апрель 2026 / 🗓 April 2026"""
    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        d: date = data["date"]
        return f"🗓 {_month_name(d, manager)} {d.year}"


class _WeekdayText(Text):
    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        d: date = data["date"]
        days = _WEEKDAYS_RU if _lang(manager) == "ru" else _WEEKDAYS_EN
        return days[d.weekday()]


class _PrevMonthText(Text):
    """<< Март 2026 / << March 2026"""
    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        d: date = data["date"]
        return f"<< {_month_name(d, manager)} {d.year}"


class _NextMonthText(Text):
    """Май 2026 >> / May 2026 >>"""
    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        d: date = data["date"]
        return f"{_month_name(d, manager)} {d.year} >>"


# ──────────────────────────────────────────────
# Months-view Text classes (the month selection grid)
# ──────────────────────────────────────────────

class _MonthText(Text):
    """Рядовая ячейка месяца: Январь / January"""
    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        d: date = data["date"]
        return _month_name(d, manager)


class _ThisMonthText(Text):
    """Текущий месяц: [ Апрель ] / [ April ]"""
    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        d: date = data["date"]
        return f"[ {_month_name(d, manager)} ]"


# ──────────────────────────────────────────────
# Widget
# ──────────────────────────────────────────────

class LocalizedCalendar(Calendar):
    """
    Drop-in replacement for Calendar with full RU/EN localization.
    Language is taken from middleware_data["user_language"].
    """

    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                header_text=_DaysHeaderText(),
                weekday_text=_WeekdayText(),
                prev_month_text=_PrevMonthText(),
                next_month_text=_NextMonthText(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=_MonthText(),
                this_month_text=_ThisMonthText(),
            ),
            CalendarScope.YEARS: CalendarYearsView(self._item_callback_data),
        }
