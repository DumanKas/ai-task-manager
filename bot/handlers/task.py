from aiogram.filters import Command, CommandObject
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
from keyboards import get_task_keyboard, del_task_keyboard,llm_task_keyboard
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from services.users import get_user_by_telegram_id
from services.tasks import get_tasks_by_user_id, delete_task,complete_task,get_task_by_task_id
from html import escape
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.jobstores.base import JobLookupError
from services.llm import ask_llm, SYSTEM_PROMPT, LLMUnavailableError
import asyncio
from scheduler import scheduler
from scheduler.reminders import send_reminder

router = Router()
ALMATY = ZoneInfo("Asia/Almaty")     


class TaskCreation(StatesGroup):
    title = State()
    description = State()
    deadline = State()


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
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description = message.text)
    await message.answer("Введите дедлайн задачи: как пример 20.10.2026 18:30 либо - если не нужно")
    await state.set_state(TaskCreation.deadline)

@router.message(TaskCreation.deadline)
async def process_deadline(message: Message, state: FSMContext, session: AsyncSession):
    deadline_text = "Не указан дедлайн"
    data = await state.get_data()
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if user is None:
            await message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start для регистрации.")
            await state.clear()
            return
    if message.text.strip() == "-":
        as_utc = None
    else:
        try:
            deadline_naive = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
        except ValueError:
            await message.answer("Неверный формат даты и времени!\n"
                            "Пожалуйста, введите в формате: <code>ДД.ММ.ГГГГ ЧЧ:ММ</code> (например, <code>20.10.2026 18:30</code>)")  
            return
        almaty_time = deadline_naive.replace(tzinfo = ALMATY)
        moment_now = datetime.now(ALMATY)

        if moment_now > almaty_time:
            await message.answer("Введите дату в будущем")
            return

        as_utc = almaty_time.astimezone(ZoneInfo('UTC'))
        deadline_text = almaty_time.strftime("%d.%m.%Y %H:%M")


    new_task = Task(user_id=user.id, title = data['title'], description = data['description'], deadline = as_utc)
    session.add(new_task)
    try:
        await session.flush()
        await session.commit()
    except SQLAlchemyError as e:
        logging.error(f"Ошибка при создании задачи: {e}", exc_info=True)
        await session.rollback()
        await message.answer("Произошла ошибка при создании задачи. Пожалуйста, попробуйте снова.")
        return
    if as_utc:
        scheduler.add_job(
        send_reminder,
        trigger="date",
        run_date=as_utc,
        args=[message.bot, message.from_user.id, data["title"]],
        id=f"reminder_{new_task.id}",
    )

    await state.clear()
    await message.answer(
        f"Задача создана!\n"
        f"Название: {escape(data['title'])}\n"
        f"Описание: {escape(data['description'])}\n"
        f"Дедлайн: {deadline_text}", reply_markup= llm_task_keyboard(new_task)
    )


    





 


async def cycle_for_tasks(message: Message, tasks,keyboard_builder):
    max_limit = 4000
    current_chunk = ""
    chunk_tasks = []
    for task in tasks:
        created_text = task.created_at.replace(tzinfo = ZoneInfo('UTC')).astimezone(ALMATY).strftime("%d.%m.%Y %H:%M")
        deadline_task = task.deadline.astimezone(ALMATY).strftime('%d.%m.%Y %H:%M') if task.deadline else "Без дедлайна"
        description = task.description if task.description else "Нет описания"
        task_info = f"ID: {task.id}\nНазвание: {escape(task.title)}\nОписание: {escape(description)}\nСтатус: {task.status}\nДата создания: {created_text}\nДедлайн: {deadline_task}\n\n"
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
    try:
        scheduler.remove_job(f"reminder_{task_id}")
    except JobLookupError:
        pass
    await callback_query.message.answer(f"Задача с ID {completed_task} успешно завершена.")
    await callback_query.answer()



@router.callback_query(F.data.startswith('llm_help_'))
async def llm_helper_callback(callback_query: CallbackQuery, session: AsyncSession):
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=None)
    user = await get_user_by_telegram_id(session, callback_query.from_user.id)
    if user is None:
        await callback_query.message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start для регистрации.")
        return
    task_id = int(callback_query.data.split("_")[-1])
    task = await get_task_by_task_id(session,user.id, task_id)
    if task is None:
        await callback_query.message.answer("Задач нет чтобы разобрать с Сэм, проверьте еще раз")
        return
    task_text = f'Название: {task.title}'
    if task.description:
        task_text += f"\nОписание: {task.description}"


    messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT 
            },
            {
                "role": "user",
                "content": task_text
            }
        ]
    status_message = await callback_query.message.answer("Думаю...")
    try:
        llm_response = await ask_llm(messages=messages)
        await status_message.edit_text(llm_response)
    except LLMUnavailableError:
            await status_message.edit_text(
                "Сервис временно недоступен. Пожалуйста, попробуйте повторить запрос позже."
            )


    


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
    try:
        scheduler.remove_job(f"reminder_{task_id}")
    except JobLookupError:
        pass
    await callback_query.message.answer(f"Задача с ID {deleted_task} успешно удалена.")
    await callback_query.answer('Удалено')

@router.message(Command("help_task"))       
async def help_llm_handler(message: Message, session: AsyncSession, command: CommandObject):
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if user is None:
            await message.answer("Вы не зарегистрированы. Пожалуйста, используйте команду /start для регистрации.")
            return
    
    task_text = command.args
    if not task_text: 
        await message.answer(
            "После команды /help_task вы не указали описание задачи. "
            "Используйте команду так: <code>/help_task Текст задачи</code>"
        )
        return
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT 
        },
        {
            "role": "user",
            "content": task_text
        }
    ]
    status_message = await message.answer("Думаю...")

    try:
        llm_response = await ask_llm(messages=messages)
        await status_message.edit_text(llm_response)
    except LLMUnavailableError:
        await status_message.edit_text(
            "Сервис временно недоступен. Пожалуйста, попробуйте повторить запрос позже."
        )
