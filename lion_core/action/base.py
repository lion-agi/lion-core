from typing import Any, NoReturn

from lionabc import Action, EventStatus
from lionabc.exceptions import LionAccessError
from lionfuncs import to_dict
from pydantic import PrivateAttr
from typing_extensions import override

from lion_core import event_log_manager
from lion_core.generic import Element, Log
from lion_core.log_manager import LogManager
from lion_core.setting import (
    DEFAULT_TIMED_FUNC_CALL_CONFIG,
    TimedFuncCallConfig,
)


class ObservableAction(Element, Action):

    status: EventStatus = EventStatus.PENDING
    execution_time: float | None = None
    execution_response: Any = None
    execution_error: str | None = None
    _timed_config: TimedFuncCallConfig | None = PrivateAttr(None)
    _content_fields: list = PrivateAttr(["execution_response"])
    _log: Log | None = PrivateAttr(None)

    @override
    def __init__(
        self, timed_config: dict | TimedFuncCallConfig | None, **kwargs: Any
    ) -> None:
        super().__init__()
        if timed_config is None:
            self._timed_config = DEFAULT_TIMED_FUNC_CALL_CONFIG

        else:
            if isinstance(timed_config, TimedFuncCallConfig):
                timed_config = timed_config.to_dict()
            if isinstance(timed_config, dict):
                timed_config = {**timed_config, **kwargs}
            timed_config = TimedFuncCallConfig(**timed_config)
            self._timed_config = timed_config

    @property
    def log_id(self) -> str:
        _l = self.to_log()
        return _l.ln_id

    async def alog(self, log_manager: LogManager = event_log_manager) -> str:
        """
        Log the action asynchronously.
        return log ln_id
        """
        _l = self.to_log()
        await log_manager.alog(_l)
        return _l.ln_id

    def to_log(self) -> Log:
        """
        Convert the action to a log entry.

        Returns:
            BaseLog: A log entry representing the action.
        """
        if self._log:
            return self._log

        dict_ = self.to_dict()
        content = {k: dict_[k] for k in self._content_fields if k in dict_}
        loginfo = {k: dict_[k] for k in dict_ if k not in self._content_fields}
        content = to_dict(
            content,
            use_model_dump=True,
            recursive=True,
            recursive_python_only=False,
            max_recursive_depth=5,
        )
        loginfo = to_dict(
            loginfo,
            use_model_dump=True,
            recursive=True,
            recursive_python_only=False,
            max_recursive_depth=5,
        )
        self._log = Log(content=content, loginfo=loginfo)
        return self._log

    @classmethod
    def from_dict(cls, data: dict, /, **kwargs: Any) -> NoReturn:
        """Event cannot be re-created."""
        raise LionAccessError(
            "An event cannot be recreated. Once it's done, it's done."
        )


__all__ = ["ObservableAction"]
# File: lion_core/action/base.py
