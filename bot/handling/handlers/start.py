from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database.models import User
from bot.handling.states import Main_menu
from bot.services.premium import grant_premium_days

start_router = Router()

REFERRAL_GOAL = 5
PREMIUM_DAYS = 30


@start_router.message(Command("start"))
async def handler(
    msg: Message,
    command: CommandObject,
    dialog_manager: DialogManager,
    db: AsyncSession,
    bot: Bot,
):
    user_id = msg.from_user.id

    # ── Referral deep link processing ─────────────────────────────────────────
    payload = command.args  # e.g. "1009034711"
    if payload and payload.isdigit():
        referrer_id = int(payload)

        # Guard 1: no self-referral
        # Guard 2: only if user doesn't already have a referrer (idempotent on /start restarts)
        if referrer_id != user_id:
            current_user = await db.scalar(select(User).where(User.id == user_id))
            if current_user and current_user.referred_by is None:
                # Mark referral link on new user
                await db.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(referred_by=referrer_id)
                )

                # Increment referrer's count
                referrer = await db.scalar(select(User).where(User.id == referrer_id))
                if referrer:
                    new_count = (referrer.referral_count or 0) + 1
                    await db.execute(
                        update(User)
                        .where(User.id == referrer_id)
                        .values(referral_count=new_count)
                    )

                    # Milestone check: every 5 successful referrals → 30 days premium
                    if new_count % REFERRAL_GOAL == 0:
                        new_until = await grant_premium_days(referrer_id, PREMIUM_DAYS, db)
                        until_str = new_until.strftime("%d.%m.%Y")

                        # Notify referrer with a button to open their referral dashboard
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(
                                text="💎 Моя рефералка",
                                callback_data="open_referral"
                            )
                        ]])
                        await bot.send_message(
                            chat_id=referrer_id,
                            text=(
                                f"🎉 Друг #{new_count} присоединился! "
                                f"Вы заработали {PREMIUM_DAYS} дней Premium!\n"
                                f"✅ Premium активен до: {until_str}"
                            ),
                            reply_markup=keyboard,
                        )

    # ── Always open main menu ──────────────────────────────────────────────────
    await dialog_manager.start(Main_menu.start, mode=StartMode.RESET_STACK)
