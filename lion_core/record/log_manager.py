"""LogManager module for efficient log management in the Lion framework."""

from typing import Any, List, TypeVar

from lion_core.abc.observer import BaseManager
from lion_core.generic.note import Note
from lion_core.generic.pile import Pile, pile

from .log import BaseLog

T = TypeVar("T", bound=BaseLog)


class LogManager(BaseManager):

    def __init__(self, logs: Any = None, default_log_class: type[T] = BaseLog) -> None:
        self.logs: Pile[T] = pile(logs or {})
        self.default_log_class: type[T] = default_log_class

    def add_log(self, content: dict | Note, loginfo: Note | dict, **data: Any) -> None:
        data["content"] = content
        data["loginfo"] = loginfo
        log_entry = self.default_log_class(**data)
        self.logs.append(log_entry)

    def dump_log(self, *args, **kwargs):
        """
        kwargs for pile.dump function,
        """
        return self.logs.dump(*args, **kwargs)

    def load_log(self, data: List[dict], *args, **kwargs) -> None:
        """
        kwargs for pile.load function,
        pile function should include all the load method kwargs
        """
        self.logs = Pile.load(data, *args, **kwargs)


# File: lion_core/log/log_manager.py
