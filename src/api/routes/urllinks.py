"""Эндпоинты для управления ссылками (UrlLinks)."""

from fastapi import APIRouter, status

from src.api.core.dependencies import DBSession, UrlLinkSvc
from src.api.schemas import UrlLinkCreateSchema, UrlLinkResponseSchema
from src.api.utils import format_short_url

router = APIRouter(prefix="/urls", tags=["URLs"])


@router.post(
    "/shorten",
    response_model=UrlLinkResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой короткой ссылки",
    description="Создает новую короткую ссылку для пользователя",
)
async def create_link(
    db_session: DBSession,
    urllink_service: UrlLinkSvc,
    data_in: UrlLinkCreateSchema,
) -> UrlLinkResponseSchema:
    """
    Создает новую короткую ссылку для пользователя.

    Args:
        db_session: Асинхронная сессия базы данных.
        urllink_service: Сервис для работы со ссылками.
        data_in: Данные для создания ссылки (оригинальный URL пользователя).

    Returns:
        UrlLink: Созданный объект ссылки.

    Raises:
        ConflictException: Если ссылка с таким шорт кодом уже существует в БД.
    """
    # Создаем новый объект ссылки
    new_link = await urllink_service.create(db_session, url=data_in.url)

    return UrlLinkResponseSchema(
        short_code=new_link.short_code,
        original_url=new_link.original_url,
        short_url=format_short_url(new_link.short_code),
    )
