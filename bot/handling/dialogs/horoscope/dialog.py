import operator

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Button, Row, Group, SwitchTo, Select, Cancel, Back
)
from bot.widgets.localized_calendar import LocalizedCalendar
from aiogram_dialog.widgets.text import Format

from bot.handling.states.horoscope import HoroscopeGroup
from .getters import get_horoscope_data, get_compatibility_result
from .handlers import (
    on_dob_selected, on_period_selected, on_compat_clicked,
    on_own_gender_selected, on_partner_zodiac_selected
)

dialog = Dialog(
    # ── Window 1: Ask DOB if no zodiac sign ──────────────────────────────────
    Window(
        Format("{horo_ask_dob}"),
        LocalizedCalendar(id="horo_calendar", on_click=on_dob_selected),
        Cancel(Format("{btn_back}")),
        state=HoroscopeGroup.ask_dob,
        getter=get_horoscope_data,
    ),

    # ── Window 2: Horoscope view ─────────────────────────────────────────────
    Window(
        Format("<b>{horo_title}</b>\n\n{horo_text}\n\n{horo_finance}\n{horo_health}\n{horo_love}"),
        Row(
            Select(
                Format("{item[1]}"),
                id="period_sel",
                item_id_getter=operator.itemgetter(0),
                items="periods",
                on_click=on_period_selected,
            ),
        ),
        Button(Format("{horo_compat_btt}"), id="go_compat", on_click=on_compat_clicked),
        Cancel(Format("{btn_back}")),
        state=HoroscopeGroup.view,
        getter=get_horoscope_data,
    ),

    # ── Window 3: Ask USER's own gender (only if not set in profile) ─────────
    Window(
        Format("{horo_ask_own_gender}"),
        Row(
            Button(
                Format("{horo_compat_male}"), id="og_male",
                on_click=lambda c, w, m: on_own_gender_selected(c, w, m, "male")
            ),
            Button(
                Format("{horo_compat_female}"), id="og_female",
                on_click=lambda c, w, m: on_own_gender_selected(c, w, m, "female")
            ),
        ),
        Back(Format("{btn_back}")),
        state=HoroscopeGroup.ask_own_gender,
        getter=get_horoscope_data,
    ),

    # ── Window 4: Compatibility – partner zodiac sign (3x4 grid) ────────────
    Window(
        Format("{horo_compat_zodiac}"),
        Group(
            Select(
                Format("{item[1]}"),
                id="zodiac_sel",
                item_id_getter=operator.itemgetter(0),
                items="zodiac_signs",
                on_click=on_partner_zodiac_selected,
            ),
            width=3,
        ),
        Back(Format("{btn_back}")),
        state=HoroscopeGroup.compatibility_zodiac,
        getter=get_horoscope_data,
    ),

    # ── Window 5: Compatibility result ──────────────────────────────────────
    Window(
        Format("<b>{compat_title}</b>\n\n{compat_text}"),
        SwitchTo(Format("{btn_back}"), id="compat_back", state=HoroscopeGroup.view),
        state=HoroscopeGroup.compatibility_result,
        getter=get_compatibility_result,
    ),
)
