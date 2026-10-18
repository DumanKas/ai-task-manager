import asyncio
import logging
import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
import asyncpg
from config import settings
engine = create_async_engine(settings.DB_URL, echo=True)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)