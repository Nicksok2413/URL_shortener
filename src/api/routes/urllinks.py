"""Эндпоинты для управления ссылками (UrlLinks)."""

from fastapi import APIRouter, BackgroundTasks, status
from starlette.responses import RedirectResponse

from src.api.core.dependencies import DBSession, UrlLinkSvc
from src.api.schemas import UrlLinkCreateSchema, UrlLinkDetailsResponseSchema, UrlLinkResponseSchema
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


@router.get(
    "/{short_code}",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Редирект по короткой ссылке на оригинальный URL",
    description="Находит объект ссылки по шорт коду и перенаправляет на оригинальный URL",
)
async def get_link(
    short_code: str,
    db_session: DBSession,
    urllink_service: UrlLinkSvc,
    background_tasks: BackgroundTasks,
) -> RedirectResponse:
    """
    Находит объект ссылки по шорт коду и перенаправляет на оригинальный URL.

    Args:
        short_code: Шорт код ссылки из URL пути.
        db_session: Асинхронная сессия базы данных.
        urllink_service: Сервис для работы со ссылками.

    Returns:
        RedirectResponse: Ответ перенаправления на оригинальный URL.

    Raises:
        NotFoundException: Если ссылка не найдена.
    """

    # Проверка существования объекта ссылки
    link = await urllink_service.get_by_code(db_session, short_code=short_code)

    # Фоном увеличиваем счетчик переходов по ссылке через BackgroundTasks
    background_tasks.add_task(urllink_service.perform_click_increment, short_code)

    return RedirectResponse(link.original_url)


@router.get(
    "/{short_code}/details",
    status_code=status.HTTP_200_OK,
    summary="Вывод детальной информации по шорт коду",
    description="Находит объект ссылки по шорт коду и выводит детальную информацию",
)
async def get_link_details(
    short_code: str,
    db_session: DBSession,
    urllink_service: UrlLinkSvc,
) -> UrlLinkDetailsResponseSchema:
    """
    Находит объект ссылки по шорт коду и выводит детальную информацию.

    Args:
        short_code: Шорт код ссылки из URL пути.
        db_session: Асинхронная сессия базы данных.
        urllink_service: Сервис для работы со ссылками.

    Returns:
        UrlLinkDetailsResponseSchema: Детальная информация об объекте ссылки.

    Raises:
        NotFoundException: Если ссылка не найдена.
    """

    # Проверка существования объекта ссылки
    link = await urllink_service.get_by_code(db_session, short_code=short_code)

    return UrlLinkDetailsResponseSchema(
        short_code=link.short_code,
        original_url=link.original_url,
        short_url=format_short_url(link.short_code),
        click_count=link.click_count,
    )
