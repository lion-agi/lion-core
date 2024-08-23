from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing_extensions import override

from lion_core.abc import Container
from lion_core.libs import flatten, nfilter, nget, ninsert, nmerge, npop, nset, to_list
from lion_core.setting import LN_UNDEFINED
from lion_core.sys_utils import SysUtil

INDICE_TYPE = str | list[str | int]


class Note(BaseModel, Container):
    """A container for managing nested dictionary data structures."""

    content: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize a Note instance with the given keyword arguments."""
        super().__init__()
        self.content = kwargs

    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Initialize subclass and register update method."""
        super().__pydantic_init_subclass__(**kwargs)
        cls.update.register(cls, cls._update_with_note)

    @field_serializer("content")
    def _serialize_content(self, value: Any) -> dict[str, Any]:
        """Serialize the content, handling special cases for BaseMail objects."""
        from lion_core.communication.base_mail import BaseMail

        output_dict = SysUtil.copy(value, deep=True)
        origin_obj = output_dict.pop("clone_from", None)

        if origin_obj and isinstance(origin_obj, BaseMail):
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

    def pop(self, indices: INDICE_TYPE, default: Any = LN_UNDEFINED, /) -> Any:
        """Remove and return an item from the nested structure."""
        indices = to_list(indices, flatten=True, dropna=True)
        return npop(self.content, indices, default)

    def insert(self, indices: INDICE_TYPE, value: Any, /) -> None:
        """Insert a value into the nested structure at the specified indices."""
        indices = to_list(indices, flatten=True, dropna=True)
        ninsert(self.content, indices, value)

    def set(self, indices: INDICE_TYPE, value: Any, /) -> None:
        """Set a value in the nested structure at the specified indices."""
        indices = to_list(indices, flatten=True, dropna=True)

        if self.get(indices, None) is None:
            self.insert(indices, value)
        else:
            nset(self.content, indices, value)

    def get(self, indices: INDICE_TYPE, default: Any = LN_UNDEFINED, /) -> Any:
        """Get a value from the nested structure at the specified indices."""
        indices = to_list(indices, flatten=True, dropna=True)
        return nget(self.content, indices, default)

    def keys(self, /, flat: bool = False, **kwargs: Any) -> list:
        """
        Get the keys of the Note.

        Args:
            flat: If True, return flattened keys.
            kwargs: Additional keyword arguments for flattening
        """
        if flat:
            return flatten(self.content, **kwargs).keys()
        return list(self.content.keys())

    def values(self, /, flat: bool = False, **kwargs: Any):
        """
        Get the values of the Note.

        Args:
            flat: If True, return flattened values.
            kwargs: Additional keyword arguments for flattening
        """
        if flat:
            return flatten(self.content, **kwargs).values()
        return self.content.values()

    def items(self, /, flat: bool = False, **kwargs: Any):
        """
        Get the items of the Note.

        Args:
            flat: If True, return flattened items.
            kwargs: Additional keyword arguments for flattening
        """
        if flat:
            return flatten(self.content, **kwargs).items()
        return self.content.items()

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """
        Convert the Note to a dictionary.

        kwargs: Additional keyword arguments for BaseModel.model_dump

        Returns:
            A dictionary representation of the Note.
        """
        output_dict = self.model_dump(**kwargs)
        return output_dict["content"]

    def clear(self):
        """Clear the content of the Note."""
        self.content.clear()

    def update(
        self,
        indices: INDICE_TYPE,
        *args: list[Any],
        filter: Callable[[Any], bool] | None = None,
        overwrite: bool = True,
        dict_sequence: bool = True,
        sort_list: bool = False,
        custom_sort: Callable[[Any], Any] | None = None,
    ):
        """
        update the content of the Note with a number of dictionaries or Notes.
        optionally filter the values, overwrite existing keys, and sort lists.

        default behavior is to mimic the behavior of dict.update().
        which is to overwrite existing keys.
        Optionally, you can set overwrite to False, and by default, the subsequent
        duplicated keys will have a postfix of '_1', '_2', '_3', etc to preserve
        all data.
        """
        if not indices:
            args = [self.content, *args]
        else:
            args = [self.content.get(indices, {}), *args]

        args = [arg.content if isinstance(arg, self.__class__) else arg for arg in args]
        value = [nfilter(arg, filter) for arg in args] if filter else args
        value = nmerge(
            value,
            overwrite=overwrite,
            dict_sequence=dict_sequence,
            sort_list=sort_list,
            custom_sort=custom_sort,
        )
        if not indices:
            self.content = value
        else:
            self.set(indices, value)

    @classmethod
    def from_dict(cls, kwargs: Any) -> "Note":
        """Create a Note from a dictionary."""
        return cls(**kwargs)

    def __contains__(self, indices: INDICE_TYPE) -> bool:
        """Check if the Note contains the specified indices."""
        return self.content.get(indices, LN_UNDEFINED) is not LN_UNDEFINED

    def __len__(self) -> int:
        """Return the length of the Note's content."""
        return len(self.content)

    def __iter__(self):
        """Return an iterator over the Note's content."""
        return iter(self.content)

    def __next__(self):
        """Return the next item in the Note's content."""
        return next(iter(self.content))

    @override
    def __str__(self) -> str:
        """Return a string representation of the Note's content."""
        return str(self.content)

    @override
    def __repr__(self) -> str:
        """Return a detailed string representation of the Note's content."""
        return repr(self.content)

    def __getitem__(self, indices: INDICE_TYPE) -> Any:
        """Get an item from the Note using index notation."""
        indices = to_list(indices, flatten=True, dropna=True)
        return self.get(indices)

    def __setitem__(self, indices: INDICE_TYPE, value: Any) -> None:
        """Set an item in the Note using index notation."""
        self.set(indices, value)


def note(**kwargs: Any) -> Note:
    """Create a Note object from keyword arguments."""
    return Note(**kwargs)


__all__ = ["Note", "note"]

# File : lion_core/generic/note.py
