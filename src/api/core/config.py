"""Конфигурация приложения."""

from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Основные настройки приложения.

    Наследуется от Pydantic BaseSettings для автоматической валидации и загрузки переменных окружения.
    """

    # --- Статические настройки ---

    # Название приложения
    PROJECT_NAME: str = "Habit Tracker Telegram Bot"
    # Версия API
    API_VERSION: str = "0.1.0"
    # Хост API
    API_HOST: str = "0.0.0.0"  # noqa: S104 - 0.0.0.0 необходимо для Docker контейнера
    # Порт API
    API_PORT: int = 8000

    # --- Настройки, читаемые из .env ---

    # Настройки БД
    DB_NAME: str = Field(default="url_shortener_db", description="Название базы данных")
    DB_USER: str = Field(default="url_shortener_user", description="Имя пользователя базы данных")
    DB_PASSWORD: str = Field(..., description="Пароль пользователя базы данных")
    DB_HOST: str = Field(
        default="db",
        description="Имя хоста базы данных (название сервиса в Docker)",
    )
    DB_PORT: int = Field(default=5432, description="Порт хоста базы данных")

    # Настройки режима разработки/тестирования (по умолчанию `False` для продакшен)
    DEBUG: bool = Field(default=False, description="Режим разработки/тестирования")

    # Настройки логирования
    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")
    LOG_ROTATION: str = Field(default="10 MB", description="Размер файла логов в мегабайтах")
    LOG_RETENTION: str = Field(default="7 days", description="Количество файлов логов")

    # --- Вычисляемые поля ---

    # Формируем URL основной базы данных
    @computed_field(repr=False)
    def DB_URL(self) -> str:
        """Собирает URL для SQLAlchemy."""

        # Экранируем имя пользователя и пароль, чтобы спецсимволы не ломали URL
        encoded_user = quote_plus(self.DB_USER)
        encoded_password = quote_plus(self.DB_PASSWORD)

        db_url = f"postgresql+psycopg://{encoded_user}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        return db_url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Имена переменных окружения не чувствительны к регистру
        extra="ignore",  # Игнорировать лишние переменные .env
    )


# Создаем глобальный экземпляр настроек
settings = Settings()  # type: ignore[call-arg]
