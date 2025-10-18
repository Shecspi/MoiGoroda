.PHONY: help install run test lint format check clean migrate collectstatic shell

help: ## Показать справку по командам
	@printf "\033[0;32mДоступные команды:\033[0m\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;33m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	@printf "\033[0;32mУстановка зависимостей...\033[0m\n"
	poetry install

install-dev: ## Установить зависимости для разработки
	@printf "\033[0;32mУстановка зависимостей для разработки...\033[0m\n"
	poetry install --with dev,test

run: ## Запустить сервер разработки
	@printf "\033[0;32mЗапуск сервера разработки...\033[0m\n"
	poetry run python manage.py runserver 0.0.0.0:8000

migrate: ## Применить миграции
	@printf "\033[0;32mПрименение миграций...\033[0m\n"
	poetry run python manage.py migrate

makemigrations: ## Создать миграции
	@printf "\033[0;32mСоздание миграций...\033[0m\n"
	poetry run python manage.py makemigrations

collectstatic: ## Собрать статические файлы
	@printf "\033[0;32mСборка статических файлов...\033[0m\n"
	poetry run python manage.py collectstatic --noinput

shell: ## Запустить Django shell
	@printf "\033[0;32mЗапуск Django shell...\033[0m\n"
	poetry run python manage.py shell

# Тесты
test: ## Запустить все тесты
	@printf "\033[0;32mЗапуск всех тестов...\033[0m\n"
	poetry run pytest

test-fast: ## Запустить быстрые тесты (unit и integration)
	@printf "\033[0;32mЗапуск быстрых тестов...\033[0m\n"
	poetry run pytest -m "not slow"

test-unit: ## Запустить только unit-тесты
	@printf "\033[0;32mЗапуск unit-тестов...\033[0m\n"
	poetry run pytest -m unit

test-integration: ## Запустить только интеграционные тесты
	@printf "\033[0;32mЗапуск интеграционных тестов...\033[0m\n"
	poetry run pytest -m integration

test-e2e: ## Запустить только e2e-тесты
	@printf "\033[0;32mЗапуск e2e-тестов...\033[0m\n"
	poetry run pytest -m e2e

test-cov: ## Запустить тесты с отчетом о покрытии
	@printf "\033[0;32mЗапуск тестов с отчетом о покрытии...\033[0m\n"
	poetry run pytest --cov=. --cov-report=html --cov-report=term

# Линтеры и проверки
lint: ## Запустить все проверки (mypy + ruff)
	@printf "\033[0;32mЗапуск всех проверок...\033[0m\n"
	@$(MAKE) lint-mypy
	@$(MAKE) lint-ruff
	@printf "\033[0;32m✓ Все проверки пройдены успешно!\033[0m\n"

lint-mypy: ## Проверка типизации с помощью mypy
	@printf "\033[0;32mПроверка типизации (mypy)...\033[0m\n"
	poetry run mypy .

lint-ruff: ## Проверка кода с помощью ruff
	@printf "\033[0;32mПроверка кода (ruff check)...\033[0m\n"
	poetry run ruff check .
	@printf "\033[0;32mПроверка форматирования (ruff format)...\033[0m\n"
	poetry run ruff format --check .

format: ## Автоматическое форматирование кода с помощью ruff
	@printf "\033[0;32mФорматирование кода...\033[0m\n"
	poetry run ruff format .
	poetry run ruff check --fix .

# Комплексные проверки
check: ## Запустить все проверки и тесты (как в CI/CD)
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\033[0;32mЗапуск всех проверок (как в CI/CD)...\033[0m\n"
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\n"
	@$(MAKE) lint-mypy
	@printf "\n"
	@$(MAKE) lint-ruff
	@printf "\n"
	@$(MAKE) test
	@printf "\n"
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\033[0;32m✓ Все проверки пройдены успешно!\033[0m\n"
	@printf "\033[0;32m========================================\033[0m\n"

# Очистка
clean: ## Удалить временные файлы и кэш
	@printf "\033[0;32mОчистка временных файлов...\033[0m\n"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@printf "\033[0;32m✓ Очистка завершена\033[0m\n"

# Frontend
frontend-install: ## Установить зависимости frontend
	@printf "\033[0;32mУстановка зависимостей frontend...\033[0m\n"
	cd frontend && npm ci

frontend-build: ## Собрать frontend
	@printf "\033[0;32mСборка frontend...\033[0m\n"
	cd frontend && npm run build

frontend-dev: ## Запустить frontend в режиме разработки
	@printf "\033[0;32mЗапуск frontend в режиме разработки...\033[0m\n"
	cd frontend && npm run dev

# Полная установка проекта
setup: ## Полная установка проекта (зависимости + миграции + frontend)
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\033[0;32mПолная установка проекта...\033[0m\n"
	@printf "\033[0;32m========================================\033[0m\n"
	@$(MAKE) install-dev
	@$(MAKE) frontend-install
	@$(MAKE) migrate
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\033[0;32m✓ Установка завершена!\033[0m\n"
	@printf "\033[0;32mЗапустите 'make run' для старта сервера\033[0m\n"
	@printf "\033[0;32m========================================\033[0m\n"

# Pre-commit проверки
pre-commit: ## Проверки перед коммитом
	@printf "\033[0;32mЗапуск pre-commit проверок...\033[0m\n"
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) test-fast
	@printf "\033[0;32m✓ Pre-commit проверки пройдены!\033[0m\n"

