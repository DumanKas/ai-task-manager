
from services.tasks import new_task_telegram, old_task_telegram,complete_task,delete_task,get_tasks_by_user_id
from core.models import Task, User
from datetime import datetime, timedelta
from services.tasks import ALMATY
from sqlalchemy import select
from core.constans import STATUS_NEW,STATUS_DELETED,STATUS_COMPLETED
async def test_future_task_goes_to_new(session,create_user):
    moment_now =datetime(2026,11,4,12,0,0, tzinfo = ALMATY)
    task = Task(user_id = create_user.id, title = "Test Task", description = "Test desc", status = STATUS_NEW, deadline = moment_now + timedelta(hours=1))
    
    session.add(task)
    await session.flush()
    result = await new_task_telegram(session, moment_now)
    assert len(result) == 1
    assert result[0][0] == task.id
    assert result[0][3] == create_user.telegram_id


async def test_task_without_deadline_not_in_any_select(session,create_user):
    moment_now = datetime(2026,11,4,12,0,0, tzinfo = ALMATY)
    task_with_deadline = Task(user_id = create_user.id, title = "Task with deadline", description = "deadline", status = STATUS_NEW, deadline =  moment_now + timedelta(hours=1))
    task_without_deadline = Task(user_id = create_user.id, title = "Task without deadline", description = "No deadline", status = STATUS_NEW, deadline = None)
    session.add(task_with_deadline)
    session.add(task_without_deadline)
    await session.flush()
    result = await new_task_telegram(session, moment_now)
    result_old = await old_task_telegram(session, moment_now)
    assert len(result) == 1
    assert result[0][0] == task_with_deadline.id  
    assert len(result_old) == 0

async def test_not_new_status(session,create_user):
    moment_now = datetime(2026,11,4,12,0,0, tzinfo = ALMATY)
    task_completed = Task(user_id = create_user.id, title = "Completed Task", description = "Completed", status = STATUS_COMPLETED, deadline = moment_now + timedelta(hours=1))
    task_completed_minus_hour = Task(user_id = create_user.id, title = "Completed Task", description = "Completed", status = STATUS_COMPLETED, deadline = moment_now - timedelta(hours=1))

    session.add(task_completed)
    session.add(task_completed_minus_hour)
    await session.flush()
    result = await new_task_telegram(session, moment_now)
    result_old = await old_task_telegram(session, moment_now)

    assert len(result) == 0
    assert len(result_old) == 0


async def test_deadline_equal_to_now_goes_to_old(session,create_user):

    moment_now = datetime(2026,11,4,12,0,0, tzinfo = ALMATY)
    task = Task(user_id = create_user.id, title = "Completed Task", description = "Completed", status = STATUS_NEW, deadline = moment_now)
    session.add(task)
    await session.flush()
    result = await new_task_telegram(session, moment_now)
    result_old = await old_task_telegram(session, moment_now)
    assert len(result) == 0
    assert len(result_old) == 1
    assert result_old[0][0] == task.id

async def test_complete_task_success(session,create_user):

    moment_now = datetime(2026,11,4,12,0,0, tzinfo = ALMATY)
    task = Task(user_id = create_user.id, title = "new_task", description = "new_task_des", status = STATUS_NEW, deadline = moment_now)
    session.add(task)
    await session.flush()
    result = await complete_task(session,task.id, create_user.id)
    stmt_task = select(Task.status).where(Task.id == task.id)
    result_task = await session.execute(stmt_task)
    status =  result_task.scalar_one()
    assert result == task.id
    assert status == STATUS_COMPLETED

async def test_complete_task_wrong_user_returns_none(session,create_user):
    user_not_right = User(telegram_id = 123321)
    session.add(user_not_right)
    await session.flush()
    task = Task(user_id = create_user.id, title = "test_none_task", description = "new_task_des",status = STATUS_NEW)
    session.add(task)
    await session.flush()
    result = await complete_task(session, task.id, user_not_right.id)
    assert result is None
    stmt_task = select(Task.status).where(Task.id == task.id)
    result_task = await session.execute(stmt_task)
    status =  result_task.scalar_one()
    assert status == STATUS_NEW

async def test_complete_task_already_completed_returns_none(session,create_user):

    task = Task(user_id = create_user.id, title = "test_none_task", description = "new_task_des",status = STATUS_COMPLETED)
    session.add(task)
    await session.flush()
    result = await complete_task(session,task.id,create_user.id)
    assert result is None
    stmt_task = select(Task.status).where(Task.id == task.id)
    result_task = await session.execute(stmt_task)
    status =  result_task.scalar_one()
    assert status == STATUS_COMPLETED


async def test_complete_task_nonexistent_id_returns_none(session,create_user):
    result =await complete_task(session, 999, create_user.id)
    assert result is None


