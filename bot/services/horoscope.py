"""
Async horoscope service.
- Stateless: zodiac & period passed as arguments
- Redis TTL cache expiring at 23:59:59 of the current Moscow day
- Shared httpx.AsyncClient passed via DI (initialized in app lifespan)
- Max 3 retries with exponential backoff; safe fallback on failure
"""
from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone, timedelta

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from redis.asyncio import Redis

# ──────────────────────────────────────────────
# Mail.ru URL patterns
# ──────────────────────────────────────────────
_HORO_URL = "https://horo.mail.ru/prediction/{zodiac}/{period}/"
_COMPAT_URL = "https://horo.mail.ru/compatibility/zodiac/{compat_id}/"

# Ported from legacy lexicon
HORO_STARS = {
    "1 из 5": "★ ☆ ☆ ☆ ☆",
    "2 из 5": "★ ★ ☆ ☆ ☆",
    "3 из 5": "★ ★ ★ ☆ ☆",
    "4 из 5": "★ ★ ★ ★ ☆",
    "5 из 5": "★ ★ ★ ★ ★",
}

# Compat table: key = "{female_sign}_{male_sign}" -> Mail.ru numeric ID
HORO_COMPAT: dict[str, int] = {
    "aries_aries": 1, "aries_taurus": 2, "aries_gemini": 3, "aries_cancer": 4,
    "aries_leo": 5, "aries_virgo": 6, "aries_libra": 7, "aries_scorpio": 8,
    "aries_sagittarius": 9, "aries_capricorn": 10, "aries_aquarius": 11, "aries_pisces": 12,
    "taurus_aries": 13, "taurus_taurus": 14, "taurus_gemini": 15, "taurus_cancer": 16,
    "taurus_leo": 17, "taurus_virgo": 18, "taurus_libra": 19, "taurus_scorpio": 20,
    "taurus_sagittarius": 21, "taurus_capricorn": 22, "taurus_aquarius": 23, "taurus_pisces": 24,
    "gemini_aries": 25, "gemini_taurus": 26, "gemini_gemini": 27, "gemini_cancer": 28,
    "gemini_leo": 29, "gemini_virgo": 30, "gemini_libra": 31, "gemini_scorpio": 32,
    "gemini_sagittarius": 33, "gemini_capricorn": 34, "gemini_aquarius": 35, "gemini_pisces": 36,
    "cancer_aries": 37, "cancer_taurus": 38, "cancer_gemini": 39, "cancer_cancer": 40,
    "cancer_leo": 41, "cancer_virgo": 42, "cancer_libra": 43, "cancer_scorpio": 44,
    "cancer_sagittarius": 45, "cancer_capricorn": 46, "cancer_aquarius": 47, "cancer_pisces": 48,
    "leo_aries": 49, "leo_taurus": 50, "leo_gemini": 51, "leo_cancer": 52,
    "leo_leo": 53, "leo_virgo": 54, "leo_libra": 55, "leo_scorpio": 56,
    "leo_sagittarius": 57, "leo_capricorn": 58, "leo_aquarius": 59, "leo_pisces": 60,
    "virgo_aries": 61, "virgo_taurus": 62, "virgo_gemini": 63, "virgo_cancer": 64,
    "virgo_leo": 65, "virgo_virgo": 66, "virgo_libra": 67, "virgo_scorpio": 68,
    "virgo_sagittarius": 69, "virgo_capricorn": 70, "virgo_aquarius": 71, "virgo_pisces": 72,
    "libra_aries": 73, "libra_taurus": 74, "libra_gemini": 75, "libra_cancer": 76,
    "libra_leo": 77, "libra_virgo": 78, "libra_libra": 79, "libra_scorpio": 80,
    "libra_sagittarius": 81, "libra_capricorn": 82, "libra_aquarius": 83, "libra_pisces": 84,
    "scorpio_aries": 85, "scorpio_taurus": 86, "scorpio_gemini": 87, "scorpio_cancer": 88,
    "scorpio_leo": 89, "scorpio_virgo": 90, "scorpio_libra": 91, "scorpio_scorpio": 92,
    "scorpio_sagittarius": 93, "scorpio_capricorn": 94, "scorpio_aquarius": 95, "scorpio_pisces": 96,
    "sagittarius_aries": 97, "sagittarius_taurus": 98, "sagittarius_gemini": 99, "sagittarius_cancer": 100,
    "sagittarius_leo": 101, "sagittarius_virgo": 102, "sagittarius_libra": 103, "sagittarius_scorpio": 104,
    "sagittarius_sagittarius": 105, "sagittarius_capricorn": 106, "sagittarius_aquarius": 107, "sagittarius_pisces": 108,
    "capricorn_aries": 109, "capricorn_taurus": 110, "capricorn_gemini": 111, "capricorn_cancer": 112,
    "capricorn_leo": 113, "capricorn_virgo": 114, "capricorn_libra": 115, "capricorn_scorpio": 116,
    "capricorn_sagittarius": 117, "capricorn_capricorn": 118, "capricorn_aquarius": 119, "capricorn_pisces": 120,
    "aquarius_aries": 121, "aquarius_taurus": 122, "aquarius_gemini": 123, "aquarius_cancer": 124,
    "aquarius_leo": 125, "aquarius_virgo": 126, "aquarius_libra": 127, "aquarius_scorpio": 128,
    "aquarius_sagittarius": 129, "aquarius_capricorn": 130, "aquarius_aquarius": 131, "aquarius_pisces": 132,
    "pisces_aries": 133, "pisces_taurus": 134, "pisces_gemini": 135, "pisces_cancer": 136,
    "pisces_leo": 137, "pisces_virgo": 138, "pisces_libra": 139, "pisces_scorpio": 140,
    "pisces_sagittarius": 141, "pisces_capricorn": 142, "pisces_aquarius": 143, "pisces_pisces": 144,
}


