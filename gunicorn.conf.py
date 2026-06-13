from typing import Any
from prometheus_client import multiprocess


def child_exit(server: Any, worker: Any) -> None:
    """Clean up the dead worker's Prometheus metrics file on shutdown."""
    multiprocess.mark_process_dead(worker.pid)  # type: ignore[no-untyped-call]
