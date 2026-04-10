from aiogram.fsm.state import State, StatesGroup


class HoroscopeGroup(StatesGroup):
    ask_dob              = State()  # Calendar to capture DOB if zodiac_sign is missing
    view                 = State()  # Main horoscope window
    ask_own_gender       = State()  # Ask user's own gender if not set in DB
    compatibility_zodiac = State()  # Ask partner's zodiac sign (3x4 grid)
    compatibility_result = State()  # Show compatibility result
