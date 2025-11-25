#!/usr/bin/env bash
set -euo pipefail

echo "Сборка статики Django..."
poetry run python3 manage.py collectstatic --noinput
echo "Готово."