async def test_delete_task_success(session,create_user):

    task = Task(user_id = create_user.id, title = "test_delete_task", description = "new_task_des",status = STATUS_NEW)
    session.add(task)
    await session.flush()
    result = await delete_task(session,task.id,create_user.id)
    assert result == task.id
    stmt_task = select(Task.status).where(Task.id == task.id)
    result_task = await session.execute(stmt_task)
    status = result_task.scalar_one()
    assert status == STATUS_DELETED

async def test_delete_task_returns_none_for_already_deleted(session,create_user):

    task = Task(user_id = create_user.id, title = "test_delete_task", description = "new_task_des",status = STATUS_DELETED)
    session.add(task)
    await session.flush()
    result = await delete_task(session,task.id,create_user.id)
    assert result is None
    stmt_task = select(Task.status).where(Task.id == task.id)
    result_task = await session.execute(stmt_task)
    status = result_task.scalar_one()
    assert status == STATUS_DELETED


async def test_delete_task_wrong_user(session,create_user):

    user_two = User(telegram_id = 5555)
    session.add(user_two)
    await session.flush()
    task = Task(user_id = create_user.id, title = "test_delete_task", description = "new_task_des",status = STATUS_NEW)
    session.add(task)
    await session.flush()
    result = await delete_task(session,task.id,user_two.id)
    assert result is None
    stmt_task = select(Task.status).where(Task.id == task.id)
    result_task = await session.execute(stmt_task)
    status = result_task.scalar_one()
    assert status == STATUS_NEW



async def test_delete_task_without_task(session, create_user):
    result = await delete_task(session,999,create_user.id)
    assert result is None


async def test_delete_task_completed(session,create_user):
    task = Task(user_id = create_user.id, title = "test_delete_task", description = "new_task_des",status = STATUS_COMPLETED)
    session.add(task)
    await session.flush()
    result = await delete_task(session,task.id,create_user.id)
    assert result == task.id
    stmt = select(Task.status).where(Task.id == task.id)
    result_task = await session.execute(stmt)
    status = result_task.scalar_one()
    assert status == STATUS_DELETED


async def test_get_tasks_by_user_id_no_task(session,create_user):

    result = await get_tasks_by_user_id(session,create_user.id)

    assert result == []

async def test_get_tasks_by_user_id_another_user(session,create_user):
    user_not_right = User(telegram_id = 123321)
    session.add(user_not_right)
    await session.flush()
    task = Task(user_id = create_user.id,title = 'test')
    session.add(task)
    await session.flush()
    res = await get_tasks_by_user_id(session,user_not_right.id)
    assert res == []

async def test_get_tasks_by_user_id_wrong_status(session,create_user):
    task = Task(user_id = create_user.id, title = "test_task_completed",description = "new_task_des",status = STATUS_COMPLETED)
    task2 = Task(user_id = create_user.id, title = "test_task_new",description = "new_task_des",status = STATUS_NEW)
    task3 = Task(user_id = create_user.id, title = "test_task_deleted",description = "new_task_des",status = STATUS_DELETED)
    session.add(task)
    session.add(task2)
    session.add(task3)
    await session.flush()
    res = await get_tasks_by_user_id(session, create_user.id)
    res1 = []
    for x in res:
        res1.append(x.id)

    assert len(res1) == 2
    assert task3.id not in res1 


async def test_get_tasks_by_user_id_check_status(session,create_user):
    task = Task(user_id = create_user.id, title = "test_task_completed",description = "new_task_des",status = STATUS_COMPLETED)
    task2 = Task(user_id = create_user.id, title = "test_task_new",description = "new_task_des",status = STATUS_NEW)
    task3 = Task(user_id = create_user.id, title = "test_task_deleted",description = "new_task_des",status = STATUS_DELETED)
    session.add(task)
    session.add(task2)
    session.add(task3)
    await session.flush()
    res = await get_tasks_by_user_id(session, create_user.id,status=STATUS_COMPLETED)
    res1 = []
    for x in res:
        res1.append(x.id)

    assert len(res1) == 1
    assert task.id in res1 

async def test_get_tasks_by_user_id_time_check(session,create_user):
    moment_now = datetime(2026,11,4,12,0,0)
    task = Task(user_id = create_user.id, title = "test_task_completed",description = "new_task_des",status = STATUS_COMPLETED,created_at = moment_now)
    task1 = Task(user_id = create_user.id, title = "test_task_completed_old_time",description = "new_task_des",status = STATUS_COMPLETED,created_at = moment_now - timedelta(hours=1))
    session.add(task1)
    session.add(task)
    await session.flush()
    res = await get_tasks_by_user_id(session, create_user.id)
    assert res[0].created_at > res[1].created_at