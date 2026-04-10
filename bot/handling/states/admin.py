from aiogram.fsm.state import State, StatesGroup

class AdminGroup(StatesGroup):
    view = State()
    analytics = State()
    users = State()
    finance = State()
    broadcasting = State()
    tech_zone = State()
    confirm_action = State()
