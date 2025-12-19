"""Репозиторий для работы с моделью UrlLink."""

from pydantic import BaseModel
from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import UrlLink

from .base_repository import BaseRepository


class UrlLinkRepository(BaseRepository[UrlLink, BaseModel, BaseModel]):  # Используем BaseModel как тип-заглушку
    """
    Репозиторий для выполнения CRUD-операций с моделью UrlLink.

    Наследует общие методы от BaseRepository и содержит специфичные для UrlLink методы.
    """

    async def create(self, db_session: AsyncSession, *, new_link_data: dict[str, str]) -> UrlLink:
        """
        Создает и добавляет новый объект ссылки в сессию.

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            new_link_data (dict[str, str]): Словарь с данными для создания нового объекта ссылки.

        Returns:
            UrlLink: Созданный экземпляр ссылки.
        """
        # Подготавливаем объект
        new_link = self.model(**new_link_data)

        # Добавляем объект в сессию
        db_session.add(new_link)

        # Получаем ID и другие сгенерированные базой данных значения
        await db_session.flush()

        # Обновляем объект из базы данных
        await db_session.refresh(new_link)

        # Возвращаем созданный объект
        return new_link

    async def get_by_filter(self, db_session: AsyncSession, *filters: ColumnElement[bool]) -> UrlLink | None:
        """
        Получает первую запись, соответствующую заданным критериям фильтрации, или None.

        Критерии должны быть выражениями SQLAlchemy (например, self.model.name == "John").

        Args:
            db_session (AsyncSession): Асинхронная сессия базы данных.
            *filters (ColumnElement[bool]): Один или несколько критериев фильтрации SQLAlchemy.
                                            Они будут объединены через AND.

        Returns:
            UrlLink | None: Экземпляр модели или None, если запись не найдена.
        """
        statement = select(self.model)

        if filters:
            statement = statement.where(*filters)

        # Явное ограничение остановки поиска после первого совпадения
        statement = statement.limit(1)

        result = await db_session.execute(statement)

        return result.scalar_one_or_none()
