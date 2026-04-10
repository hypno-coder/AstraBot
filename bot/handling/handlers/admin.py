from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from bot.handling.filters.is_admin import IsAdminFilter
from bot.handling.states.admin import AdminGroup
from bot.handling.states.referral import ReferralGroup


admin_router = Router()


@admin_router.message(Command("admin"), IsAdminFilter())
async def admin_cmd(msg: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminGroup.view, mode=StartMode.RESET_STACK)


@admin_router.callback_query(F.data == "open_referral")
async def open_referral_callback(callback: CallbackQuery, dialog_manager: DialogManager):
    """Handle the 'open referral' button in the milestone notification."""
    await callback.answer()
    await dialog_manager.start(ReferralGroup.view, mode=StartMode.NORMAL)
