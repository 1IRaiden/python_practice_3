from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Group(Base):
    """
    Модель учебной группы.
    """
    __tablename__ = "groups"

    # Использование mapped_column вместо старого Column
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # func.now() заставляет БД саму выставлять текущее время при создании записи
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Денормализация: поле для быстрого отображения количества студентов в группе без лишних JOIN-запросов
    members_count: Mapped[int] = mapped_column(default=0)

    # Отношение "один ко многим": у одной группы может быть много студентов
    students: Mapped[List["Student"]] = relationship(back_populates="group")


class Student(Base):
    """
    Модель студента.
    """
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Внешний ключ на таблицу groups. Optional означает, что студент может быть временно без группы (nullable=True)
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)

    # Обратная связь с моделью Group
    group: Mapped[Optional["Group"]] = relationship(back_populates="students")