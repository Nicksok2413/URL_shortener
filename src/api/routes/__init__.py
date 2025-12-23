"""Основной API роутер, объединяющий все остальные роутеры."""

from fastapi import APIRouter

from . import urllinks

# Основной роутер API, объединяющий все остальные
api_router = APIRouter(prefix="/v1")  # Префикс /v1 для всех API эндпоинтов

api_router.include_router(urllinks.router)

__all__ = ["api_router"]
