"""
Базовый класс для сервисов.

Реализует основную бизнес-логику CRUD операций, управление транзакциями
и валидацию данных перед передачей в репозиторий.
"""

from typing import Generic, TypeVar, cast

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.core.logging import log
from src.api.models import Base as SQLAlchemyBaseModel
from src.api.repositories import BaseRepository

# Определяем обобщенные (Generic) типы для моделей SQLAlchemy, репозиториев и схем Pydantic
ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)  # SQLAlchemy модель
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)  # Репозиторий
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)  # Pydantic схема для создания
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)  # Pydantic схема для обновления


class BaseService(Generic[ModelType, RepositoryType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый сервис с общими операциями и управлением транзакциями.

    Этот класс предназначен для наследования конкретными сервисами.
    Он предоставляет общую логику для CRUD операций, используя репозиторий.
    Управление транзакциями (commit, rollback) предполагается на уровне
    конкретных методов сервиса, которые представляют собой "единицу работы (Unit of Work)".

    Attributes:
        repository (RepositoryType): Экземпляр репозитория для работы с данными.
    """

    def __init__(self, repository: RepositoryType):
        """
        Инициализирует базовый сервис.

        Args:
            repository (RepositoryType): Репозиторий для работы с данными.
        """
        self.repository = repository

    async def create(self, db_session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Создает новый объект.

        Управляет транзакцией: выполняет commit в случае успеха или rollback при ошибке.

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            obj_in (CreateSchemaType): Схема с данными для создания.

        Returns:
            ModelType: Созданный объект.
        """

        model_name = self.repository.model.__name__

        try:
            # Репозиторий добавляет объект в сессию
            db_obj = await self.repository.create(db_session, obj_in=obj_in)

            # Сервис фиксирует транзакцию (бизнес-операция завершена успешно)
            await db_session.commit()

            # Возвращаем созданный объект
            return cast(ModelType, db_obj)  # Явное приведение типа для mypy

        except Exception as exc:
            # При любой ошибке откатываем транзакцию, чтобы сохранить целостность данных
            await db_session.rollback()

            # Логируем ошибку и выбрасываем исключение
            log.error(f"Ошибка при создании {model_name}: {exc}", exc_info=True)
            raise exc
