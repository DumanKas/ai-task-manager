from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



def get_task_keyboard(tasks):
    if not tasks:
        return None
    rows = []
    for task in tasks:
        btn_complete = InlineKeyboardButton(
            text=f"✅ Выполнить № {task.id}", 
            callback_data=f"complete_{task.id}"
        )
        btn_delete = InlineKeyboardButton(
            text=f"❌ Удалить № {task.id}", 
            callback_data=f"delete_{task.id}"
        )

        rows.append([btn_complete, btn_delete])
    return InlineKeyboardMarkup(inline_keyboard=rows)



def del_task_keyboard(tasks):
    if not tasks:
        return None
    rows = []
    for task in tasks:
        btn_delete = InlineKeyboardButton(
            text=f"❌ Удалить № {task.id}", 
            callback_data=f"delete_{task.id}"
        )
        rows.append([btn_delete])
    return InlineKeyboardMarkup(inline_keyboard=rows)
