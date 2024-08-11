from pydantic import ConfigDict

from lion_core.abc import Relational
from lion_core.generic.component import Component


class Node(Component, Relational):

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )


__all__ = ["Node"]
