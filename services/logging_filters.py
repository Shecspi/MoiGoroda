# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Logging filters for records without request context."""

from logging import Filter
from logging import LogRecord


class DefaultLogContextFilter(Filter):
    """Добавляет безопасные fallback-поля для общего formatter'а приложения."""

    def filter(self, record: LogRecord) -> bool:
        if not hasattr(record, 'IP'):
            record.IP = 'INTERNAL'
        if not hasattr(record, 'user'):
            record.user = 'CACHE'

        return True
