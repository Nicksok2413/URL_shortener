"""Базовый репозиторий с общими CRUD-операциями."""

from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.core.logging import log
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

    async def get_by_filter(self, db_session: AsyncSession, *filters: ColumnElement[bool]) -> ModelType | None:
        """
        Получает первую запись, соответствующую заданным критериям фильтрации, или None.

        Критерии должны быть выражениями SQLAlchemy (например, self.model.name == "John").

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            *filters (ColumnElement[bool]): Один или несколько критериев фильтрации SQLAlchemy.
                                            Они будут объединены через AND.

        Returns:
            ModelType | None: Экземпляр модели или None, если запись не найдена.
        """
        statement = select(self.model)

        if filters:
            statement = statement.where(*filters)

        # Явное ограничение остановки поиска после первого совпадения
        statement = statement.limit(1)

        result = await db_session.execute(statement)

        return result.scalar_one_or_none()

    async def create(self, db_session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Создает и добавляет новый объект в сессию на основе Pydantic схемы.

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            obj_in (CreateSchemaType): Pydantic схема с данными для создания модели.

        Returns:
            ModelType: Созданный экземпляр модели.
        """
        model_name = self.model.__name__

        # Конвертируем данные в словарь
        obj_in_data = obj_in.model_dump()

        # Подготавливаем объект
        log.debug(f"Подготовка к созданию записи {model_name} с данными: {obj_in_data}")
        db_obj = self.model(**obj_in_data)

        # Добавляем объект в сессию
        db_session.add(db_obj)

        # Получаем ID и другие сгенерированные базой данных значения
        await db_session.flush()

        # Обновляем объект из базы данных
        await db_session.refresh(db_obj)

        # Логируем успешное создание объекта
        log.info(f"{model_name} успешно создан.")

        # Возвращаем созданный объект
        return db_obj
