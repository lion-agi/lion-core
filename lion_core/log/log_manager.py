"""LogManager module for efficient log management in the Lion framework."""

from typing import Any, List, Iterator, TypeVar

from lion_core.abc import BaseManager
from lion_core.container.pile import Pile, pile
from lion_core.log.base import BaseLog, LogLevel
from lion_core.log.d_log import DataLog

T = TypeVar('T', bound=BaseLog)


class LogManager(BaseManager):
    """
    Manages log entries in the Lion framework.

    Provides a minimal interface for logging and accessing log entries,
    utilizing a Pile for efficient storage and operations.

    Attributes:
        default_log_class: The default class used for creating log entries.
    """

    def __init__(
        self,
        logs: List[T] | None = None,
        default_log_class: type[T] = DataLog,
    ) -> None:
        """
        Initialize the LogManager.

        Args:
            logs: Optional list of initial log entries.
            default_log_class: The default class for creating log entries.
        """
        super().__init__()
        self._logs: Pile[T] = pile(logs or [], item_type={BaseLog, DataLog})
        self.default_log_class: type[T] = default_log_class

    def log(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        **kwargs: Any,
    ) -> None:
        """
        Create a new log entry and add it to the logs Pile.

        Args:
            message: The main log message.
            level: The severity level of the log entry.
            **kwargs: Additional keyword arguments for the log entry.
        """
        log_entry = self.default_log_class.create(
            message=message, level=level, **kwargs
        )
        self._logs.append(log_entry)

    @property
    def pile(self) -> Pile[T]:
        """
        Provide a deep copy of the underlying Pile of logs.

        Returns:
            A deep copy of the Pile containing all log entries.
        """
        return self._logs.copy(deep=True)

    def __iter__(self) -> Iterator[T]:
        """
        Provide an iterator over the log entries.

        Yields:
            Each log entry in the Pile.
        """
        return iter(self._logs)

    def __len__(self) -> int:
        """Return the number of logs in the manager."""
        return len(self._logs)

# File: lion_core/log/log_manager.py