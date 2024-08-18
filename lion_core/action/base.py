from typing import Any
from pydantic import Field
from lion_core.abc import Action
from lion_core.generic.element import Element
from lion_core.action.status import ActionStatus


class ObservableAction(Element, Action):

    status: ActionStatus = ActionStatus.PENDING
    execution_time: float = None
    response: Any = None
    error: str = None
    retry_config: dict = Field(default_factory=dict, exclude=True)

    def __init__(self, retry_config: dict = None):
        super().__init__()
        self.retry_config = retry_config or {}

    @property
    def request(self) -> dict:
        """the request to get permission for, if any"""
        return {}
