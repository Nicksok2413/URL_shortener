"""Централизованная настройка логирования для всех сервисов проекта."""

import os
import sys
from typing import TYPE_CHECKING

from loguru import logger as global_loguru_logger
from pydantic import BaseModel, Field

# Импортируем Logger только для проверки типов
if TYPE_CHECKING:
    from loguru import Logger


class LogConfig(BaseModel):
    """Конфигурация логирования."""

    level: str = Field(default="INFO", description="Уровень логирования")
    format: str = Field(
        default=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[service_name]}</cyan> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        ),
        description="Формат лог сообщения",
    )
    rotation: str = Field(default="10 MB", description="Ротация лог-файлов по размеру")
    retention: str = Field(default="7 days", description="Время хранения лог-файлов")
    serialize: bool = Field(default=False, description="Сериализовать логи в JSON")
    enable_debug_mode: bool = Field(default=False, description="Включить режим разработки/тестирования")
    enable_file_logging: bool = Field(default=True, description="Включить логирование в файл")
    log_file_path: str = Field(
        default="logs/{service_name}_{time:YYYY-MM-DD}.log",
        description="Путь к файлу логов",
    )


def setup_logger(
    service_name: str,
    log_config: LogConfig | None = None,
    log_level_override: str | None = None,
    log_rotation_override: str | None = None,
    log_retention_override: str | None = None,
    debug_mode_override: bool | None = None,
) -> "Logger":
    """
    Настраивает Loguru логгер для указанного сервиса и возвращает его экземпляр.

    Удаляет все предыдущие обработчики перед добавлением новых,
    чтобы избежать дублирования при повторных вызовах (например, в тестах).

    Args:
        service_name: Имя сервиса (например, "API", "Alembic").
        log_config: Объект конфигурации LogConfig. Если None, используются значения по умолчанию.
        log_level_override: Переопределяет уровень логирования из конфигурации.
        log_rotation_override: Переопределяет ротацию лог-файлов по размеру (в мегабайтах) из конфигурации.
        log_retention_override: Переопределяет время хранения лог-файлов (в днях) из конфигурации.
        debug_mode_override: Переопределяет включение режима разработки/тестирования из конфигурации.

    Returns:
        Сконфигурированный экземпляр логгера Loguru.
    """
    if log_config is None:
        current_config = LogConfig()
    else:
        current_config = log_config

    # Применяем переопределения, если они есть
    if log_level_override:
        current_config.level = log_level_override.upper()

    if log_rotation_override:
        current_config.rotation = log_rotation_override

    if log_retention_override:
        current_config.retention = log_retention_override

    if debug_mode_override:
        current_config.enable_debug_mode = debug_mode_override

    # Удаляем все предыдущие обработчики, чтобы избежать дублирования
    global_loguru_logger.remove()

    # Используем `bind` для добавления service_name в `extra` словарь логгера
    # Это позволяет использовать {extra[service_name]} в формате
    # Этот экземпляр будет "помнить" это значение
    service_specific_logger = global_loguru_logger.bind(service_name=service_name)

    # Обработчик для вывода в консоль (stderr)
    service_specific_logger.add(
        sys.stderr,
        level=current_config.level,
        format=current_config.format,
        serialize=current_config.serialize,
        filter=lambda record: record["name"] != "uvicorn.access",  # Фильтруем стандартные логи доступа uvicorn
        colorize=True,  # Цветной вывод
        backtrace=current_config.enable_debug_mode,  # Подробный трейсбек в режиме разработки/тестирования
        diagnose=current_config.enable_debug_mode,  # Диагностика переменных в режиме разработки/тестирования
    )

    # Обработчик для записи в файл (по умолчанию включен)
    if current_config.enable_file_logging:
        # Меняем service_name
        log_file_path_formatted = current_config.log_file_path.replace("{service_name}", service_name.lower())

        # Вычисляем директорию. Разбиваем строку по "{time}", чтобы отсечь динамическую часть имени файла.
        # Если в пути нет {time}, берем просто директорию от файла.
        if "{time}" in log_file_path_formatted:
            log_dir = os.path.dirname(log_file_path_formatted.split("{time}")[0])
        else:
            log_dir = os.path.dirname(log_file_path_formatted)

        # Пытаемся создать директорию
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError as exc:
                # Если не удалось создать директорию, логируем через stderr
                service_specific_logger.warning(
                    f"Не удалось создать директорию для логов '{log_dir}': {exc}. "
                    f"Логирование в файл для для сервиса '{service_name}' будет отключено."
                )
        else:
            service_specific_logger.add(
                log_file_path_formatted,
                level=current_config.level,
                format=current_config.format,
                rotation=current_config.rotation,
                retention=current_config.retention,
                serialize=current_config.serialize,
                encoding="utf-8",
                compression="zip",  # Сжимать старые логи
                enqueue=True,  # Асинхронная запись для производительности
            )

    file_logging_status = "Включено" if current_config.enable_file_logging else "Отключено"

    service_specific_logger.info(
        f"Loguru сконфигурирован. Уровень: {current_config.level}. Логирование в файл: {file_logging_status}."
    )

    return service_specific_logger


__all__ = ["setup_logger", "LogConfig"]
