"""
Premium grant service.
Always uses datetime.now(timezone.utc) for UTC-safe comparisons.
"""
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database.models import User, UserStatus


async def grant_premium_days(user_id: int, days: int, db: AsyncSession) -> datetime:
    """
    Grant premium access to a user.
    - If premium_until is NULL or expired: set it to now + days (UTC).
    - If premium_until is in the future: extend it by days.
    - Sets status = PREMIUM.
    Returns the new premium_until datetime.
    """
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise ValueError(f"User {user_id} not found")

    now = datetime.now(timezone.utc)

    if user.premium_until and user.premium_until > now:
        new_until = user.premium_until + timedelta(days=days)
    else:
        new_until = now + timedelta(days=days)

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(premium_until=new_until, status=UserStatus.PREMIUM)
    )

    return new_until
