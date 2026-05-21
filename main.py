from contextlib import asynccontextmanager
from fastapi import FastAPI

# Импортируем компоненты базы данных и роутеры
from database import db_manager, Base, engine
from routers import students, groups


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения (Lifespan).

    Здесь описывается логика, которая выполняется строго ПЕРЕД запуском
    приложения и СРАЗУ ПОСЛЕ его остановки.
    """
    # Выполняется при запуске приложения:
    print("Инициализация базы данных...")
    async with engine.begin() as conn:
        # Создаем таблицы в БД, если они еще не созданы
        await conn.run_sync(Base.metadata.create_all)

    yield  # В этой точке приложение запускается и обрабатывает запросы

    # Выполняется при остановке приложения:
    print("Закрытие соединений с базой данных...")
    await db_manager.close()


# Инициализируем приложение FastAPI
app = FastAPI(
    title="Student Management API",
    description="API для управления студентами и учебными группами.",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем роутеры с общим префиксом для версионирования API v1
app.include_router(
    students.router_student,
    prefix="/api/v1",
    tags=["Students"]
)

app.include_router(
    groups.router_group,
    prefix="/api/v1",
    tags=["Groups"]
)