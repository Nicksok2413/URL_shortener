"""Создаём экземпляр настроенного логгера для API"""

from src.core_shared.logging_setup import setup_logger

from .config import settings

# Получаем экземпляр логгера API
api_log = setup_logger(
    service_name="API",
    log_level_override=settings.LOG_LEVEL,
    log_rotation_override=settings.LOG_ROTATION,
    log_retention_override=settings.LOG_RETENTION,
    debug_mode_override=settings.DEBUG,
)
