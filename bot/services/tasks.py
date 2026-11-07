import logging
from html import escape
from scheduler import scheduler
from sqlalchemy import select, update
from scheduler.reminders import send_reminder
from core.models import Task, User
from sqlalchemy.ext.asyncio import AsyncSession
from core.constans import STATUS_COMPLETED, STATUS_DELETED, STATUS_NEW
from datetime import datetime
from zoneinfo import ZoneInfo
from aiogram.exceptions import TelegramAPIError
from core.database import async_session_maker


ALMATY = ZoneInfo("Asia/Almaty")     
async def get_tasks_by_user_id(session: AsyncSession, user_id: int, status: str | None = None):

    stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    if status:    
        stmt = stmt.where(Task.status == status) 
    else:
        stmt = stmt.where(Task.status != STATUS_DELETED) 
    result = await session.execute(stmt)
    return result.scalars().all()


async def new_task_telegram(session: AsyncSession,moment_now: datetime):
    stmt = select(Task.id,Task.title, Task.deadline, User.telegram_id).join(User, Task.user_id == User.id).where(Task.status == STATUS_NEW, Task.deadline > moment_now)
    result = await session.execute(stmt)
    return result.all()


async def old_task_telegram(session: AsyncSession, moment_now: datetime):
    stmt = select(Task.id, Task.title, Task.deadline, User.telegram_id).join(User, Task.user_id == User.id).where(Task.status == STATUS_NEW, Task.deadline <= moment_now)
    result = await session.execute(stmt)
    return result.all()


async def restore_task_reminders( bot, moment_now: datetime):
    async with async_session_maker() as session:
        old_tasks = await old_task_telegram(session, moment_now)
        new_tasks = await new_task_telegram(session, moment_now)

    for task in old_tasks:
        try:
            text = f"⏰ Задача {escape(task[1])} Просрочена!\nСрок выполнения: {task[2].astimezone(ALMATY).strftime('%d.%m.%Y %H:%M')}"
            await bot.send_message(task[3], text)
        except TelegramAPIError as e:
            logging.warning(f"Не удалось отправить просрочку по задаче {task[0]}: {e}")


    for task in new_tasks:
        scheduler.add_job(
            send_reminder,
            trigger = "date",
            run_date = task.deadline,
            args = [bot, task.telegram_id, task.title],
            id = f"reminder_{task.id}",
            replace_existing = True
        )


async def get_task_by_task_id(session: AsyncSession,user_id: int,task_id: int):
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id,Task.status != STATUS_DELETED)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def delete_task(session: AsyncSession, task_id: int, user_id: int):
    stmt = update(Task).where(Task.id == task_id, Task.user_id == user_id, Task.status != STATUS_DELETED).values(status=STATUS_DELETED).returning(Task.id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def complete_task(session: AsyncSession, task_id: int, user_id: int):
    stmt_task = update(Task).where(Task.id == task_id, Task.user_id == user_id, Task.status == STATUS_NEW).values(status=STATUS_COMPLETED).returning(Task.id)
    result_task = await session.execute(stmt_task)
    return result_task.scalar_one_or_none()
