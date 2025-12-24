"""Сервис для работы с UrlLink."""

from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.core.database import db
from src.api.core.exceptions import ConflictException, NotFoundException
from src.api.core.logging import api_log as log
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
    """

    def __init__(self, urllink_repository: UrlLinkRepository):
        """
        Инициализирует сервис для репозитория UrlLinkRepository.

        Args:
            urllink_repository (UrlLinkRepository): Репозиторий для работы со ссылками.
        """
        super().__init__(repository=urllink_repository)

    async def create(self, db_session: AsyncSession, *, url: HttpUrl) -> UrlLink:
        """
        Создает новый объект ссылки.

        Управляет транзакцией: выполняет commit в случае успеха или rollback при ошибке.

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            url (HttpUrl): Оригинальная пользовательская ссылка, прошедшая валидацию.

        Returns:
            UrlLink: Созданный объект ссылки.

        Raises:
            ConflictException: Если ссылка с таким шорт кодом уже существует в БД.
        """
        # Лимит количества попыток для генерации шорт кода
        attempts: int = 5

        for attempt in range(attempts):
            # Генерируем шорт код
            short_code: str = generate_short_code()

            # Проверяем, существует ли такой шорт код в БД
            existed_short_code = await self.repository.is_exists(
                db_session,
                self.repository.model.short_code == short_code,
            )

            # Если шорт код существует
            if existed_short_code:
                log.warning(f"Коллизия: {short_code} уже занят. Попытка {attempt + 1}/{attempts}")
                continue  # Пробуем снова

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

        # Если цикл завершился (мы исчерпали лимит попыток генерации шорт кода), выбрасываем исключение
        raise ConflictException(
            error_type="urllink_conflict", message="Не удалось сгенерировать уникальный шорт код."
        )  # Можно выбросить IntegrityError вместо кастомной ошибки

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

    async def perform_click_increment(self, short_code: str) -> None:
        """
        Фоновая задача: создает свою сессию и вызывает инкремент в репозитории.

        Args:
            short_code (str): Шорт код (случайно сгенерированная строка).
        """
        # Открываем абсолютно новую сессию, не связанную с HTTP запросом
        async with db.session() as session:
            try:
                await self.repository.increment_click_count(session, short_code)
                # Коммитим (бизнес-операция завершена успешно)
                await session.commit()
            except Exception as exc:
                # rollback и close произойдут автоматически в контекстном менеджере db.session()
                log.error(f"Ошибка при обновлении счетчика кликов: {exc}")
