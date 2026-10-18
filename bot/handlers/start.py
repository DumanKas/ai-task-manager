
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router
from sqlalchemy import select
from core.database import async_session_maker
from core.models import User
router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            new_user = User(telegram_id = message.from_user.id)
            session.add(new_user)
            await session.commit()
            await message.answer("Добро пожаловать! Вы успешно зарегистрированы.")
        else:
            await message.answer("С возвращением")
