"""Сервис для работы с UrlLink."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.core.exceptions import NotFoundException
from src.api.models import UrlLink
from src.api.repositories import UrlLinkRepository
from src.api.schemas import UrlLinkCreate

from .base_service import BaseService


class UrlLinkService(BaseService[UrlLink, UrlLinkRepository, UrlLinkCreate, None]):
    """
    Сервис для управления ссылками.

    Отвечает за создание, чтение, обновление и удаление записей о ссылках.
    """

    def __init__(self, urllink_repository: UrlLinkRepository):
        """
        Инициализирует сервис для репозитория UrlLinkRepository.

        Args:
            urllink_repository (UrlLinkRepository): Репозиторий для работы со ссылками.
        """
        super().__init__(repository=urllink_repository)

    async def create_link(self, db_session: AsyncSession, *, url: str) -> UrlLink:
        """"""
        pass

    async def get_link_by_code(self, db_session: AsyncSession, *, short_code: str) -> UrlLink:
        """
        Получает ссылку по шорт коду.

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            short_code (str): Шорт код (случайно сгенерированная строка).

        Returns:
            UrlLink: Найденная ссылка.

        Raises:
            NotFoundException: Если ссылка не найдена.
        """
        # Проверка существования объекта ссылки
        url = await self.repository.get_by_code(db_session, short_code=short_code)

        # Если объект ссылки не найден, выбрасываем исключение
        if not url:
            raise NotFoundException(
                message=f"UrlLink по шорт коду ({short_code}) не найден.",
                error_type="urllink_not_found",
            )

        # Возвращаем найденный объект ссылки
        return url

    async def get_link_by_original_url(self, db_session: AsyncSession, *, original_url: str) -> UrlLink:
        """
        Получает ссылку по оригинальной пользовательской ссылке.

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            original_url (str): Оригинальная пользовательская ссылка.

        Returns:
            UrlLink: Найденная ссылка.

        Raises:
            NotFoundException: Если ссылка не найдена.
        """
        # Проверка существования объекта ссылки
        url = await self.repository.get_by_original_url(db_session, url=original_url)

        # Если объект ссылки не найден, выбрасываем исключение
        if not url:
            raise NotFoundException(
                message=f"UrlLink по оригинальной ссылке ({original_url}) не найден.",
                error_type="urllink_not_found",
            )

        # Возвращаем найденный объект ссылки
        return url
