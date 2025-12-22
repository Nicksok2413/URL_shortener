"""Базовый репозиторий с общими CRUD-операциями."""

from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import ColumnElement, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import Base as SQLAlchemyBaseModel

# Определяем обобщенные (Generic) типы для моделей SQLAlchemy и схем Pydantic
ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)  # SQLAlchemy модель
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)  # Pydantic схема для создания
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)  # Pydantic схема для обновления


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый класс репозитория для асинхронных CRUD-операций.

    Предоставляет общие методы для создания, чтения, обновления и удаления
    сущностей в базе данных.

    Attributes:
        model: Класс модели SQLAlchemy, с которым работает репозиторий.
    """

    def __init__(self, model: type[ModelType]):
        """
        Инициализирует базовый репозиторий.

        Args:
            model (ModelType): Класс модели SQLAlchemy.
        """
        self.model = model

    async def is_exists(self, db_session: AsyncSession, *filters: ColumnElement[bool]) -> bool:
        """
        Проверяет существование записи в базе данных по заданным критериям фильтрации.

        Критерии должны быть выражениями SQLAlchemy (например, self.model.name == "John").

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            *filters (ColumnElement[bool]): Один или несколько критериев фильтрации SQLAlchemy.
                                            Они будут объединены через AND.

        Returns:
            bool: True - запись существует, False - нет
        """
        statement = select(exists().where(*filters))

        result = await db_session.execute(statement)

        # Оборачиваем в bool, чтобы mypy не ругался (сигнатура scalar -> Any | None)
        return bool(result.scalar())
