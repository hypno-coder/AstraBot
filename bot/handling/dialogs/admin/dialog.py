from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, Group, SwitchTo, Cancel, Back
from aiogram_dialog.widgets.text import Format

from bot.handling.states.admin import AdminGroup
from .getters import get_admin_data
from .handlers import on_lang_toggle, dummy_action

dialog = Dialog(
    Window(
        Format("{admin_header}\n"),
        Button(Format("{lang_toggle}"), id="lang_toggle", on_click=on_lang_toggle),
        Group(
            SwitchTo(Format("{btn_admin_analytics}"), id="s_analytics", state=AdminGroup.analytics),
            SwitchTo(Format("{btn_admin_users}"), id="s_users", state=AdminGroup.users),
            SwitchTo(Format("{btn_admin_finance}"), id="s_finance", state=AdminGroup.finance),
            SwitchTo(Format("{btn_admin_broadcast}"), id="s_broadcast", state=AdminGroup.broadcasting),
            SwitchTo(Format("{btn_admin_tech}"), id="s_tech", state=AdminGroup.tech_zone),
        ),
        Cancel(Format("{admin_back}")),
        state=AdminGroup.view,
        getter=get_admin_data
    ),
    Window(
        Format("📊 {btn_admin_analytics}\n"),
        Button(Format("📈 {stub_analytics_stats}"), id="a_stats", on_click=dummy_action),
        Button(Format("🪙 {stub_analytics_tokens}"), id="a_tokens", on_click=dummy_action),
        Button(Format("💰 {stub_analytics_payments}"), id="a_pay", on_click=dummy_action),
        SwitchTo(Format("{admin_back}"), id="back", state=AdminGroup.view),
        state=AdminGroup.analytics,
        getter=get_admin_data
    ),
    Window(
        Format("👥 {btn_admin_users}\n"),
        Button(Format("🔍 {stub_users_search}"), id="u_search", on_click=dummy_action),
        Button(Format("🚫 {stub_users_block}"), id="u_block", on_click=dummy_action),
        Button(Format("💬 {stub_users_reply}"), id="u_reply", on_click=dummy_action),
        Button(Format("🗨 {stub_users_dialogs}"), id="u_dialogs", on_click=dummy_action),
        SwitchTo(Format("{admin_back}"), id="back", state=AdminGroup.view),
        state=AdminGroup.users,
        getter=get_admin_data
    ),
    Window(
        Format("💳 {btn_admin_finance}\n"),
        Button(Format("🔍 {stub_finance_search}"), id="f_search", on_click=dummy_action),
        Button(Format("🎁 {stub_finance_gift}"), id="f_gift", on_click=dummy_action),
        Button(Format("🪙 {stub_finance_prices}"), id="f_prices", on_click=dummy_action),
        Button(Format("🎟 {stub_finance_promos}"), id="f_promos", on_click=dummy_action),
        SwitchTo(Format("{admin_back}"), id="back", state=AdminGroup.view),
        state=AdminGroup.finance,
        getter=get_admin_data
    ),
    Window(
        Format("📢 {btn_admin_broadcast}\n"),
        Button(Format("📝 {stub_broadcast_create}"), id="b_create", on_click=dummy_action),
        Button(Format("📈 {stub_broadcast_stats}"), id="b_stats", on_click=dummy_action),
        SwitchTo(Format("{admin_back}"), id="back", state=AdminGroup.view),
        state=AdminGroup.broadcasting,
        getter=get_admin_data
    ),
    Window(
        Format("🛠 {btn_admin_tech}\n"),
        SwitchTo(Format("🔧 {stub_tech_maintenance}"), id="t_maint", state=AdminGroup.confirm_action),
        Button(Format("👮‍♂️ {stub_tech_admin}"), id="t_admin", on_click=dummy_action),
        SwitchTo(Format("🔄 {stub_tech_restart_bot}"), id="t_res_bot", state=AdminGroup.confirm_action),
        SwitchTo(Format("🔁 {stub_tech_restart_server}"), id="t_res_srv", state=AdminGroup.confirm_action),
        SwitchTo(Format("🛑 {stub_tech_block_bot}"), id="t_block", state=AdminGroup.confirm_action),
        SwitchTo(Format("{admin_back}"), id="back", state=AdminGroup.view),
        state=AdminGroup.tech_zone,
        getter=get_admin_data
    ),
    Window(
        Format("{confirm_action_prompt}"),
        Row(
            Button(Format("{btn_confirm_yes}"), id="confirm_yes", on_click=dummy_action),
            Back(Format("{btn_confirm_no}")),
        ),
        state=AdminGroup.confirm_action,
        getter=get_admin_data
    )
)
