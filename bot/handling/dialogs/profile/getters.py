from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User
from fluentogram import TranslatorRunner

TIMEZONE_MAPPING = {
    "-12": "Etc/GMT+12",
    "-11": "Pacific/Midway",
    "-10": "Pacific/Honolulu",
    "-9": "America/Anchorage",
    "-8": "America/Los_Angeles",
    "-7": "America/Denver",
    "-6": "America/Chicago",
    "-5": "America/New_York",
    "-4": "America/Caracas",
    "-3": "America/Argentina/Buenos_Aires",
    "-2": "Atlantic/South_Georgia",
    "-1": "Atlantic/Azores",
    "0": "Europe/London",
    "+1": "Europe/Paris",
    "+2": "Europe/Kyiv",
    "+3": "Europe/Moscow",
    "+4": "Asia/Dubai",
    "+5": "Asia/Yekaterinburg",
    "+6": "Asia/Omsk",
    "+7": "Asia/Novosibirsk",
    "+8": "Asia/Singapore",
    "+9": "Asia/Tokyo",
    "+10": "Australia/Sydney",
    "+11": "Pacific/Guadalcanal",
    "+12": "Pacific/Fiji",
    "+13": "Pacific/Tongatapu",
    "+14": "Pacific/Kiritimati",
}

REVERSE_TZ = {v: k for k, v in TIMEZONE_MAPPING.items()}

async def get_profile_data(dialog_manager: DialogManager, **kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    db: AsyncSession = dialog_manager.middleware_data["db"]
    user_id = dialog_manager.event.from_user.id

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    lang = dialog_manager.middleware_data.get("user_language", "ru")
    date_fmt = "%d.%m.%Y" if lang == "ru" else "%Y.%m.%d"

    not_set = i18n.profile_not_set()

    fio = f"{user.fio} ✅" if user and user.fio else not_set
    
    gender_map = {
        "MALE": i18n.gender_male(),
        "FEMALE": i18n.gender_female(),
        "UNKNOWN": i18n.gender_unknown(),
    }
    
    gender_translated = gender_map.get(user.gender.value if user and user.gender else "")
    gender = f"{gender_translated} ✅" if gender_translated else not_set
    
    if user and user.birth_city:
        if user.birth_lat and user.birth_lon:
            birth_city = f"{user.birth_city} ({user.birth_lat}, {user.birth_lon}) ✅"
        else:
            birth_city = f"{user.birth_city} ✅"
    else:
        birth_city = not_set
        
    birthday_raw = f"{user.birthday.strftime(date_fmt)}" if user and user.birthday else None
    zodiac_emoji = {
        "aries": "♈", "taurus": "♉", "gemini": "♊", "cancer": "♋",
        "leo": "♌", "virgo": "♍", "libra": "♎", "scorpio": "♏",
        "sagittarius": "♐", "capricorn": "♑", "aquarius": "♒", "pisces": "♓",
    }
    if birthday_raw:
        zodiac = user.zodiac_sign or ""
        zodiac_part = f" {zodiac_emoji.get(zodiac, '')}" if zodiac else ""
        birthday = f"{birthday_raw}{zodiac_part} ✅"
    else:
        birthday = not_set
    birth_time = f"{user.birth_time.strftime('%H:%M')} ✅" if user and user.birth_time else not_set
    
    if user and user.timezone:
        tz_offset = REVERSE_TZ.get(user.timezone, user.timezone)
        timezone = f"UTC {tz_offset} ✅" if tz_offset in TIMEZONE_MAPPING else f"{tz_offset} ✅"
    else:
        timezone = not_set

    # Prepare timezone choices for the Select widget
    timezones = [(k, f"UTC {k}") for k in TIMEZONE_MAPPING.keys()]

    # Also prepare gender choices for the Select widget
    genders = [
        ("MALE", i18n.gender_male()),
        ("FEMALE", i18n.gender_female()),
        ("UNKNOWN", i18n.gender_unknown()),
    ]

    return {
        "profile_title": i18n.profile_title(),
        "profile_fio": i18n.profile_fio(fio=fio),
        "profile_gender": i18n.profile_gender(gender=gender),
        "profile_city": i18n.profile_city(birth_city=birth_city),
        "profile_birthday": i18n.profile_birthday(birthday=birthday),
        "profile_time": i18n.profile_time(birth_time=birth_time),
        "profile_timezone": i18n.profile_timezone(timezone=timezone),
        
        "btn_edit_fio": i18n.btn_edit_fio(),
        "btn_edit_gender": i18n.btn_edit_gender(),
        "btn_edit_city": i18n.btn_edit_city(),
        "btn_edit_birthday": i18n.btn_edit_birthday(), 
        "btn_edit_time": i18n.btn_edit_time(),
        "btn_edit_timezone": i18n.btn_edit_timezone(),
        "btn_back": i18n.btn_back(),

        "prompt_fio": i18n.prompt_fio(),
        "prompt_gender": i18n.prompt_gender(),
        "prompt_city": i18n.prompt_city(),
        "prompt_birthday": i18n.prompt_birthday(),
        "prompt_time": i18n.prompt_time(),
        "prompt_timezone": i18n.prompt_timezone(),
        
        "confirm_city_prompt": i18n.confirm_city_prompt(
            address=dialog_manager.dialog_data.get("address", "")
        ),
        "btn_yes_city": i18n.btn_yes_city(),
        "btn_no_city": i18n.btn_no_city(),
        
        "genders": genders,
        "timezones": timezones
    }
