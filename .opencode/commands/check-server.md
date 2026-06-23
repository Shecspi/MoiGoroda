---
description: Собрать аналитику работы сервера moi-goroda.ru через Grafana/Prometheus за последние 24 часа
subtask: true
---
Открой SSH тунели для доступа к Grafana и Prometheus на prod.moi-goroda (если ещё не открыты):

```bash
nc -z 127.0.0.1 3009 2>/dev/null || ssh -N -L 3009:127.0.0.1:3000 prod.moi-goroda &
nc -z 127.0.0.1 9091 2>/dev/null || ssh -N -L 9091:localhost:9090 prod.moi-goroda &
```

Собери аналитику работы сервера moi-goroda.ru за последние 24 часа через Grafana MCP.

Datasource: prometheus (uid: ffkhfvqyeyzuob)

### 1. Node Exporter (сервер)
- instance: 127.0.0.1:9100, job: node_exporter
- CPU Busy: `100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle",instance="127.0.0.1:9100",job="node_exporter"}[5m])))` и среднее за 24h
- RAM: `clamp_min((1 - (node_memory_MemAvailable_bytes{instance="127.0.0.1:9100", job="node_exporter"} / node_memory_MemTotal_bytes{instance="127.0.0.1:9100", job="node_exporter"})) * 100, 0)`
- Disk /: `(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes * 100` (mountpoint="/", fstype!="rootfs")
- Swap: `(node_memory_SwapTotal_bytes - node_memory_SwapFree_bytes) / node_memory_SwapTotal_bytes * 100`
- Uptime: `node_time_seconds - node_boot_time_seconds`
- Load: `scalar(node_load1) * 100 / count(count(node_cpu_seconds_total) by (cpu))`
- Network: трафик на eth0

### 2. Django (приложение)
- instance: 127.0.0.1:9101
- Request rate: `sum(irate(django_http_requests_total_by_transport_total{instance="127.0.0.1:9101"}[5m]))`
- Latency p50/p95/p99: `histogram_quantile(0.50, sum(rate(django_http_requests_latency_seconds_by_view_method_bucket{instance="127.0.0.1:9101"}[5m])) by (le))`
- Total requests: `django_http_requests_total_by_transport_total{instance="127.0.0.1:9101"}`
- Response status (обязательно):
  - Ошибки 404: `sum(rate(django_http_responses_total_by_status_total{status="404", instance="127.0.0.1:9101"}[5m]))` и общее число за 24h — `sum(increase(django_http_responses_total_by_status_total{status="404", instance="127.0.0.1:9101"}[24h]))`
  - Ошибки 500: `sum(rate(django_http_responses_total_by_status_total{status="500", instance="127.0.0.1:9101"}[5m]))` и общее число за 24h — `sum(increase(django_http_responses_total_by_status_total{status="500", instance="127.0.0.1:9101"}[24h]))`
  - Если метрика `django_http_responses_total_by_status_total` недоступна, используй `django_http_requests_total_by_status_total`
- Проверь также доступность метрик ошибок БД
- Медленные запросы (обязательно):
  - Топ-5 эндпоинтов по p95 latency за последние 5m: `topk(5, histogram_quantile(0.95, sum(rate(django_http_requests_latency_seconds_by_view_method_bucket{instance="127.0.0.1:9101"}[5m])) by (le, view)))`
  - Топ-3 эндпоинта по p95 latency за последние 24h: `topk(3, histogram_quantile(0.95, sum(rate(django_http_requests_latency_seconds_by_view_method_bucket{instance="127.0.0.1:9101"}[24h])) by (le, view)))`
  - Если latency-гистограмма недоступна по `view`, попробуй без группировки: `histogram_quantile(0.95, sum(rate(django_http_requests_latency_seconds_by_view_method_bucket{instance="127.0.0.1:9101"}[5m])) by (le))`
  - Эндпоинт считается медленным, если p95 > 500ms

### 3. PostgreSQL
- instance: 127.0.0.1:9187, datname: moi_goroda__db
- Active/idle sessions: `pg_stat_activity_count{datname="moi_goroda__db", instance="127.0.0.1:9187"}`
- Cache hit rate: `pg_stat_database_blks_hit / (pg_stat_database_blks_read + pg_stat_database_blks_hit)`
- Transactions: `irate(pg_stat_database_xact_commit[5m])` и rollback
- Conflicts/deadlocks: `pg_stat_database_conflicts`

### 4. Loki (логи)
- datasource: Loki (uid: dfpwlwxt5x1q8b)
- Доступность: проверь, что Loki отвечает (любой простой запрос)
- Статистика по уровням за 24h:
  - ERROR: `sum(count_over_time({level="ERROR"} [24h]))`
  - WARNING: `sum(count_over_time({level="WARNING"} [24h]))`
  - INFO: `sum(count_over_time({level="INFO"} [24h]))`
  - Распределение по уровням: `sum(count_over_time({job=~".+"} [24h])) by (level)`
- Error rate по источникам (5m):
  - app: `rate({level="ERROR",job="moigoroda-app"} [5m])`
  - payments: `rate({level="ERROR",job="moigoroda-payments"} [5m])`
  - cron: `rate({level="ERROR",job="moigoroda-cron"} [5m])`
- Последние ошибки (последние 10): `{level="ERROR"}` (limit=10)
- Медленные запросы из логов (обязательно):
  - django.request WARNING с duration: `{job="moigoroda-app"} |= "duration" | logfmt`
  - Если logfmt не поддерживается: `{job="moigoroda-app"} |~ "(slow|duration|timeout)"`
  - Критерий: duration > 500ms считается медленным

### Формат вывода
Предоставь таблицу метрик со статусами (✅ / ⚠️ / ❌) и краткую сводку с проблемами и рекомендациями.
