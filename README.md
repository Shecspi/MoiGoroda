# 🗺️ Мои города

<div align="center">

![Logo](static/image/favicon.ico)

**Современный веб-сервис для отслеживания и визуализации путешествий**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-moi--goroda.ru-00b894?style=for-the-badge)](https://moi-goroda.ru/)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange?style=for-the-badge&logo=apache)](LICENSE)

</div>

## 📖 О проекте

**Мои города** — это полнофункциональный веб-сервис для отслеживания посещённых городов и стран. Приложение позволяет пользователям вести учёт своих путешествий, делиться достижениями с друзьями и открывать новые направления для поездок.

### ✨ Ключевые возможности

-   🗺️ **Интерактивные карты** — визуализация посещённых мест на картах OpenStreetMap
-   📊 **Подробная статистика** — детальная аналитика путешествий с графиками и диаграммами
-   👥 **Социальные функции** — подписки на других путешественников и уведомления о новых поездках
-   📝 **Личные заметки** — запись впечатлений с поддержкой Markdown
-   🌍 **Глобальный охват** — поддержка городов и стран по всему миру
-   📱 **Адаптивный дизайн** — отличная работа на всех устройствах

## 🚀 Технологический стек

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092e20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952b3?style=for-the-badge&logo=bootstrap&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white)

</div>

### Backend

-   **Django 4.2** — основной веб-фреймворк
-   **PostgreSQL** — основная база данных
-   **Django REST Framework** — API для фронтенда

### Frontend

-   **Bootstrap 5.3** — UI фреймворк
-   **Leaflet** — интерактивные карты
-   **Vanilla JavaScript** — клиентская логика
-   **Markdownify** — рендеринг Markdown

### Инструменты разработки

-   **Poetry** — управление зависимостями
-   **Pytest** — тестирование
-   **MyPy** — статическая типизация
-   **Ruff** — линтинг и форматирование
-   **Pre-commit** — автоматические проверки

## 🎯 Основные функции

### 🗺️ Карты и визуализация

-   **Интерактивные карты** городов и стран с использованием OpenStreetMap
-   **Слои границ** регионов и стран для лучшей ориентации
-   **Скриншоты карт** для сохранения достижений
-   **Фильтрация** по странам, регионам и коллекциям

### 📊 Статистика и аналитика

-   **Личная статистика** с графиками и диаграммами
-   **Географические достижения** по регионам и странам
-   **Временная статистика** посещений по годам и месяцам
-   **Сравнение** с другими пользователями

### 👥 Социальные возможности

-   **Подписки** на других путешественников
-   **Уведомления** о новых поездках подписанных пользователей
-   **Публичные профили** с настраиваемой приватностью
-   **Общие карты** для просмотра городов друзей

### 📝 Личный дневник путешествий

-   **Заметки и впечатления** с поддержкой Markdown
-   **Рейтинги городов** от 1 до 5 звёзд
-   **Даты посещений** с возможностью повторных визитов
-   **Сувениры** — отметки о наличии памятных вещей

### 🎒 Коллекции и планирование

-   **Тематические коллекции** (Золотое кольцо, города на Волге и др.)
-   **Список желаний** — города, которые хочется посетить
-   **Рекомендации** на основе посещённых мест
-   **Поиск** по городам, регионам и странам

## 🛠️ Установка и настройка

### Предварительные требования

-   Python 3.12+
-   Poetry
-   PostgreSQL 12+
-   Node.js 18+ и npm (обязательно для работы фронтенда)

### Быстрая установка

1. **Клонирование репозитория**

```bash
git clone https://github.com/Shecspi/MoiGoroda.git
cd MoiGoroda
```

2. **Установка Python и зависимостей**

```bash
# Установка нужной версии Python через pyenv
if [[ "$(pyenv versions 2> /dev/null)" != *"$(cat .python-version )"* ]]; then
    pyenv install $(cat .python-version)
fi

# Создание виртуального окружения и установка зависимостей
poetry env use $(cat .python-version)
poetry install
```

3. **Настройка окружения**

```bash
# Копирование файла конфигурации
cp MoiGoroda/.env.example MoiGoroda/.env

# Редактирование настроек базы данных в .env файле
# DATABASE_NAME=your_db_name
# DATABASE_USER=your_db_user
# DATABASE_PASSWORD=your_db_password
```

4. **Инициализация базы данных**

```bash
# Применение миграций
poetry run python manage.py migrate

# Создание суперпользователя
poetry run python manage.py createsuperuser

# Загрузка начальных данных (города, регионы, страны)
poetry run python manage.py loaddata initial_db.json
```

5. **Сборка статических файлов**

```bash
poetry run python manage.py collectstatic
```

6. **Запуск фронтенда (в отдельном терминале)**

```bash
cd frontend
npm install
npm run dev
```

