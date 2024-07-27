from functools import singledispatchmethod, partial
from collections.abc import Mapping
from typing import Tuple, Any, override, Literal

import contextlib
from pydantic import Field

from lion_core.sys_utils import SysUtil
from lion_core.setting import LionUndefined, LN_UNDEFINED
from lion_core.abc import Collective, Container
from lion_core.generic import (
    Element,
    Note,
    Pile,
    pile,
    Progression,
    progression,
    to_list_type,
)
from lion_core.exceptions import (
    LionTypeError,
    ItemNotFoundError,
    ItemExistsError,
    LionValueError,
)
from lion_core.libs import is_same_dtype, to_list
from pydantic_core import PydanticUndefined

flow_pile = partial(pile, item_type=Progression, strict=True)


class Flow(Element, Container):

    sequences: Pile[Progression] = Field(default_factory=flow_pile)
    registry: Note = Field(default_factory=Note)
    default_name: str = "main"

    @override
    def __init__(self, sequences: Any = None, default_name: str | None = None):
        super().__init__()
        self.sequences = self._validate_sequences(sequences)
        self.default_name = default_name or "main"

    @singledispatchmethod
    def _validate_sequences(self, value: Any) -> Pile[Progression]:
        value = to_list_type(value)
        return self._validate_sequences(value)

    @_validate_sequences.register(list)
    def _(self, value: list[Progression]):
        if len(value) < 1:
            return flow_pile({})
        if not is_same_dtype(value, Progression):
            raise LionTypeError("Flow sequences must be of type Progression.")
        return flow_pile(value)

    @_validate_sequences.register(Mapping)
    @_validate_sequences.register(dict)
    def _(self, value: dict[str, Progression]):
        value = list(value.values())
        return self._validate_sequences(value)

    @_validate_sequences.register(Pile)
    def _validate_sequences(self, value: Any) -> Pile[Progression]:
        return self._validate_sequences(list(value))

    @_validate_sequences.register(Progression)
    def _(self, value: Progression):
        return self._validate_sequences([value])

    def __list__(self) -> list[Progression]:
        return [list(seq) for seq in self.sequences]

    def __contains__(self, item: Any) -> bool:
        return (
            item in self.registry or item in self.sequences or item in self.unique_items
        )

    @property
    def unique_items(self) -> list[Any]:
        return list({item for seq in self.sequences for item in seq})

    def get(self, seq=None, default=LN_UNDEFINED):
        if not seq:
            if self.default_name in self.registry:
                return self.sequences[self.registry[self.default_name]]
            if default not in [LN_UNDEFINED, PydanticUndefined]:
                return default
            raise ItemNotFoundError("No sequence found.")

        if seq in self:
            if not isinstance(seq, Progression):
                if isinstance(seq, str):
                    seq = self.registry[seq]
                else:
                    if default is not LN_UNDEFINED:
                        return default
                    raise LionTypeError("Sequence must be of type Progression.")

        return self.sequences.get(seq, default)

    def __getitem__(self, seq: str | None = None) -> Progression:
        return self.get(seq)

    def __setitem__(self, seq: str, value: Any) -> None:
        if not isinstance(value, Progression):
            raise LionTypeError("Sequence must be of type Progression.")
        if isinstance(seq, Progression):
            seq = seq.name or seq.ln_id
        self.sequences[seq] = value

    def shape(self) -> dict[str, int]:
        return {key: len(self.sequences[value]) for key, value in self.registry.items()}

    def size(self) -> int:
        return len(to_list(list(self), flatten=True, dropna=True))

    def clear(self) -> None:
        self.sequences.clear()
        self.registry.clear()

    def append(
        self,
        item: Any,
        seq: str | Progression = None,
    ):
        seq = self.get(seq)
        seq.append(item)

    def include(
        self,
        item: Any = None,  # if only item, we add it to default
        seq: (
            str | Progression | None
        ) = None,  # if both item and seq, we add item to seq
    ) -> bool:  # if not item, we include seq to flow
        if not seq and item:
            seq = self.get()
            seq.include(item)
            return True

        elif seq and item:
            seq = self.get(seq)
            seq.include(item)
            return True

        elif seq and not item:
            if isinstance(seq, Progression):
                if seq.name and seq.name not in self.registry:
                    self.registry[seq.name] = seq.ln_id
                else:
                    self.registry[seq.ln_id] = seq.ln_id
            elif isinstance(seq, str):
                seq = self.get(seq, None)
                if seq:
                    seq.include(item)
                    return True
        return False

    def exclude(
        self,
        item: Any | None = None,
        seq: str | Progression | None = None,
        how: Literal["all"] | None = None,  # "all" will exclude item from all sequences
    ) -> bool:

        # this is not allowed
        if not item and not seq:
            return False

        if item:
            if not how == "all":
                seq = self.get(seq)
                seq.exclude(item)
                return True
            for _sq in self.sequences:
                _sq.exclude(item)
            return True

        seq = self.get(seq)
        self.sequences.exclude(seq)
        self.registry.pop(seq.name or seq.ln_id)
        return True

    def popleft(self, seq) -> Any:
        seq = self.get(seq)
        return seq.popleft()

    def remove(
        self,
        item: Any,
        seq: str | Progression,
    ):

        seq = self.get(seq)
        seq.remove(item)

    def __len__(self) -> int:
        return len(self.sequences)

    def __iter__(self):
        return iter(self.sequences)

    def __next__(self):
        return next(iter(self))


def flow(sequences: Any = None, default_name: str | None = "main") -> Flow:
    if sequences is None:
        return Flow(default_name=default_name)

    flow = Flow()
    flow.default_name = default_name
    flow.sequences = flow.sequences._validate_pile(sequences)
    for seq in flow.sequences:
        if seq.name and seq.name not in flow.registry:
            flow.registry[seq.name] = seq.ln_id
        else:
            flow.registry[seq.name or seq.ln_id] = seq.ln_id

    return flow


# File: lion_core/container/flow.py
