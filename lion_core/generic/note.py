from typing import Any

from lionabc import Communicatable, Container
from lionfuncs import Note as _Note
from lionfuncs import copy
from pydantic import field_serializer

INDICE_TYPE = str | list[str | int]


class Note(_Note, Container):
    """A container for managing nested dictionary data structures."""

    @field_serializer("content")
    def _serialize_content(self, value: Any) -> dict[str, Any]:
        """Serialize the content"""

        output_dict = copy(value, deep=True)
        origin_obj = output_dict.pop("clone_from", None)

        if origin_obj and isinstance(origin_obj, Communicatable):
            info_dict = {
                "clone_from_info": {
                    "original_ln_id": origin_obj.ln_id,
                    "original_timestamp": origin_obj.timestamp,
                    "original_sender": origin_obj.sender,
                    "original_recipient": origin_obj.recipient,
                }
            }
            output_dict.update(info_dict)
        return output_dict


def note(**kwargs: Any) -> Note:
    """Create a Note object from keyword arguments."""
    return Note(**kwargs)


__all__ = ["Note", "note"]

# File : lion_core/generic/note.py
