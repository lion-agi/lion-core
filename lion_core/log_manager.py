import atexit
import json
from pathlib import Path
from typing import Any, TypeVar

from lionabc import BaseManager
from lionfuncs import create_path

from lion_core.generic.log import Log
from lion_core.generic.pile import Pile, pile

T = TypeVar("T", bound=Log)


class LogManager(BaseManager):
    """Manages logging operations and persistence."""

    def __init__(
        self,
        logs: Any = None,
        persist_dir: str | None = None,
        subfolder: str | None = None,
        file_prefix: str | None = None,
        capacity: int = 1000,
    ) -> None:
        """Initialize the LogManager.

        Args:
            logs: Initial logs to manage.
            persist_dir: Directory for log persistence.
            persist_path: Full path for log persistence.
            subfolder: Subfolder within persist_dir.
            file_prefix: Prefix for log files.
        """
        self.logs: Pile[T] = pile(logs or {}, item_type={Log})
        self.persist_dir = persist_dir
        self.file_prefix = file_prefix
        self.subfolder = subfolder
        self.capacity = capacity
        atexit.register(self.save_at_exit)

    async def alog(self, log_: Log, /) -> None:
        """Asynchronously add a log to the pile.

        Args:
            log_: The log to add.
        """
        await self.logs.ainclude(log_)
        if self.logs.size() >= self.capacity:
            await self.adump()

    async def adump(self, clear: bool = True) -> dict:
        """Asynchronously dump logs and save them.

        Args:
            clear: Whether to clear logs after dumping.
            persist_path: Path to save the dumped logs.

        Returns:
            The dumped log data.
        """
        async with self.logs.async_lock:
            data = self.logs.to_dict()
            self._save(data)
            if clear:
                self.logs.clear()
        return data

    def dump(self, clear: bool = True) -> dict:
        """Dump logs and save them.

        Args:
            clear: Whether to clear logs after dumping.

        Returns:
            The dumped log data.
        """
        data = self.logs.to_dict()
        if clear:
            self.logs.clear()
        self._save(data)
        return data

    def _save(self, data: dict) -> None:
        """Save log data to a file.

        Args:
            id_: Identifier for the log file.
            data: Log data to save.
            persist_path: Path to save the log file.
        """

        directory = self.persist_dir or "./data/logs"
        if (directory := str(directory)).endswith("/"):
            directory = directory[:-1]
        if self.subfolder:
            directory = f"{directory}/{self.subfolder}"

        fp = create_path(
            directory=directory,
            filename=self.file_prefix or "",
            extension=".json",
            timestamp=True,
            random_hash_digits=5,
        )
        json.dump(data, fp)

    def load(self, persist_path: str | Path) -> None:
        """Load logs from a JSON file.

        Args:
            persist_path: Path to load the log file from.

        Raises:
            FileNotFoundError: If the log file is not found.
        """
        try:
            with open(persist_path) as f:
                data = json.load(f)
            self.logs = Pile.from_dict(data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found at {persist_path}")

    def save_at_exit(self) -> None:
        """Save logs when exiting the program."""
        if self.logs:
            self.dump(clear=True)


# File: lion_core/log/log_manager.py
