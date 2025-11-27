.PHONY: help run-dev run-frontend-dev run-prod build-prod check format lint test frontend-install frontend-build lint-mypy lint-ruff

help: ## Показать справку по командам
	@printf "\033[0;32mДоступные команды:\033[0m\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;33m%-20s\033[0m %s\n", $$1, $$2}'

# Development
run-dev: ## Запустить сервер разработки
	@printf "\033[0;32mЗапуск сервера разработки...\033[0m\n"
	poetry run python manage.py runserver 0.0.0.0:8000

run-frontend-dev: ## Запустить frontend dev server
	@printf "\033[0;32mЗапуск frontend dev server...\033[0m\n"
	@printf "\033[0;33mFrontend будет доступен по адресу: http://localhost:5173\033[0m\n"
	@printf "\033[0;33mДля остановки нажмите Ctrl+C\033[0m\n\n"
	cd frontend && npm run dev

# Production
build-prod: ## Подготовить проект к production (собрать frontend и статику)
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\033[0;32mПодготовка к production режиму...\033[0m\n"
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\n\033[0;32m1. Установка зависимостей frontend...\033[0m\n"
	@$(MAKE) frontend-install
	@printf "\n\033[0;32m2. Сборка frontend...\033[0m\n"
	@$(MAKE) frontend-build
	@printf "\n\033[0;32m3. Сборка статики Django...\033[0m\n"
	@poetry run python manage.py collectstatic --noinput
	@printf "\n\033[0;32m========================================\033[0m\n"
	@printf "\033[0;32m✓ Подготовка завершена!\033[0m\n"
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\n\033[0;33mДля запуска сервера используйте:\033[0m\n"
	@printf "\033[0;33m  make run-prod\033[0m\n\n"

run-prod: ## Запустить сервер в production режиме
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\033[0;32mЗапуск в production режиме...\033[0m\n"
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\033[0;33mВнимание: убедитесь, что в .env файле установлено:\033[0m\n"
	@printf "\033[0;33m  DEBUG=False\033[0m\n"
	@printf "\033[0;33m  STATIC_ROOT=<путь к директории со статикой>\033[0m\n"
	@printf "\033[0;33m  ALLOWED_HOSTS=<список хостов через запятую>\033[0m\n"
	@printf "\n\033[0;32mЗапуск сервера...\033[0m\n"
	@printf "\033[0;33mСервер будет доступен по адресу: http://localhost:8000\033[0m\n"
	@printf "\033[0;33mДля остановки нажмите Ctrl+C\033[0m\n"
	@printf "\033[0;33mВнимание: используется --insecure для отдачи статики\033[0m\n\n"
	@poetry run python manage.py runserver 0.0.0.0:8000 --insecure

# Проверки
check: ## Запустить все проверки (форматирование, линтеры, тесты)
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\033[0;32mЗапуск всех проверок...\033[0m\n"
	@printf "\033[0;32m========================================\033[0m\n"
	@printf "\n\033[0;32m1. Форматирование кода...\033[0m\n"
	@$(MAKE) format
	@printf "\n\033[0;32m2. Проверка линтерами...\033[0m\n"
	@$(MAKE) lint
	@printf "\n\033[0;32m3. Запуск тестов...\033[0m\n"
	@$(MAKE) test
	@printf "\n\033[0;32m========================================\033[0m\n"
	@printf "\033[0;32m✓ Все проверки пройдены успешно!\033[0m\n"
	@printf "\033[0;32m========================================\033[0m\n"

format:
	@printf "\033[0;32mФорматирование кода...\033[0m\n"
	poetry run ruff format .
	poetry run ruff check --fix .

lint:
	@printf "\033[0;32mЗапуск проверок линтерами...\033[0m\n"
	@$(MAKE) lint-mypy
	@$(MAKE) lint-ruff
	@printf "\033[0;32m✓ Все проверки линтерами пройдены успешно!\033[0m\n"

lint-mypy:
	@printf "\033[0;32mПроверка типизации (mypy)...\033[0m\n"
	poetry run mypy .

lint-ruff:
	@printf "\033[0;32mПроверка кода (ruff check)...\033[0m\n"
	poetry run ruff check .
	@printf "\033[0;32mПроверка форматирования (ruff format)...\033[0m\n"
	poetry run ruff format --check .

test:
	@printf "\033[0;32mЗапуск всех тестов...\033[0m\n"
	poetry run pytest

# Вспомогательные команды для внутреннего использования
frontend-install:
	@printf "\033[0;32mУстановка зависимостей frontend...\033[0m\n"
	cd frontend && npm ci

frontend-build:
	@printf "\033[0;32mСборка frontend...\033[0m\n"
	cd frontend && npm run build
