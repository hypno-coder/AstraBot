from aiogram.fsm.state import State, StatesGroup


class HoroscopeGroup(StatesGroup):
    ask_dob             = State()   # Calendar to capture DOB if zodiac_sign is missing
    view                = State()   # Main horoscope window
    compatibility_gender = State()  # Ask partner's gender
    compatibility_zodiac = State()  # Ask partner's zodiac sign (3x4 grid)
    compatibility_result = State()  # Show compatibility result
