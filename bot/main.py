import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import settings
from aiogram.client.default import DefaultBotProperties
from handlers.start import router
from handlers.task import router as task_router
from core.database import engine
from core.models import Base
from services.tasks import restore_task_reminders
from middlewares import DbSessionMiddleware
from scheduler import scheduler
from datetime import datetime, timedelta
from core.constans import LOCATION
from zoneinfo import ZoneInfo

bot = Bot(token=settings.BOT_TOKEN,default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.message.middleware(DbSessionMiddleware())
dp.callback_query.middleware(DbSessionMiddleware())
dp.include_router(task_router)
dp.include_router(router)


async def main():
    logging.basicConfig(level=logging.INFO)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all
        )
    scheduler.start()
    
    try:
        moment_now = datetime.now(ZoneInfo(LOCATION))
        await restore_task_reminders(bot, moment_now)
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
    