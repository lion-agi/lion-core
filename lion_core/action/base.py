from pydantic import Field
from lion_core.abc import Action
from lion_core.generic.element import Element
from lion_core.action.status import ActionStatus


class ObservableAction(Element, Action):
    """
    Represents an action that can be observed, with a trackable status.

    The `ObservableAction` class extends `Action` and `Element` to provide a
    structure for actions whose status can be monitored. It includes a status
    field to indicate the current state of the action, and a request property
    that can be used to check for permission before the action is performed.

    Attributes:
        status (ActionStatus): The current status of the action. Defaults to `ActionStatus.PENDING`.

    Properties:
        request (dict): A dictionary representing the request for permission to perform the action, if any.
    """

    status: ActionStatus = Field(default=ActionStatus.PENDING)

    @property
    def request(self) -> dict:
        """
        The request to get permission for, if any.

        This property returns a dictionary representing the request for
        permission before the action is performed. It can be overridden in
        subclasses to provide specific request details.

        Returns:
            dict: A dictionary containing the request details.
        """
        return {}
