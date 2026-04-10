from aiogram.fsm.state import State, StatesGroup

class Profile(StatesGroup):
    view = State()
    edit_fio = State()
    edit_gender = State()
    edit_birth_city = State()
    edit_birthday = State()
    edit_birth_time = State()
    edit_coords = State()
    edit_timezone = State()
