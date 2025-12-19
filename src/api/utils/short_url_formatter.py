"""Модель для формирования полного URL из шорт кода."""

from fastapi import Request


def format_short_url(short_code: str, request: Request) -> str:
    """
    Формирует полный URL из short_code.
    Использует base_url из запроса.

    Args:
        short_code (str): Шорт код (случайно сгенерированная строка).
        request (Request): Объект запроса.

    Returns:
        str: Полный URL с использованием шорт кода.
    """
    base_url = str(request.base_url).rstrip("/")
    full_url = f"{base_url}/{short_code}"

    return full_url
