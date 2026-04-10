from datetime import date
import httpx
from redis.asyncio import Redis
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import User
from bot.services.horoscope import get_horo, get_compare


ZODIAC_SIGNS = [
    ("aries",        "♈ Овен"),
    ("taurus",       "♉ Телец"),
    ("gemini",       "♊ Близнецы"),
    ("cancer",       "♋ Рак"),
    ("leo",          "♌ Лев"),
    ("virgo",        "♍ Дева"),
    ("libra",        "♎ Весы"),
    ("scorpio",      "♏ Скорпион"),
    ("sagittarius",  "♐ Стрелец"),
    ("capricorn",    "♑ Козерог"),
    ("aquarius",     "♒ Водолей"),
    ("pisces",       "♓ Рыбы"),
]

PERIOD_CHOICES = [
    ("today",    "Сегодня"),
    ("tomorrow", "Завтра"),
    ("week",     "Неделя"),
    ("month",    "Месяц"),
]


async def get_horoscope_data(dialog_manager: DialogManager, **kwargs):
    i18n = dialog_manager.middleware_data["i18n"]
    db: AsyncSession = dialog_manager.middleware_data["db"]
    client: httpx.AsyncClient = dialog_manager.middleware_data["http_client"]
    redis: Redis = dialog_manager.middleware_data["redis"]

    user = await db.scalar(select(User).where(User.id == dialog_manager.event.from_user.id))
    zodiac = user.zodiac_sign if user else None
    period = dialog_manager.dialog_data.get("period", "today")

    horo = {"title": "", "text": i18n.horo_error(), "finance": "", "health": "", "love": ""}
    if zodiac:
        horo = await get_horo(zodiac, period, client=client, redis=redis, fallback=i18n.horo_error())

    return {
        "horo_title": horo["title"],
        "horo_text": horo["text"],
        "horo_finance": f"💰 {i18n.horo_finance()}: {horo['finance']}" if horo["finance"] else "",
        "horo_health": f"❤️ {i18n.horo_health()}: {horo['health']}" if horo["health"] else "",
        "horo_love": f"💕 {i18n.horo_love()}: {horo['love']}" if horo["love"] else "",
        "horo_ask_dob": i18n.horo_ask_dob(),
        "horo_select_period": i18n.horo_select_period(),
        "horo_compat_btt": i18n.horo_compat_btt(),
        "horo_ask_own_gender": i18n.horo_ask_own_gender(),
        "horo_compat_male": i18n.horo_compat_male(),
        "horo_compat_female": i18n.horo_compat_female(),
        "horo_compat_zodiac": i18n.horo_compat_zodiac(),
        "btn_back": i18n.btn_back(),
        "periods": PERIOD_CHOICES,
        "zodiac_signs": ZODIAC_SIGNS,
        "current_period": period,
    }


async def get_compatibility_result(dialog_manager: DialogManager, **kwargs):
    i18n = dialog_manager.middleware_data["i18n"]
    db: AsyncSession = dialog_manager.middleware_data["db"]
    client: httpx.AsyncClient = dialog_manager.middleware_data["http_client"]
    redis: Redis = dialog_manager.middleware_data["redis"]

    user = await db.scalar(select(User).where(User.id == dialog_manager.event.from_user.id))
    user_zodiac = user.zodiac_sign if user else "aries"

    # user_gender is stored in dialog_data after they chose it or from their profile
    user_gender = dialog_manager.dialog_data.get("user_gender", "male")
    partner_zodiac = dialog_manager.dialog_data.get("partner_zodiac", "aries")

    # Mail.ru key always: female_zodiac_male_zodiac
    if user_gender == "female":
        female_z, male_z = user_zodiac, partner_zodiac
    else:
        female_z, male_z = partner_zodiac, user_zodiac

    result = await get_compare(female_z, male_z, client=client, redis=redis, fallback=i18n.horo_error())

    return {
        "compat_title": result["title"],
        "compat_text": result["text"],
        "btn_back": i18n.btn_back(),
    }
