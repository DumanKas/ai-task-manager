
import logging
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import SQLAlchemyError
from aiogram import Router
from sqlalchemy import select, update
from aiogram.filters import Command
from core.models import Task
from core.constans import STATUS_COMPLETED,STATUS_NEW
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards import get_task_keyboard, del_task_keyboard
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from services.users import get_user_by_telegram_id
from services.tasks import get_tasks_by_user_id, delete_task,complete_task
from html import escape
router = Router()

class TaskCreation(StatesGroup):
    title = State()
    description = State()


@router.message(Command("create_task"))
async def create_task(message: Message, state: FSMContext):
    await message.answer("Введите название задачи:") 
    await state.set_state(TaskCreation.title)

@router.message(TaskCreation.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание задачи:")
    await state.set_state(TaskCreation.description)

@router.message(TaskCreation.description)
async def process_description(message: Message, state: FSMContext, session: AsyncSession):

    data = await state.get_data()
    user = await get_user_by_telegram_id(session, message.from_user.id)

    if user is None:
        await message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start для регистрации.")
        await state.clear()
        return

    new_task = Task(user_id=user.id, title = data['title'], description = message.text)
    session.add(new_task)
    try:
        await session.commit()
    except SQLAlchemyError as e:
        logging.error(f"Ошибка при создании задачи: {e}", exc_info=True)
        await session.rollback()
        await message.answer("Произошла ошибка при создании задачи. Пожалуйста, попробуйте снова.")
        return  
    await state.clear()
    await message.answer(f"Задача создана!\nНазвание: {escape(data['title'])}\nОписание: {escape(message.text)}")


async def cycle_for_tasks(message: Message, tasks,keyboard_builder):


    max_limit = 4000
    current_chunk = ""
    chunk_tasks = []
    for task in tasks:
        description = task.description if task.description else "Нет описания"
        task_info = f"ID: {task.id}\nНазвание: {escape(task.title)}\nОписание: {escape(description)}\nСтатус: {task.status}\nДата создания: {task.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        if len(current_chunk) + len(task_info) > max_limit:
            await message.answer((current_chunk), reply_markup=keyboard_builder(chunk_tasks) if chunk_tasks else None)
            current_chunk = task_info
            chunk_tasks = []
        else:
            current_chunk += task_info  
        
        chunk_tasks.append(task)
    if current_chunk:
        await message.answer(current_chunk, reply_markup=keyboard_builder(chunk_tasks) if chunk_tasks else None)



@router.message(Command("tasks", "my_tasks"))
async def list_tasks(message: Message, session: AsyncSession):
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if user is None:
        await message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start для регистрации.")
        return
    tasks = await get_tasks_by_user_id(session, user.id, status = STATUS_NEW)
    if not tasks:
        await message.answer("Нет активных задач.")
        return

    await cycle_for_tasks(message, tasks,get_task_keyboard)

@router.message(Command("completed", "completed_tasks"))
async def list_completed_tasks(message:Message, session:AsyncSession):
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if user is None:
        await message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start для регистрации.")
        return

    tasks = await get_tasks_by_user_id(session, user.id, status= STATUS_COMPLETED)
    if not tasks:
        await message.answer("Нет выполненных задач.")
        return
    await cycle_for_tasks(message, tasks, del_task_keyboard)


    
@router.callback_query(F.data.startswith("complete_"))
async def complete_task_callback(callback_query: CallbackQuery,session: AsyncSession):
        
    user = await get_user_by_telegram_id(session, callback_query.from_user.id)
    if user is None:
        await callback_query.message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start для регистрации.")
        await callback_query.answer()
        return
    task_id = int(callback_query.data.split("_")[1])
    completed_task = await complete_task(session, task_id, user.id)
    if completed_task is None:
        await callback_query.message.answer("Эта задача уже выполнена или не найдена.")
        await callback_query.answer()
        return

    await session.commit()
    await callback_query.message.answer(f"Задача с ID {completed_task} успешно завершена.")
    await callback_query.answer()



@router.callback_query(F.data.startswith('delete_'))
async def delete_task_callback(callback_query: CallbackQuery, session: AsyncSession):
    user = await get_user_by_telegram_id(session, callback_query.from_user.id)
    if user is None:
        await callback_query.message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start для регистрации.")
        await callback_query.answer()
        return
    task_id = int(callback_query.data.split('_')[1])
    deleted_task = await delete_task(session, task_id, user.id)
    if deleted_task is None:
        await callback_query.message.answer("Нечего удалять. Эта задача уже удалена или не найдена.")
        await callback_query.answer()
        return
        
    await session.commit()
    await callback_query.message.answer(f"Задача с ID {deleted_task} успешно удалена.")
    await callback_query.answer('Удалено')

        
