
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import Future
from typing import Any, Callable, Tuple

from . import stats

class Jobs(ThreadPoolExecutor):
    def __init__(self, max_workers = None, thread_name_prefix: str = "job", initializer = None, initargs: Tuple[Any, ...] = ...) -> None:
        super().__init__(max_workers, thread_name_prefix, initializer, initargs)

    def submit(self, fn: Callable, *args, **kwargs) -> Future:
        future = super().submit(fn, *args, **kwargs)
        return future
