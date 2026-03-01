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

5. **Настройка `.env` файла для разработки**

```bash
# Убедитесь, что в .env файле установлено:
DEBUG=True
TESTING=True
```

6. **Запуск проекта в режиме разработки**

Используйте команды Makefile (см. раздел "Использование Makefile"):

-   `make run-frontend-dev` — запуск frontend dev server
-   `make run-dev` — запуск Django dev server

> **Важно**: Для полноценной работы приложения необходимо запустить оба сервера одновременно в разных терминалах.

### 🎯 Использование Makefile (рекомендуется)

Для упрощения работы с проектом доступен Makefile с набором полезных команд:

```bash
# Просмотр всех доступных команд
make help
```

#### 🚀 Запуск в режиме разработки (Development)

Для запуска проекта в режиме разработки необходимо:

1. **Настроить `.env` файл** с параметрами:

    ```env
    DEBUG=True
    TESTING=True
    ```

2. **Запустить frontend dev server** (в первом терминале):

    ```bash
    make run-frontend-dev
    ```

    Frontend будет доступен на `http://localhost:5173`

3. **Запустить Django dev server** (во втором терминале):
    ```bash
    make run-dev
    ```
    Backend будет доступен на `http://localhost:8000`

> **Важно**: Для полноценной работы приложения необходимо запустить оба сервера одновременно.

#### 🏭 Запуск в production режиме

Для запуска проекта в production режиме необходимо:

1. **Настроить `.env` файл** с параметрами:

    ```env
    DEBUG=False
    TESTING=False
    STATIC_ROOT=/path/to/static/directory
    ALLOWED_HOSTS=your-domain.com,www.your-domain.com
    ```

2. **Собрать проект**:

    ```bash
    make build-prod
    ```

    Эта команда выполнит:

    - Установку зависимостей frontend
    - Сборку frontend
    - Сборку статических файлов Django

3. **Запустить production сервер**:
    ```bash
    make run-prod
    ```

#### ✅ Проверка кода

```bash
# Комплексная проверка (форматирование, линтеры, тесты)
make check
```

> **Совет**: Используйте `make check` перед коммитом для проверки всего кода!

### Установка для продакшена

Для продакшена используйте команды Makefile:

```bash
# Настройте .env файл с параметрами:
# DEBUG=False
# TESTING=False
# STATIC_ROOT=/var/www/static
# ALLOWED_HOSTS=your-domain.com

# Создание директории для статических файлов
sudo mkdir -p /var/www/static
sudo chown www-data:www-data /var/www/static

# Сборка проекта
make build-prod

# Запуск production сервера
make run-prod
```

> **Примечание**: В production рекомендуется использовать веб-сервер (Nginx/Apache) для отдачи статики вместо `--insecure` флага.

### Премиум-подписки: истечение по расписанию

Чтобы просроченные премиум-подписки переводились в статус «Истекла», нужно ежедневно запускать management-команду, например через cron или systemd timer:

```bash
# Пример записи в crontab (раз в день в 03:00)
0 3 * * * cd /path/to/MoiGoroda && .venv/bin/python manage.py expire_premium_subscriptions
```

Подставьте свой путь к проекту и к интерпретатору Python (или используйте `poetry run`).

## 🧪 Тестирование

Проект включает комплексную систему тестирования с покрытием всех основных компонентов.

### Запуск тестов

**С использованием Makefile:**

```bash
# Запуск всех тестов
make test
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

> **Примечание**: Для запуска всех проверок (форматирование, линтеры, тесты) используйте `make check`.

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
    make check  # Форматирование + линтинг + тесты
    ```
5. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
6. Отправьте **Pull Request**

### Полезные команды для разработчиков

```bash
make check       # Полная проверка (форматирование, линтеры, тесты)
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
