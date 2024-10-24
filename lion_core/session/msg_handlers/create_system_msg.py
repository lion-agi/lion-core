from typing import Any

from lion_core.communication.system import System

from .utils import DEFAULT_SYSTEM


def create_system_message(
    system: Any = None,
    sender: Any = None,
    recipient: Any = None,
    system_datetime: bool | str = None,
) -> System:
    """Create or update a System message.

    Args:
        system: Existing System or system content.
        sender: The sender of the system message.
        recipient: The recipient of the system message.
        system_datetime: System datetime information.
            ignored if system is a System instance.

    Returns:
        System: New or updated System instance.
    """
    system = system or DEFAULT_SYSTEM

    if isinstance(system, System):
        if sender:
            system.sender = sender
        if recipient:
            system.recipient = recipient
        return system

    return System(
        system=system,
        sender=sender,
        recipient=recipient,
        system_datetime=system_datetime,
    )
