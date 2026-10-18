import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import settings
from aiogram.client.default import Default,DefaultBotProperties
from handlers.start import router
from handlers.task import router as task_router
from core.database import engine
from core.models import Base
from middlewares import DbSessionMiddleware


bot = Bot(token=settings.BOT_TOKEN,default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.message.middleware(DbSessionMiddleware())
dp.callback_query.middleware(DbSessionMiddleware())
dp.include_router(task_router)
dp.include_router(router)



async def main():
    logging.basicConfig(level=logging.INFO)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
    