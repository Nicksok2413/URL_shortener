"""Модель для формирования полного URL из шорт кода."""

from src.api.core.config import settings


def format_short_url(short_code: str) -> str:
    """
    Формирует полный URL из short_code.

    Args:
        short_code (str): Шорт код (случайно сгенерированная строка).

    Returns:
        str: Полный URL с использованием шорт кода.
    """
    full_url = f"http://{settings.API_HOST}:{settings.API_PORT}/{short_code}"
    return full_url
