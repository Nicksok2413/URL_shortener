"""Модель SQLAlchemy для UrlLink (Ссылка)."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UrlLink(Base):
    """
    Представляет пользователя Telegram в приложении.

    Attributes:
        id: Первичный ключ, внутренний идентификатор ссылки (унаследован от Base).
        original_url: Длинная ссылка, передавая пользователем.
        short_code: Сокращенная ссылка ( короткий "хвост").
        click_count: Счётчик переходов по ссылке.
        created_at: Время создания записи (унаследовано от TimestampMixin).
        updated_at: Время последнего обновления записи (унаследовано от TimestampMixin).
    """

    original_url: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)