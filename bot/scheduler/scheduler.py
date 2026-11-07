from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.constans import LOCATION

scheduler = AsyncIOScheduler(timezone=ZoneInfo(LOCATION))