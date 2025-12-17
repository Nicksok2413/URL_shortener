"""Зависимости для FastAPI."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.core.database import get_db_session

# --- Типизация для инъекции сессии базы данных ---

DBSession = Annotated[AsyncSession, Depends(get_db_session)]
