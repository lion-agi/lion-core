import atexit
import json
from typing import Any, TypeVar

from lion_core.abc._observer import BaseManager
from lion_core.generic.pile import Pile, pile

from lion_core.generic.log import BaseLog

T = TypeVar("T", bound=BaseLog)


class LogManager(BaseManager):

    def __init__(self, logs: Any = None, persist_path: str = None):
        self.logs: Pile[T] = pile(logs or {}, {BaseLog})
        self.persist_path = persist_path
        atexit.register(self.save_at_exit)

    async def alog(self, log_):
        await self.logs.ainclude(log_)

    async def adump(self, clear=True, persist_path=None) -> dict:
        async with self.logs.async_lock:
            id_ = self.logs[-1].ln_id[:-6]
            data = await self.logs.dump(clear)
            self._save(id_, data, persist_path)

    def dump(self, clear=True, persist_path=None) -> dict:
        with self.logs.lock:
            id_ = self.logs[-1].ln_id[:-6]
            data = self.logs.dump(clear)
            self._save(id_, data, persist_path)

    def _save(self, id_, data, persist_path=None):
        persist_path = persist_path or self.persist_path

        if not persist_path:
            persist_path = f"/data/logs/{id_}.json"

        with open(self.persist_dir, "w") as f:
            json.dump(data, f)

    def load_json(self, persist_path=None):
        persist_path = persist_path or self.persist_path
        try:
            data = None
            with open(persist_path, "r") as f:
                data = json.load(f)
            self.logs = Pile.load(data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found at {persist_path}")

    def save_at_exit(self):
        if self.logs:
            self.dump(clear=True)


log_manager = LogManager()

# File: lion_core/log/log_manager.py
