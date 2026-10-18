from sqlalchemy import select, update
from core.models import Task
from sqlalchemy.ext.asyncio import AsyncSession
from core.constans import STATUS_COMPLETED, STATUS_DELETED, STATUS_NEW

async def get_tasks_by_user_id(session: AsyncSession, user_id: int, status: str | None = None):

    stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    if status:    
        stmt = stmt.where(Task.status == status) 
    else:
        stmt = stmt.where(Task.status != STATUS_DELETED) 
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_task(session: AsyncSession, task_id: int, user_id: int):
    stmt = update(Task).where(Task.id == task_id, Task.user_id == user_id, Task.status != STATUS_DELETED).values(status=STATUS_DELETED).returning(Task.id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def complete_task(session: AsyncSession, task_id: int, user_id: int):
    stmt_task = update(Task).where(Task.id == task_id, Task.user_id == user_id, Task.status == STATUS_NEW).values(status=STATUS_COMPLETED).returning(Task.id)
    result_task = await session.execute(stmt_task)
    return result_task.scalar_one_or_none()
