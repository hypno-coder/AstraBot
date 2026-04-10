from datetime import datetime, timezone

from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User

REFERRAL_GOAL = 5


async def get_referral_data(dialog_manager: DialogManager, **kwargs):
    i18n = dialog_manager.middleware_data["i18n"]
    db: AsyncSession = dialog_manager.middleware_data["db"]
    bot = dialog_manager.middleware_data["bot"]

    user = await db.scalar(select(User).where(User.id == dialog_manager.event.from_user.id))

    referral_count = user.referral_count if user else 0
    current_in_cycle = referral_count % REFERRAL_GOAL
    bot_info = await bot.get_me()

    # Premium status (always compare with UTC)
    now = datetime.now(timezone.utc)
    if user and user.premium_until and user.premium_until > now:
        premium_str = i18n.ref_premium_active(date=user.premium_until.strftime("%d.%m.%Y"))
    else:
        premium_str = i18n.ref_premium_inactive()

    return {
        "ref_title": i18n.ref_title(),
        "ref_progress": i18n.ref_progress(current=current_in_cycle, goal=REFERRAL_GOAL),
        "ref_premium_status": premium_str,
        "ref_body": i18n.ref_body(),
        "ref_invite_btt": i18n.ref_invite_btt(),
        "btn_back": i18n.btn_back(),
        # Inline query text for SwitchInlineQueryCurrentChat / invite link
        "invite_link": f"https://t.me/{bot_info.username}?start={dialog_manager.event.from_user.id}",
        "ref_invite_text": i18n.ref_invite_share_text(bot_username=bot_info.username, user_id=dialog_manager.event.from_user.id),
    }
