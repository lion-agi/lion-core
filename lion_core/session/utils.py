from collections.abc import Mapping, Sequence
from functools import singledispatch, partial
from typing import Any, Union

from lion_core.setting import LionUndefined, LN_UNDEFINED
from lion_core.libs import to_dict, to_list
from lion_core.generic.pile import Pile, pile
from lion_core.communication.message import RoledMessage
from lion_core.communication.system import System

"""
messages:
1. a single message object, or a single dict that can be converted to a message object
2. a sequence of message objects, or a sequence of dicts that can be converted to message objects
3. a pile of message objects
"""

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


@singledispatch
def validate_messages(messages: Any) -> list[RoledMessage] | RoledMessage:
    raise NotImplementedError(f"Invalid messages type: {type(messages)}")


@to_dict.register(LionUndefined)
@to_dict.register(type(None))
def _(messages):
    return []


@validate_messages.register(RoledMessage)
def _(messages):
    return messages


@validate_messages.register(dict)
def _(messages):
    try:
        return RoledMessage.from_dict(messages)
    except Exception as e:
        raise ValueError(f"Error in creating message object: {e}")


@validate_messages.register(str)
def _(messages):
    e1 = None
    try:
        try:
            _d = to_dict(messages, str_type="json")
            return validate_messages(_d)
        except ValueError as e:
            e1 = e
            _d = to_dict(messages, str_type="xml")
            return validate_messages(_d)
    except ValueError as e:
        raise ValueError(f"Error in converting string to dict: {e1}, {e}")


@validate_messages.register(Mapping)
def _(messages):
    try:
        _d = to_dict(messages)
        return validate_messages(_d)
    except Exception as e:
        raise e


@validate_messages.register(Sequence)
def _(messages):
    try:
        _lst_d = to_dict(messages)
        if not isinstance(_lst_d, list):
            messages = [messages]
        return to_list([validate_messages(d) for d in _lst_d if d], faltten_=True)
    except Exception as e:
        raise e


@validate_messages.register(Pile)
def _(messages):
    if messages.is_empty():
        return []
    return to_list(
        [validate_messages(d) for d in messages.values() if d], flatten_=True
    )


def validate_system(
    system: Any = None, sender=None, recipient=None, system_datetime=None, **kwargs
) -> None:

    config = {
        "sender": sender,
        "recipient": recipient,
        "system_datetime": system_datetime,
        **kwargs,
    }

    config = {k: v for k, v in config.items() if v not in [None, LN_UNDEFINED]}

    if not system:
        return System(DEFAULT_SYSTEM, **config)
    if isinstance(system, System):
        if config:
            for k, v in config.items():
                setattr(system, k, v)
        return system
    return System(system, **config)
