"""Репозиторий для работы с моделью UrlLink."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.core.logging import log
from src.api.models import UrlLink
from src.api.schemas import UrlLinkCreate

from .base_repository import BaseRepository


class UrlLinkRepository(BaseRepository[UrlLink, UrlLinkCreate, None]):
    """
    Репозиторий для выполнения CRUD-операций с моделью UrlLink.

    Наследует общие методы от BaseRepository и содержит специфичные для UrlLink методы.
    """

    async def get_by_code(self, db_session: AsyncSession, *, short_code: str) -> UrlLink | None:
        """
        Получает объект ссылки по шорт коду.

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            short_code (str): Шорт код (случайно сгенерированная строка).

        Returns:
            UrlLink | None: Экземпляр модели UrlLink или None, если запись не найдена.
        """
        log.debug(f"Получение объекта ссылки по шорт коду: {short_code}")
        url = self.get_by_filter(db_session, self.model.short_code == short_code)

        status = f"найден (ID: {url.id})" if url else "не найден"
        log.debug(f"Объект ссылки по шорт коду ({short_code}) {status}.")

        return url

    async def get_by_original_url(self, db_session: AsyncSession, *, url: str) -> UrlLink | None:
        """
        Получает объект ссылки по оригинальной пользовательской ссылке.

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            url (str): Оригинальная пользовательская ссылка.

        Returns:
            UrlLink | None: Экземпляр модели UrlLink или None, если запись не найдена.
        """
        log.debug(f"Получение объекта ссылки по оригинальной ссылке: {url}")
        url = self.get_by_filter(db_session, self.model.original_url == url)

        status = f"найден (ID: {url.id})" if url else "не найден"
        log.debug(f"Объект ссылки по оригинальной ссылке ({url}) {status}.")

        return url
