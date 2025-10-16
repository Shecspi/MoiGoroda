#!/usr/bin/env python
"""
Скрипт для проверки настроек Django в CI/CD
"""

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoiGoroda.settings')

# Загружаем .env вручную для диагностики
from dotenv import load_dotenv

env_path = Path(__file__).parent / 'MoiGoroda' / '.env'
print(f'🔍 Загружаем .env из: {env_path}')
print(f'📁 .env существует: {env_path.exists()}')

if env_path.exists():
    with open(env_path, 'r') as f:
        print('\n📄 Содержимое .env:')
        for line in f:
            if line.strip() and not line.startswith('#'):
                key = line.split('=')[0]
                if key in ['DEBUG', 'TESTING', 'DATABASE_ENGINE', 'DATABASE_NAME']:
                    print(f'  {line.strip()}')

load_dotenv(env_path)

print(f'\n🔧 Переменные окружения после load_dotenv:')
print(f'  DEBUG from env: {os.getenv("DEBUG")}')
print(f'  TESTING from env: {os.getenv("TESTING")}')
print(f'  DATABASE_ENGINE from env: {os.getenv("DATABASE_ENGINE")}')

# Проверяем sys.argv
print(f'\n📋 sys.argv: {sys.argv}')
print(f"  'test' in sys.argv: {'test' in sys.argv}")
print(f"  'pytest' in sys.modules: {'pytest' in sys.modules}")

# Импортируем настройки Django
import django

django.setup()

from django.conf import settings

print(f'\n⚙️  Django Settings:')
print(f'  settings.DEBUG: {settings.DEBUG}')
print(f"  settings.DATABASES['default']['ENGINE']: {settings.DATABASES['default']['ENGINE']}")
print(
    f"  settings.DATABASES['default']['NAME']: {settings.DATABASES['default'].get('NAME', 'not set')}"
)

# Проверяем TESTING из settings
from MoiGoroda.settings import TESTING

print(f'  TESTING variable: {TESTING}')

print('\n✅ Проверка завершена')
