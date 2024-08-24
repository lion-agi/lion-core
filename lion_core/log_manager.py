import atexit
import json
import os
from typing import Any, TypeVar

from lion_core.abc._observer import BaseManager
from lion_core.generic.log import BaseLog
from lion_core.generic.pile import Pile, pile

T = TypeVar("T", bound=BaseLog)


class LogManager(BaseManager):
    def __init__(
        self,
        logs: Any = None,
        persist_dir: str = None,
        persist_path: str = None,
        subfolder=None,
        file_prefix: str = None,
    ):
        self.logs: Pile[T] = pile(logs or {}, {BaseLog})
        self.persist_dir = persist_dir
        self.persist_path = persist_path
        self.file_prefix = file_prefix
        self.subfolder = subfolder
        atexit.register(self.save_at_exit)

    async def alog(self, log_):
        await self.logs.ainclude(log_)

    async def adump(self, clear=True, persist_path=None) -> dict:
        async with self.logs.async_lock:
            id_ = self.logs[-1].ln_id[:-6]
            data = self.logs.dump(clear)
            self._save(id_, data, persist_path)

    def dump(self, clear=True, persist_path=None) -> dict:
        id_ = self.logs[-1].ln_id[:-6]
        data = self.logs.dump(clear)
        self._save(id_, data, persist_path)

    def _save(self, id_, data, persist_path=None):
        persist_path = persist_path or self.persist_path

        if not persist_path:
            persist_dir = self.persist_dir or "./data/logs"
            if self.subfolder:
                persist_dir = f"{persist_dir}/{self.subfolder}"
            persist_path = f"{persist_dir}/{self.file_prefix or ''}{id_}.json"

        if not os.path.exists(os.path.dirname(persist_path)):
            os.makedirs(os.path.dirname(persist_path))

        with open(persist_path, "w") as f:
            json.dump(data, f)

    def load_json(self, persist_path=None):
        persist_path = persist_path or self.persist_path
        try:
            data = None
            with open(persist_path) as f:
                data = json.load(f)
            self.logs = Pile.load(data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found at {persist_path}")

    def save_at_exit(self):
        if self.logs:
            self.dump(clear=True)


# File: lion_core/log/log_manager.py
