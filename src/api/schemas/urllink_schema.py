"""Схемы Pydantic для модели UrlLink"""

from pydantic import Field, HttpUrl

from .base_schema import BaseSchema


class UrlLinkBase(BaseSchema):
    """Базовая схема ссылки."""
    original_url: str = Field(..., description="Оригинальная пользовательская ссылка")
    short_code: str = Field(..., description="Шорт код (случайно сгенерированная строка)")


class UrlLinkCreate(BaseSchema):
    """Схема для создания новой ссылки (данные от пользователя)."""
    url: HttpUrl = Field(..., description="Ссылка от пользователя")


class UrlLinkResponse(UrlLinkBase):
    """
    Схема ответа пользователю.

    Наследует поля от базовой схемы ссылки.
    """
    short_url: str = Field(..., description="Новая короткая ссылка")