def _random_headers() -> dict[str, str]:
    ua = UserAgent()
    return {
        "User-Agent": ua.random,
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }


def _ttl_until_midnight() -> int:
    """Seconds remaining until 23:59:59 Moscow time."""
    msk = timezone(timedelta(hours=3))
    now = datetime.now(msk)
    midnight = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return max(int((midnight - now).total_seconds()), 1)


async def _fetch(client: httpx.AsyncClient, url: str) -> bytes | None:
    """Fetch URL with max-3 retries and exponential backoff."""
    for attempt in range(3):
        try:
            resp = await client.get(url, headers=_random_headers(), follow_redirects=True, timeout=10.0)
            if resp.status_code == 200:
                return resp.content
        except Exception:
            pass
        await asyncio.sleep(2 ** attempt)
    return None


async def get_horo(
    zodiac: str,
    period: str,
    *,
    client: httpx.AsyncClient,
    redis: Redis,
    fallback: str = "⚠️ Гороскоп временно недоступен. Попробуйте позже.",
) -> dict[str, str]:
    """Fetch horoscope text + ratings. Cached in Redis until end of day."""
    cache_key = f"horo:{zodiac}:{period}"
    import json

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    url = _HORO_URL.format(zodiac=zodiac, period=period)
    content = await _fetch(client, url)
    if not content:
        return {"title": "", "text": fallback, "finance": "", "health": "", "love": ""}

    soup = BeautifulSoup(content, "lxml")
    text_el = soup.find("main", {"itemprop": "articleBody"})
    title_el = soup.find("h1", {"data-qa": "Title"})
    ratings = soup.find_all("ul", class_="b5ce145b7d")

    if not text_el or not title_el:
        return {"title": "", "text": fallback, "finance": "", "health": "", "love": ""}

    result = {
        "title": title_el.text,
        "text": text_el.text,
        "finance": HORO_STARS.get(ratings[0]["aria-label"], "") if len(ratings) > 0 else "",
        "health": HORO_STARS.get(ratings[1]["aria-label"], "") if len(ratings) > 1 else "",
        "love": HORO_STARS.get(ratings[2]["aria-label"], "") if len(ratings) > 2 else "",
    }

    import json as _json
    await redis.set(cache_key, _json.dumps(result), ex=_ttl_until_midnight())
    return result


async def get_compare(
    female_zodiac: str,
    male_zodiac: str,
    *,
    client: httpx.AsyncClient,
    redis: Redis,
    fallback: str = "⚠️ Совместимость временно недоступна. Попробуйте позже.",
) -> dict[str, str]:
    """Fetch compatibility text. Cached in Redis until end of day."""
    import json

    key = f"{female_zodiac}_{male_zodiac}"
    cache_key = f"horo:compat:{key}"

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    compat_id = HORO_COMPAT.get(key)
    if not compat_id:
        return {"title": "", "text": fallback}

    url = _COMPAT_URL.format(compat_id=compat_id)
    content = await _fetch(client, url)
    if not content:
        return {"title": "", "text": fallback}

    soup = BeautifulSoup(content, "lxml")
    text_el = soup.find("div", class_="c1cd057491")
    title_el = soup.find("h1", class_="c30ebf5669 abf242312f ef123d1686")

    if not text_el or not title_el:
        return {"title": "", "text": fallback}

    formatted_text = re.sub(
        r'(\d+\.\s[^:]+:\s*[А-ЯЁ][а-яё]+)', r'\n\n<b>\1</b>\n', text_el.text
    )
    result = {"title": title_el.text, "text": formatted_text.strip()}

    await redis.set(cache_key, json.dumps(result), ex=_ttl_until_midnight())
    return result
