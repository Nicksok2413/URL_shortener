# Makefile - Единая точка входа для управления проектом

# .PHONY гарантирует, что make не будет путать эти команды с именами файлов
.PHONY: help install up down rebuild prune logs lint format types check

# Команда по умолчанию, которая будет вызвана при запуске `make`
default: help

help:
	@echo "Доступные команды:"
	@echo ""
	@echo "Установка зависимостей:"
	@echo "  install        - Установить Python зависимости"
	@echo ""
	@echo "Управление Docker окружением:"
	@echo "  up             - Запустить все сервисы в фоновом режиме"
	@echo "  down           - Остановить все сервисы"
	@echo "  rebuild        - Пересобрать образы и запустить сервисы"
	@echo "  prune          - Остановить сервисы и УДАЛИТЬ ВСЕ ДАННЫЕ (БД, логи)"
	@echo "  logs           - Показать логи всех сервисов"
	@echo ""
	@echo "Проверка качества кода и тесты:"
	@echo "  lint           - Проверить код линтером Ruff"
	@echo "  lint-fix       - Исправить код линтером Ruff"
	@echo "  format-check   - Проверить код форматтером Ruff"
	@echo "  format         - Отформатировать код форматтером Ruff"
	@echo "  types          - Проверить статическую типизацию mypy"
	@echo "  check          - Запустить статический анализ (lint, format-check, types) последовательно"


# ------------------------------------------------------------------------------
# Установка зависимостей
# ------------------------------------------------------------------------------
install:
	@echo "-> Установка зависимостей с помощью Poetry..."
	poetry install
	@echo "-> Зависимости успешно установлены."

# ------------------------------------------------------------------------------
# Управление Docker окружением
# ------------------------------------------------------------------------------
up:
	docker compose up -d

down:
	docker compose down

rebuild: down
	@echo "-> Пересборка и запуск сервисов..."
	docker compose up -d --build
	@echo "-> Сервисы успешно пересобраны и запущены."

prune:
	@echo "ВНИМАНИЕ: Эта команда остановит контейнеры и УДАЛИТ ВСЕ ДАННЫЕ В ТОМАХ (volumes)."
	@read -p "Вы уверены, что хотите продолжить? [y/N] " confirm && \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "-> Начинаем полную очистку..."; \
		echo " * Чистим основное окружение"; \
		docker compose down -v; \
		echo " * Чистим тестовое окружение"; \
		docker compose -f docker-compose.test.yml down -v; \
		echo "-> Окружение полностью очищено."; \
	else \
		echo "-> Очистка отменена."; \
	fi

logs:
	docker compose logs -f

# ------------------------------------------------------------------------------
# Проверка качества кода и тесты
# ------------------------------------------------------------------------------
lint:
	@echo "-> Проверка кода с помощью Ruff linter..."
	poetry run ruff check .

lint-fix:
	@echo "-> Исправление кода с помощью Ruff linter..."
	poetry run ruff check . --fix

format-check:
	@echo "-> Форматирование кода с помощью Ruff formatter..."
	poetry run ruff format . --check

format:
	@echo "-> Форматирование кода с помощью Ruff formatter..."
	poetry run ruff format .

types:
	@echo "-> Статическая проверка типов с помощью mypy..."
	poetry run mypy .

check: lint format-check types
	@echo "-> Статический анализ (lint, format, types) успешно пройден!"
