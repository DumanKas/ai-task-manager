from asyncio import tasks

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, Integer
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import DateTime
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key = True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default = func.now())

class Task(Base):
    __tablename__ = "tasks"


    id: Mapped[int] = mapped_column(primary_key = True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="new")
    created_at: Mapped[datetime] = mapped_column(server_default = func.now())
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    

    

    