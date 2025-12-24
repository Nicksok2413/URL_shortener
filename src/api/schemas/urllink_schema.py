"""Схемы Pydantic для модели UrlLink"""

from pydantic import Field, HttpUrl

from .base_schema import BaseSchema


class UrlLinkBaseSchema(BaseSchema):
    """Базовая схема ссылки."""

    original_url: str = Field(..., description="Оригинальная пользовательская ссылка")
    short_code: str = Field(..., description="Шорт код (случайно сгенерированная строка)")


class UrlLinkCreateSchema(BaseSchema):
    """Схема для создания новой ссылки (данные от пользователя)."""

    url: HttpUrl = Field(..., description="Ссылка от пользователя")


class UrlLinkResponseSchema(UrlLinkBaseSchema):
    """
    Схема ответа пользователю.

    Наследует поля от базовой схемы ссылки.
    """

    short_url: str = Field(..., description="Новая короткая ссылка")


class UrlLinkDetailsResponseSchema(UrlLinkResponseSchema):
    """
    Схема ответа пользователю с детальной информацией.

    Наследует поля от схемы UrlLinkResponseSchema.
    """

    click_count: int = Field(..., description="Счётчик переходов по ссылке")
