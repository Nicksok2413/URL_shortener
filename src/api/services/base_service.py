"""
Базовый класс для сервисов.

Реализует основную бизнес-логику CRUD операций, управление транзакциями
и валидацию данных перед передачей в репозиторий.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

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
