"""System message module for the Lion framework's communication system."""

import json
from typing import Any
from pydantic import Field
from lion_core.sys_util import SysUtil
from .message import RoledMessage, MessageRole


class System(RoledMessage):
    """Represents a system message in an LLM conversation."""

    system: str | Any | None = Field(None)

    def __init__(
        self,
        system: Any,
        sender: str | None,
        recipient: str | None,
        system_datetime: bool | str | None,
        **kwargs: Any,
    ):
        """
        Initializes the System message.

        Args:
            system: The system information.
            sender: The sender of the message.
            recipient: The recipient of the message.
            system_datetime: The system datetime. If True, set to current
                datetime. If str, set to the given datetime.
            system_datetime_strftime: The system datetime strftime format.
            **kwargs: Additional fields to be added to the message content,
                must be JSON serializable.
        """
        if not system:
            if "metadata" in kwargs and "system" in kwargs["metadata"]:
                system = kwargs["metadata"].pop("system")

        if system_datetime == True:
            system_datetime = SysUtil.time(datetime_=True, iso=True)

        super().__init__(
            role=MessageRole.SYSTEM,
            sender=sender or "system",
            content=(
                {"system_info": f"{system}. System Date: {system_datetime}"}
                if system_datetime
                else {"system_info": system}
            ),
            recipient=recipient or "N/A",
            system=system,
            **kwargs,
        )

    @property
    def system_info(self) -> Any:
        """system information stored in the message content."""
        return self.content.get("system_info", None)

    def clone(self, **kwargs: Any) -> "System":
        """Creates a copy of the current System object."""
        system = json.dumps(self.system_info)
        system_copy = System(system=json.loads(system), **kwargs)
        system_copy.metadata.set("origin_ln_id", self.ln_id)
        return system_copy


# File: lion_core/communication/system.py
