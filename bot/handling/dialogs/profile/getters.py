from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User
from fluentogram import TranslatorRunner

async def get_profile_data(dialog_manager: DialogManager, **kwargs):
    i18n: TranslatorRunner = dialog_manager.middleware_data["i18n"]
    db: AsyncSession = dialog_manager.middleware_data["db"]
    user_id = dialog_manager.event.from_user.id

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    not_set = i18n.profile_not_set()

    fio = f"{user.fio} ✅" if user and user.fio else not_set
    
    gender_map = {
        "MALE": i18n.gender_male(),
        "FEMALE": i18n.gender_female(),
        "UNKNOWN": i18n.gender_unknown(),
    }
    
    gender_translated = gender_map.get(user.gender.value if user and user.gender else "")
    gender = f"{gender_translated} ✅" if gender_translated else not_set
    
    birth_city = f"{user.birth_city} ✅" if user and user.birth_city else not_set
    birthday = f"{user.birthday.strftime('%Y-%m-%d')} ✅" if user and user.birthday else not_set
    birth_time = f"{user.birth_time.strftime('%H:%M')} ✅" if user and user.birth_time else not_set
    coords = f"{user.birth_lat}, {user.birth_lon} ✅" if user and user.birth_lat and user.birth_lon else not_set
    timezone = f"{user.timezone} ✅" if user and user.timezone else not_set

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
        "profile_coords": i18n.profile_coords(coords=coords),
        "profile_timezone": i18n.profile_timezone(timezone=timezone),
        
        "btn_edit_fio": i18n.btn_edit_fio(),
        "btn_edit_gender": i18n.btn_edit_gender(),
        "btn_edit_city": i18n.btn_edit_city(),
        "btn_edit_birthday": i18n.btn_edit_birthday(), 
        "btn_edit_time": i18n.btn_edit_time(),
        "btn_edit_coords": i18n.btn_edit_coords(),
        "btn_edit_timezone": i18n.btn_edit_timezone(),
        "btn_back": i18n.btn_back(),

        "prompt_fio": i18n.prompt_fio(),
        "prompt_gender": i18n.prompt_gender(),
        "prompt_city": i18n.prompt_city(),
        "prompt_birthday": i18n.prompt_birthday(),
        "prompt_time": i18n.prompt_time(),
        "prompt_coords": i18n.prompt_coords(),
        "prompt_timezone": i18n.prompt_timezone(),
        
        "genders": genders
    }
