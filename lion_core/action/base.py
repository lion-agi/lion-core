from typing import Any

from pydantic import Field, PrivateAttr

from lion_core import event_log_manager
from lion_core.abc import Action, EventStatus
from lion_core.generic.element import Element
from lion_core.generic.log import Log
from lion_core.setting import RetryConfig


class ObservableAction(Element, Action):
    """
    Represents an action that can be observed, with a trackable status.

    The `ObservableAction` class extends `Action` and `Element` to provide a
    structure for actions whose status can be monitored. It includes a status
    field to indicate the current state of the action, and a request property
    that can be used to check for permission before the action is performed.

    Attributes:
        status (EventStatus): The current status of the action.
        execution_time (float): The time taken to execute the action.
        response (Any): The response from the action execution.
        error (str): Any error message associated with the action.
        retry_config (dict): Configuration for retry attempts.
        content_fields (list): Fields to include in the content of the log.
    """

    status: EventStatus = EventStatus.PENDING
    execution_time: float = None
    execution_response: Any = None
    execution_error: str = None
    retry_config: RetryConfig = Field(
        default_factory=RetryConfig, exclude=True
    )
    _content_fields: list = PrivateAttr(["execution_response"])

    def __init__(self, retry_config: RetryConfig = None):
        super().__init__()
        self.retry_config = retry_config or RetryConfig()

    async def alog(self) -> Log:
        """Log the action asynchronously."""
        await event_log_manager.alog(self.to_log())

    def to_log(self) -> Log:
        """
        Convert the action to a log entry.

        Returns:
            BaseLog: A log entry representing the action.
        """
        dict_ = self.to_dict()
        content = {k: dict_[k] for k in self._content_fields if k in dict_}
        loginfo = {k: dict_[k] for k in dict_ if k not in self._content_fields}
        return Log(content=content, loginfo=loginfo)


__all__ = ["ObservableAction"]
# File: lion_core/action/base.py
