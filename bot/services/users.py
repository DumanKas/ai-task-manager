from sqlalchemy import select
from core.models import User
from sqlalchemy.ext.asyncio import AsyncSession



async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

