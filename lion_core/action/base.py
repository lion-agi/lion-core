from typing import Any
from pydantic import Field
from lion_core.abc import Action
from lion_core.generic.log import BaseLog
from lion_core.generic.element import Element
from lion_core.action.status import ActionStatus
from lion_core.log_manager import log_manager


class ObservableAction(Element, Action):

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
        """the request to get permission for, if any"""
        return {}

    async def to_log(self) -> BaseLog:
        try:
            log_ = self._to_log()
            await log_manager.alog(log_)
            return log_
        finally:
            del self

    def _to_log(self) -> BaseLog:
        dict_ = super().to_dict()
        content = {k: dict_[k] for k in self.content_fields if k in dict_}
        loginfo = {k: dict_[k] for k in dict_ if k not in self.content_fields}
        return BaseLog(content=content, loginfo=loginfo)
