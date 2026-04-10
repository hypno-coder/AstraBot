from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Cancel, Back
from aiogram_dialog.widgets.text import Format

from bot.handling.states.referral import ReferralGroup
from .getters import get_referral_data

dialog = Dialog(
    # ── Window 1: Main referral dashboard ────────────────────────────────────
    Window(
        Format(
            "{ref_title}\n\n"
            "{ref_progress}\n"
            "{ref_premium_status}\n\n"
            "{ref_body}"
        ),
        SwitchTo(Format("{ref_invite_btt}"), id="ref_invite", state=ReferralGroup.invite),
        Cancel(Format("{btn_back}")),
        state=ReferralGroup.view,
        getter=get_referral_data,
    ),

    # ── Window 2: Invite link screen ─────────────────────────────────────────
    Window(
        Format(
            "🔗 {ref_link_title}\n\n"
            "<code>{invite_link}</code>\n\n"
            "{ref_link_hint}"
        ),
        Back(Format("{btn_back}")),
        state=ReferralGroup.invite,
        getter=get_referral_data,
    ),
)
