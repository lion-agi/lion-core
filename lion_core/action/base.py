from typing import Any

from pydantic import Field

from lion_core import event_log_manager
from lion_core.abc import Action
from lion_core.action.status import ActionStatus
from lion_core.exceptions import LionAccessError
from lion_core.generic.element import Element
from lion_core.generic.log import BaseLog


class ObservableAction(Element, Action):
    """
    Represents an action that can be observed, with a trackable status.

    The `ObservableAction` class extends `Action` and `Element` to provide a
    structure for actions whose status can be monitored. It includes a status
    field to indicate the current state of the action, and a request property
    that can be used to check for permission before the action is performed.

    Attributes:
        status (ActionStatus): The current status of the action.
        execution_time (float): The time taken to execute the action.
        response (Any): The response from the action execution.
        error (str): Any error message associated with the action.
        retry_config (dict): Configuration for retry attempts.
        content_fields (list): Fields to include in the content of the log.
    """

    status: ActionStatus = ActionStatus.PENDING
    execution_time: float = None
    response: Any = None
    error: str = None
    retry_config: dict = Field(default_factory=dict, exclude=True)
    content_fields: list = ["response"]

    def __init__(self, retry_config: dict = None):
        super().__init__()
        self.retry_config = retry_config or {}

    @property
    def request(self) -> dict:
        """
        The request to get permission for, if any.

        Returns:
            dict: A dictionary containing the request details.
        """
        return {}

    async def alog(self) -> BaseLog:
        """Log the action asynchronously."""
        await event_log_manager.alog(self.to_log())

    def to_log(self) -> BaseLog:
        """
        Convert the action to a log entry.

        Returns:
            BaseLog: A log entry representing the action.
        """
        dict_ = self.to_dict()
        content = {k: dict_[k] for k in self.content_fields if k in dict_}
        loginfo = {k: dict_[k] for k in dict_ if k not in self.content_fields}
        return BaseLog(content=content, loginfo=loginfo)

    @classmethod
    def from_dict(cls, data: Any):
        """
        Class method to create an instance from a dictionary.

        Args:
            data: The dictionary data to create an instance from.

        Raises:
            LionAccessError: Always raised as actions cannot be recreated.
        """
        raise LionAccessError(
            "An action cannot be recreated. Once it's done, it's done."
        )


__all__ = ["ObservableAction"]
# File: lion_core/action/base.py
