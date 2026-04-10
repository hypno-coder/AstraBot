from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Format

from bot.handling.states.referral import ReferralGroup
from .getters import get_referral_data
from .handlers import on_invite

dialog = Dialog(
    Window(
        Format(
            "{ref_title}\n\n"
            "{ref_progress}\n"
            "{ref_premium_status}\n\n"
            "{ref_body}"
        ),
        Button(Format("{ref_invite_btt}"), id="ref_invite", on_click=on_invite),
        Cancel(Format("{btn_back}")),
        state=ReferralGroup.view,
        getter=get_referral_data,
    )
)
