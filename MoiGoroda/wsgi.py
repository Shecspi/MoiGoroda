"""
WSGI config for djangoProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/

Prometheus multiprocess mode: each gunicorn worker writes its own metrics file
into PROMETHEUS_MULTIPROC_DIR; the master process aggregates them on scrape.
"""

import os
import shutil
from pathlib import Path

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MoiGoroda.settings')

_prom_dir = Path(os.environ.get('PROMETHEUS_MULTIPROC_DIR', '/dev/shm/prometheus_metrics'))

# Очистка папки метрик при инициализации мастер-процесса Gunicorn.
# В мультипроцессном режиме папка должна быть пустой перед запуском.
if _prom_dir.exists():
    shutil.rmtree(_prom_dir)
_prom_dir.mkdir(parents=True, exist_ok=True)

os.environ['PROMETHEUS_MULTIPROC_DIR'] = str(_prom_dir)

application = get_wsgi_application()
