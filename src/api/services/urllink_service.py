"""Сервис для работы с UrlLink."""

from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.core.exceptions import NotFoundException
from src.api.core.logging import log
from src.api.models import UrlLink
from src.api.repositories import UrlLinkRepository
from src.api.utils import generate_short_code

from .base_service import BaseService


class UrlLinkService(
    BaseService[UrlLink, UrlLinkRepository, BaseModel, BaseModel]
):  # Используем BaseModel как тип-заглушку
    """
    Сервис для управления ссылками.

    Отвечает за создание, чтение, обновление и удаление записей о ссылках.

    Attrs:
        attempts (int): Лимит количества попыток для ограничения рекурсивных вызовов метода `.create`.
    """

    def __init__(self, urllink_repository: UrlLinkRepository):
        """
        Инициализирует сервис для репозитория UrlLinkRepository.

        Args:
            urllink_repository (UrlLinkRepository): Репозиторий для работы со ссылками.
        """
        super().__init__(repository=urllink_repository)
        self._attempts: int = 5  # По умолчанию 5 попыток

    async def create(self, db_session: AsyncSession, *, url: HttpUrl) -> UrlLink | None:
        """
        Создает новый объект ссылки.

        Управляет транзакцией: выполняет commit в случае успеха или rollback при ошибке.

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            url (HttpUrl): Оригинальная пользовательская ссылка, прошедшая валидацию.

        Returns:
            UrlLink | None: Созданный объект ссылки или None при исчерпании лимита попыток генерации шорт кода.
        """
        # Если мы исчерпали лимит попыток генерации шорт кода, возвращаем None
        if self._attempts == 0:
            log.warning("Ошибка: Исчерпан лимит попыток генерации уникального шорт кода.")
            return None

        # Генерируем шорт код
        short_code: str = generate_short_code()

        # Проверяем, существует ли такой шорт код в БД
        is_short_code_exists = await self.get_by_code(db_session, short_code=short_code)

        # Если шорт код существует и мы не достигли лимита попыток
        if is_short_code_exists and self._attempts > 0:
            # Уменьшаем счетчик попыток
            self._attempts -= 1

            # Рекурсивно вызываем метод снова
            await self.create(db_session, url=url)

        # Сбрасываем счетчик попыток
        self._attempts = 5

        # Конвертируем данные в словарь
        new_link_data = {"original_url": str(url), "short_code": short_code}
        log.debug(f"Подготовка к созданию объекта UrlLink из данных: {new_link_data}")

        try:
            # Репозиторий добавляет объект в сессию
            new_link = await self.repository.create(db_session, new_link_data=new_link_data)

            # Сервис фиксирует транзакцию (бизнес-операция завершена успешно)
            await db_session.commit()

            # Логируем успешное создание объекта
            log.info(f"Объект UrlLink (ID: {new_link.id}) успешно создан.")

            # Возвращаем созданный объект
            return new_link

        except Exception as exc:
            # При любой ошибке откатываем транзакцию, чтобы сохранить целостность данных
            await db_session.rollback()

            # Логируем ошибку и выбрасываем исключение
            log.error(f"Ошибка при создании объекта UrlLink: {exc}", exc_info=True)
            raise exc

    async def get_by_code(self, db_session: AsyncSession, *, short_code: str) -> UrlLink:
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
        log.debug(f"Получение объекта ссылки по шорт коду: {short_code}")
        url = await self.repository.get_by_filter(db_session, self.repository.model.short_code == short_code)

        status = f"найден (ID: {url.id})" if url else "не найден"
        message = f"Объект ссылки по шорт коду ({short_code}) {status}."

        # Если объект ссылки не найден, выбрасываем исключение
        if not url:
            raise NotFoundException(
                message=message,
                error_type="urllink_not_found",
            )

        # Логируем успех и возвращаем найденный объект ссылки
        log.debug(message)
        return url

    async def get_by_original_url(self, db_session: AsyncSession, *, original_url: str) -> UrlLink:
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
        log.debug(f"Получение объекта ссылки по оригинальной ссылке: {original_url}")
        url = await self.repository.get_by_filter(db_session, self.repository.model.original_url == original_url)

        status = f"найден (ID: {url.id})" if url else "не найден"
        message = f"Объект ссылки по оригинальной ссылке ({url}) {status}."

        # Если объект ссылки не найден, выбрасываем исключение
        if not url:
            raise NotFoundException(
                message=message,
                error_type="urllink_not_found",
            )

        # Логируем успех и возвращаем найденный объект ссылки
        log.debug(message)
        return url
