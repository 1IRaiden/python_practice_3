from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


"""
    Базовый класс для всех моделей SQLAlchemy (Style 2.0).
    Все ваши модели (Group, Student) должны наследоваться от него.
"""
Base = declarative_base()

class DatabaseManager:
    """
        Класс для управления подключением к базе данных и создания сессий.
        Инкапсулирует в себе движок SQLAlchemy и фабрику асинхронных сессий.
    """
    def __init__(self, db_url: str):
        self._engine = create_async_engine(db_url, echo=True)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close(self):
        """Закрывает все соединения с базой данных и очищает пул соединений."""
        await self._engine.dispose()

    async def __call__(self) -> AsyncSession:
        async with self._session_factory() as session:
            yield session


db_manager = DatabaseManager(settings.DATABASE_URL)




