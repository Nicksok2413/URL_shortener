"""Настройка логирования для приложения."""

import os
import sys

from loguru import logger
from pydantic import BaseModel, Field

from .config import settings


class LogConfig(BaseModel):
    """Конфигурация логирования."""

    level: str = Field(default=settings.LOG_LEVEL, description="Уровень логирования")
    format: str = Field(
        default=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        ),
        description="Формат лог сообщения",
    )
    rotation: str = Field(default="10 MB", description="Ротация лог-файлов по размеру")
    retention: str = Field(default="7 days", description="Время хранения лог-файлов")
    serialize: bool = Field(default=False, description="Сериализовать логи в JSON")
    enable_file_logging: bool = Field(default=True, description="Включить логирование в файл")
    log_file_path: str = Field(
        default="logs/{name}_{time:YYYY-MM-DD}.log",
        description="Путь к файлу логов",
    )


def configure_logging():
    """
    Настраивает Loguru для приложения.

    Удаляет все предыдущие обработчики перед добавлением новых,
    чтобы избежать дублирования при повторных вызовах (например, в тестах):
    """

    log_config = LogConfig()

    # Удаляем все предыдущие обработчики, чтобы избежать дублирования
    logger.remove()

    # Флаг, включен ли режим разработки/тестирования
    is_debug: bool = settings.DEBUG

    # Обработчик для вывода в консоль (stderr)
    logger.add(
        sys.stderr,
        level=log_config.level,
        format=log_config.format,
        serialize=log_config.serialize,
        # Фильтруем стандартные логи доступа uvicorn по имени логгера
        filter=lambda record: record["name"] != "uvicorn.access",
        colorize=True,  # Цветной вывод
        backtrace=is_debug,  # Подробный трейсбек в режиме разработки/тестирования
        diagnose=is_debug,  # Диагностика переменных в режиме разработки/тестирования
    )

    # Обработчик для записи в файл (по умолчанию включен)
    if log_config.enable_file_logging:
        # Директория для лог-файлов
        log_dir = os.path.dirname(log_config.log_file_path)

        # Пытаемся создать директорию
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError as exc:
                # Если не удалось создать директорию, логируем через stderr
                logger.warning(
                    f"Не удалось создать директорию для логов '{log_dir}': {exc}. "
                    f"Логирование в файл для приложения будет отключено."
                )
        else:
            logger.add(
                log_config.log_file_path,
                level=log_config.level,
                format=log_config.format,
                rotation=settings.LOG_ROTATION,
                retention=settings.LOG_RETENTION,
                serialize=log_config.serialize,
                encoding="utf-8",
                compression="zip",  # Сжимать старые логи
                enqueue=True,  # Асинхронная запись для производительности
            )

    logger.info(
        f"Loguru сконфигурирован. Уровень: {log_config.level}. "
        f"Режим разработки/тестирования: {is_debug}. "
        f"Логирование в файл: {'Включено' if log_config.enable_file_logging else 'Отключено'}."
    )


# Инициализация логирования при импорте модуля
configure_logging()

# Экспортируем настроенный логгер для использования в других модулях
log = logger
