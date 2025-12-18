"""Схемы Pydantic для модели UrlLink"""

from pydantic import Field, HttpUrl

from .base_schema import BaseSchema


class UrlLinkCreate(BaseSchema):
    """Схема для создания новой ссылки (данные от пользователя)."""

    url: HttpUrl = Field(..., description="Ссылка от пользователя")


class UrlLinkResponse(BaseSchema):
    """"""

    short_code: str = Field(..., description="")
    original_url: HttpUrl = Field(..., description="")
