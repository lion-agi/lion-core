from pydantic import Field
from lion_core.abc import Action
from lion_core.generic.element import Element
from lion_core.action.status import ActionStatus


class ObservableAction(Element, Action):

    status: ActionStatus = Field(default=ActionStatus.PENDING)

    @property
    def request(self) -> dict:
        """the request to get permission for, if any"""
        return {}
