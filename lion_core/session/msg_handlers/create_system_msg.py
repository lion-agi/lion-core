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

    Returns:
        System: New or updated System instance.
    """
    config = {
        "sender": sender,
        "recipient": recipient,
        "system_datetime": system_datetime,
    }
    config = {k: v for k, v in config.items() if v}

    if not system:
        return System(DEFAULT_SYSTEM, **config)
    if isinstance(system, System):
        if config:
            for k, v in config.items():
                setattr(system, k, v)
        return system
    return System(system, **config)
