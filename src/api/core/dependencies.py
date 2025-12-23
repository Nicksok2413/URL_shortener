"""Зависимости для FastAPI."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import UrlLink
from src.api.repositories import UrlLinkRepository
from src.api.services import UrlLinkService

from .database import get_db_session

# --- Типизация для инъекции сессии базы данных ---

DBSession = Annotated[AsyncSession, Depends(get_db_session)]


# --- Фабрики Репозиториев ---


def get_urllink_repository() -> UrlLinkRepository:
    """Создает экземпляр репозитория для работы с моделями UrlLink."""
    return UrlLinkRepository(UrlLink)


# Типизация репозиториев (для использования в аргументах функций)
UrlLinkRepo = Annotated[UrlLinkRepository, Depends(get_urllink_repository)]


# --- Фабрики Сервисов ---


def get_urllink_service(repository: UrlLinkRepo) -> UrlLinkService:
    """Создает экземпляр сервиса для работы с UrlLink."""
    return UrlLinkService(urllink_repository=repository)


# Типизация для сервисов (для использования в аргументах функций)
UrlLinkSvc = Annotated[UrlLinkService, Depends(get_urllink_service)]