7. **Запуск сервера разработки**

```bash
poetry run python manage.py runserver
```

> **Важно**: Для полноценной работы приложения необходимо запустить как бэкенд (Django), так и фронтенд (Vite). Фронтенд сервер обычно запускается на порту 5173.

### 🎯 Использование Makefile (рекомендуется)

Для упрощения работы с проектом доступен Makefile с набором полезных команд:

```bash
# Просмотр всех доступных команд
make help

# Полная установка проекта (одной командой!)
make setup

# Запуск сервера разработки
make run

# Запуск тестов
make test              # Все тесты
make test-unit         # Только unit-тесты
make test-integration  # Только интеграционные тесты
make test-e2e          # Только e2e-тесты
make test-fast         # Быстрые тесты (без slow)

# Проверка кода
make lint              # Все проверки (mypy + ruff)
make lint-mypy         # Только проверка типов
make lint-ruff         # Только линтинг
make format            # Автоформатирование кода

# Комплексные проверки (как в CI/CD)
make check             # Все проверки + тесты
make pre-commit        # Проверки перед коммитом

# Работа с БД
make migrate           # Применить миграции
make makemigrations    # Создать миграции
make shell             # Django shell

# Frontend
make frontend-install  # Установить зависимости
make frontend-build    # Собрать для продакшена
make frontend-dev      # Запустить в режиме разработки

# Очистка
make clean             # Удалить временные файлы и кэш
```

> **Совет**: Используйте `make setup` для быстрой установки всех зависимостей и настройки проекта!

### Установка для продакшена

Для продакшена дополнительно выполните:

```bash
# Создание директории для статических файлов
sudo mkdir -p /var/www/static
sudo chown www-data:www-data /var/www/static

# Установка только продакшен зависимостей
poetry install --only=main

# Сборка фронтенда для продакшена
cd frontend
npm ci --production
npm run build

# Сборка статических файлов Django
cd ..
poetry run python manage.py collectstatic --noinput
```

## 🧪 Тестирование

Проект включает комплексную систему тестирования с покрытием всех основных компонентов.

### Запуск тестов

**С использованием Makefile (рекомендуется):**

```bash
# Запуск всех тестов
make test

# Запуск только unit-тестов
make test-unit

# Запуск только интеграционных тестов
make test-integration

# Запуск только e2e-тестов
make test-e2e

# Запуск быстрых тестов (без slow)
make test-fast

# Запуск тестов с отчетом о покрытии
make test-cov
```

**Или напрямую через Poetry:**

```bash
# Запуск всех тестов
poetry run pytest

# Запуск тестов с покрытием
poetry run pytest --cov

# Запуск тестов конкретного модуля
poetry run pytest city/tests/

# Запуск тестов в параллельном режиме
poetry run pytest -n auto
```

## 🏗️ Архитектура проекта

```
MoiGoroda/
├── account/          # Система аутентификации и профили
├── city/            # Основная логика работы с городами
├── country/         # Работа со странами
├── region/          # Регионы и их статистика
├── collection/      # Тематические коллекции
├── subscribe/       # Система подписок и уведомлений
├── share/           # Публичные профили и статистика
├── place/           # Произвольные места на карте
├── dashboard/       # Административная панель
├── news/            # Новости и объявления
├── services/        # Общие сервисы и утилиты
├── templates/       # HTML шаблоны
├── static/          # Статические файлы (CSS, JS, изображения)
└── frontend/        # Исходники JavaScript
```

### Аутентификация

API использует сессионную аутентификацию Django.

## 🤝 Участие в разработке

Я всячески приветствую вклад в развитие проекта!

### Как помочь

1. **Fork** репозитория
2. Создайте **feature branch** (`git checkout -b feature/amazing-feature`)
3. Внесите изменения и добавьте тесты
4. Убедитесь, что код соответствует стандартам:
   ```bash
   make pre-commit  # Форматирование + линтинг + быстрые тесты
   # или полная проверка:
   make check       # Все проверки как в CI/CD
   ```
5. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
6. Отправьте **Pull Request**

### Полезные команды для разработчиков

```bash
make format      # Автоматическое форматирование кода
make lint        # Проверка типов и линтинг
make test-fast   # Быстрые тесты
make pre-commit  # Все проверки перед коммитом
make check       # Полная проверка как в CI/CD
```

## 📝 Лицензия

Этот проект распространяется под лицензией [Apache License 2.0](LICENSE).

## 📞 Контакты

-   **Автор**: Egor Vavilov (Shecspi)
-   **Сайт**: [moi-goroda.ru](https://moi-goroda.ru/)
-   **GitHub**: [@Shecspi](https://github.com/Shecspi)

---

<div align="center">

**⭐ Если проект вам понравился, поставьте звезду!**

[⬆ Наверх](#-мои-города)

</div>
