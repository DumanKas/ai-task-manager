
from html import escape
async def send_reminder(bot, chat_id, title):
    text = f"⏰ Напоминание: {escape(title)}"
    await bot.send_message(chat_id, text)
