from datetime import date


# (month, day) -> zodiac slug (matches Mail.ru URL slugs)
_ZODIAC_RANGES = [
    ((3, 21), (4, 19), "aries"),
    ((4, 20), (5, 20), "taurus"),
    ((5, 21), (6, 20), "gemini"),
    ((6, 21), (7, 22), "cancer"),
    ((7, 23), (8, 22), "leo"),
    ((8, 23), (9, 22), "virgo"),
    ((9, 23), (10, 22), "libra"),
    ((10, 23), (11, 21), "scorpio"),
    ((11, 22), (12, 21), "sagittarius"),
    ((12, 22), (12, 31), "capricorn"),
    ((1, 1), (1, 19), "capricorn"),
    ((1, 20), (2, 18), "aquarius"),
    ((2, 19), (3, 20), "pisces"),
]


def calculate_zodiac(birth_date: date) -> str:
    """Returns Mail.ru URL zodiac slug (e.g. 'aries') from a birth date."""
    md = (birth_date.month, birth_date.day)
    for start, end, sign in _ZODIAC_RANGES:
        if start <= md <= end:
            return sign
    return "aries"  # fallback (should never occur)
