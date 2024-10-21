from typing import Any

from lion_core.communication.system import System


def create_system_message(
    system: Any = None,
    sender: Any = None,
    recipient: Any = None,
    system_datetime: bool | str = None,
) -> System:
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


DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."
