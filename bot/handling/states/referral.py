from aiogram.fsm.state import State, StatesGroup


class ReferralGroup(StatesGroup):
    view   = State()
    invite = State()
