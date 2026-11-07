from services.tasks import new_task_telegram, old_task_telegram
from core.models import Task, User
from datetime import datetime, timedelta
from services.tasks import ALMATY
from core.constans import STATUS_NEW,STATUS_DELETED,STATUS_COMPLETED
async def test_future_task_goes_to_new(session):
    user = User(telegram_id = 123456)
    session.add(user)
    await session.flush()
    moment_now =datetime(2026,11,4,12,0,0, tzinfo = ALMATY)
    task = Task(user_id = user.id, title = "Test Task", description = "Test desc", status = STATUS_NEW, deadline = moment_now + timedelta(hours=1))
    
    session.add(task)
    await session.flush()
    result = await new_task_telegram(session, moment_now)
    result_old = await old_task_telegram(session, moment_now)

    assert len(result) == 1
    assert result[0][0] == task.id
    assert result[0][3] == user.telegram_id
async def test_task_without_deadline_not_in_any_select(session):
    user = User(telegram_id = 789456123)
    session.add(user)
    await session.flush()
    moment_now = datetime(2026,11,4,12,0,0, tzinfo = ALMATY)
    task_with_deadline = Task(user_id = user.id, title = "Task with deadline", description = "deadline", status = STATUS_NEW, deadline =  moment_now + timedelta(hours=1))
    task_without_deadline = Task(user_id = user.id, title = "Task without deadline", description = "No deadline", status = STATUS_NEW, deadline = None)
    session.add(task_with_deadline)
    session.add(task_without_deadline)
    await session.flush()
    result = await new_task_telegram(session, moment_now)
    result_old = await old_task_telegram(session, moment_now)
    assert len(result) == 1
    assert result[0][0] == task_with_deadline.id  
    assert len(result_old) == 0

async def test_not_new_status(session):
    user = User(telegram_id = 132456789)
    session.add(user)
    await session.flush()
    moment_now = datetime(2026,11,4,12,0,0, tzinfo = ALMATY)
    task_completed = Task(user_id = user.id, title = "Completed Task", description = "Completed", status = STATUS_COMPLETED, deadline = moment_now + timedelta(hours=1))
    task_completed_minus_hour = Task(user_id = user.id, title = "Completed Task", description = "Completed", status = STATUS_COMPLETED, deadline = moment_now - timedelta(hours=1))

    session.add(task_completed)
    session.add(task_completed_minus_hour)
    await session.flush()
    result = await new_task_telegram(session, moment_now)
    result_old = await old_task_telegram(session, moment_now)

    assert len(result) == 0
    assert len(result_old) == 0


async def test_deadline_equal_to_now_goes_to_old(session):
    user = User(telegram_id = 789456)
    session.add(user)
    await session.flush()
    moment_now = datetime(2026,11,4,12,0,0, tzinfo = ALMATY)
    task = Task(user_id = user.id, title = "Completed Task", description = "Completed", status = STATUS_NEW, deadline = moment_now)
    session.add(task)
    await session.flush()
    result = await new_task_telegram(session, moment_now)
    result_old = await old_task_telegram(session, moment_now)
    assert len(result) == 0
    assert len(result_old) == 1
    assert result_old[0][0] == task.id