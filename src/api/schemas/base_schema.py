"""Базовая конфигурация и схема для Pydantic."""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема Pydantic с общей конфигурацией."""

    model_config = ConfigDict(
        from_attributes=True,  # Позволяет создавать схемы из ORM моделей
        populate_by_name=True,  # Позволяет использовать alias для полей
    )
