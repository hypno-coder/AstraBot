from aiogram import Router
from aiogram.types import ChatMemberUpdated

sub_router = Router()

# этот роутер нужен для того, что бы вызывался апдейт dp.my_chat_member
@sub_router.my_chat_member()
async def _noop(_: ChatMemberUpdated):
    pass
