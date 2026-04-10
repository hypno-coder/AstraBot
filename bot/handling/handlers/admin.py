from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode

from bot.handling.filters.is_admin import IsAdminFilter
from bot.handling.states.admin import AdminGroup

admin_router = Router()
admin_router.message.filter(IsAdminFilter())

@admin_router.message(Command("admin"))
async def start_admin(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminGroup.view, mode=StartMode.RESET_STACK)
