import operator

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, Group, SwitchTo, Select, Cancel, ScrollingGroup
from bot.widgets.localized_calendar import LocalizedCalendar
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput

from bot.handling.states.profile import Profile
from bot.handling.states.main_menu import Main_menu
from .getters import get_profile_data
from .handlers import (
    save_fio, save_city, save_time, on_city_confirmed,
    on_timezone_selected, on_gender_selected, on_date_selected
)

dialog = Dialog(
    Window(
        Format("{profile_title}\n"),
        Format("{profile_fio}"),
        Format("{profile_gender}"),
        Format("{profile_city}"),
        Format("{profile_birthday}"),
        Format("{profile_time}"),
        Format("{profile_timezone}\n"),
        Group(
            Row(
                SwitchTo(Format("{btn_edit_fio}"), id="set_fio", state=Profile.edit_fio),
                SwitchTo(Format("{btn_edit_gender}"), id="set_gender", state=Profile.edit_gender),
            ),
            Row(
                SwitchTo(Format("{btn_edit_city}"), id="set_city", state=Profile.edit_birth_city),
                SwitchTo(Format("{btn_edit_birthday}"), id="set_bd", state=Profile.edit_birthday),
            ),
            Row(
                SwitchTo(Format("{btn_edit_time}"), id="set_time", state=Profile.edit_birth_time),
                SwitchTo(Format("{btn_edit_timezone}"), id="set_tz", state=Profile.edit_timezone),
            ),
        ),
        Cancel(Format("{btn_back}")),
        state=Profile.view,
        getter=get_profile_data
    ),
    Window(
        Format("{prompt_fio}"),
        MessageInput(save_fio),
        SwitchTo(Format("{btn_back}"), id="back", state=Profile.view),
        state=Profile.edit_fio,
        getter=get_profile_data
    ),
    Window(
        Format("{prompt_gender}"),
        Select(
            Format("{item[1]}"),
            id="s_gender",
            item_id_getter=operator.itemgetter(0),
            items="genders",
            on_click=on_gender_selected
        ),
        SwitchTo(Format("{btn_back}"), id="back", state=Profile.view),
        state=Profile.edit_gender,
        getter=get_profile_data
    ),
    Window(
        Format("{prompt_city}"),
        MessageInput(save_city),
        SwitchTo(Format("{btn_back}"), id="back", state=Profile.view),
        state=Profile.edit_birth_city,
        getter=get_profile_data
    ),
    Window(
        Format("{confirm_city_prompt}"),
        Row(
            Button(Format("{btn_yes_city}"), id="yes_city", on_click=on_city_confirmed),
            SwitchTo(Format("{btn_no_city}"), id="no_city", state=Profile.edit_birth_city),
        ),
        state=Profile.confirm_city,
        getter=get_profile_data
    ),
    Window(
        Format("{prompt_birthday}"),
        LocalizedCalendar(id="calendar", on_click=on_date_selected),
        SwitchTo(Format("{btn_back}"), id="back", state=Profile.view),
        state=Profile.edit_birthday,
        getter=get_profile_data
    ),
    Window(
        Format("{prompt_time}"),
        MessageInput(save_time),
        SwitchTo(Format("{btn_back}"), id="back", state=Profile.view),
        state=Profile.edit_birth_time,
        getter=get_profile_data
    ),
    Window(
        Format("{prompt_timezone}"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="s_tz",
                item_id_getter=operator.itemgetter(0),
                items="timezones",
                on_click=on_timezone_selected
            ),
            id="tz_sg",
            width=3,
            height=6,
        ),
        SwitchTo(Format("{btn_back}"), id="back", state=Profile.view),
        state=Profile.edit_timezone,
        getter=get_profile_data
    )
)
