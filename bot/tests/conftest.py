from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from config import settings
import pytest
from core.models import User
from core.models import Base
@pytest.fixture
async def session():
    url = settings.TEST_DB_URL
    db_name = url.split('/')[-1]
    if "test" not in db_name:
          raise RuntimeError("База данных для теста должна содержать test в названий, нужно чтобы не потерять данные в основной бд")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session_maker() as session:
          
        yield session
    async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def create_user(session):
    user = User(telegram_id = 123456)
    session.add(user)
    await session.flush()
    return user
