from collections.abc import Mapping
from functools import singledispatch
from typing import Any

from lion_core.communication.message import RoledMessage
from lion_core.generic.pile import Pile
from lion_core.libs import to_dict, to_list
from lion_core.setting import LionUndefinedType


@singledispatch
def validate_message(messages: Any) -> list[RoledMessage] | RoledMessage:
    raise NotImplementedError(f"Invalid messages type: {type(messages)}")


@to_dict.register(LionUndefinedType)
@to_dict.register(type(None))
def _(messages):
    """Handle None or LionUndefined inputs."""
    return []


@validate_message.register(RoledMessage)
def _(messages, strict=False):
    """Handle RoledMessage inputs."""
    return [messages]


@validate_message.register(dict)
def _(messages, strict=False):
    """Handle dictionary inputs."""
    try:
        return [RoledMessage.from_dict(messages)]
    except Exception as e:
        if strict:
            raise ValueError(f"Error in creating message object: {e}")
        else:
            return []


@validate_message.register(str)
def _(messages, strict=False):
    """Handle string inputs."""
    e1 = None
    try:
        try:
            _d = to_dict(messages, str_type="json")
            return validate_message(_d)
        except ValueError as e:
            e1 = e
            _d = to_dict(messages, str_type="xml")
            return validate_message(_d)
    except ValueError as e:
        if strict:
            raise ValueError(f"Error in converting string to dict: {e1}, {e}")
        else:
            return []


@validate_message.register(Mapping)
def _(messages, strict=False):
    """Handle mapping inputs."""
    try:
        _d = to_dict(messages)
        return validate_message(_d)
    except Exception as e:
        if strict:
            raise e
        else:
            return []


@validate_message.register(list)
def _(messages, strict=False):
    try:
        return to_list([validate_message(d) for d in messages], faltten_=True)
    except Exception as e:
        if strict:
            raise e
        return []


@validate_message.register(Pile)
def _(messages: Pile, strict=False):
    if messages.is_empty():
        return []
    return validate_message(list(messages), strict=strict)
