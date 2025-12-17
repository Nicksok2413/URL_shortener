"""Основной файл приложения FastAPI для сервиса сокращения ссылок.

Отвечает за:
- Создание и конфигурацию экземпляра FastAPI.
- Управление жизненным циклом приложения (подключение к БД).
- Регистрацию роутеров и обработчиков исключений.
- Предоставление эндпоинта для проверки работоспособности (health check).
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Response, status
from sqlalchemy import text

from src.api.core.config import settings
from src.api.core.database import db
from src.api.core.dependencies import DBSession


# Определяем lifespan для управления подключением к БД
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Контекстный менеджер для управления жизненным циклом приложения.
    Выполняет подключение к БД при старте приложения и корректное отключение при его остановке.

    Args:
        app (FastAPI): Экземпляр приложения FastAPI.
    """
    print("Инициализация приложения...")
    try:
        await db.connect()
        yield
    except Exception as exc:
        # Логируем критическую ошибку, если подключение к БД не удалось при старте
        print(f"Критическая ошибка при старте приложения: {exc}")
        # Повторно вызываем исключение, чтобы приложение не запустилось в нерабочем состоянии
        raise exc
    finally:
        print("Остановка приложения...")
        await db.disconnect()
        print("Приложение остановлено.")


# Создаем экземпляр FastAPI
def create_app() -> FastAPI:
    """
    Создает и конфигурирует экземпляр приложения FastAPI.

    Returns:
        FastAPI: Сконфигурированный экземпляр приложения.
    """
    print(f"Создание экземпляра FastAPI для '{settings.PROJECT_NAME} {settings.API_VERSION}'")
    print(f"Режим разработки/тестирования: {settings.DEBUG}.")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        description="API для сервиса сокращения ссылок",
    )

    print(f"Приложение '{settings.PROJECT_NAME} {settings.API_VERSION}' сконфигурировано и готово к запуску.")
    return app


# Создаем основной экземпляр приложения
app = create_app()


@app.get(
    "/healthcheck",
    tags=["Health Check"],
    summary="Проверка работоспособности сервиса и его зависимостей",
    description=(
        "Проверяет, что API запущен и имеет доступ к БД. В случае недоступности БД возвращает HTTP статус 503."
    ),
)
async def health_check(
    response: Response,
    db_session: DBSession,
) -> dict[str, Any]:
    """
    Эндпоинт для проверки работоспособности сервиса.

    Args:
        response (Response): Объект ответа FastAPI для управления статус-кодом.
        db_session (DBSession): Зависимость, предоставляющая сессию БД.

    Returns:
        dict: Словарь со статусом API и его зависимостей.
    """

    try:
        # Выполняем простой и быстрый запрос к БД для проверки соединения
        await db_session.execute(text("SELECT 1"))
        is_db_ok = True
    except Exception:
        # Ошибка означает, что подключение к БД потеряно или неисправно
        is_db_ok = False

    # Формируем тело ответа
    response_body = {
        "api_status": "ok",
        "dependencies": {"database": "ok" if is_db_ok else "error"},
    }

    # Если БД недоступна, меняем HTTP статус ответа на 503 Service Unavailable
    if not is_db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        print("Health check провален: нет подключения к БД.")

    return response_body
