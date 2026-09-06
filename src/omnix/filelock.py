"""Lightweight file-based lock for environments without filelock dependency."""

import os
import time
from pathlib import Path
from typing import Optional


class FileLock:
    """A minimal file lock implementation.

    Creates an exclusive lock file to coordinate access across processes.
    This is not a full replacement for the third-party ``filelock`` package
    but provides the subset of functionality needed by the credential store.
    """

    def __init__(self, lock_file: str, timeout: Optional[float] = 10, delay: float = 0.05):
        self.lock_file = Path(lock_file)
        self.timeout = timeout
        self.delay = delay
        self._fd: Optional[int] = None

    def acquire(self) -> None:
        start_time = time.time()
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)

        while True:
            try:
                self._fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                return
            except FileExistsError:
                if self.timeout is not None and (time.time() - start_time) >= self.timeout:
                    raise TimeoutError(f"Timeout while waiting for lock {self.lock_file}")
                time.sleep(self.delay)

    def release(self) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        try:
            self.lock_file.unlink()
        except FileNotFoundError:
            pass

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False
