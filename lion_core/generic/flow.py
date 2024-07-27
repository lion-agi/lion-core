from functools import partial
from typing import Any, override, Literal

from pydantic import Field

from lion_core.setting import LN_UNDEFINED
from lion_core.abc import Container
from lion_core.generic import (
    Component,
    Note,
    Pile,
    pile,
    Progression,
)
from lion_core.sys_utils import SysUtil
from lion_core.exceptions import LionTypeError, ItemNotFoundError, LionValueError
from lion_core.libs import to_list
from pydantic_core import PydanticUndefined

flow_pile = partial(pile, item_type=Progression, strict=True)


class Flow(Component, Container):

    progressions: Pile[Progression] = Field(default_factory=flow_pile)
    registry: Note = Field(default_factory=Note)
    default_name: str = Field("main")

    @override
    def __init__(self, progressions: Any = None, default_name: str | None = None):
        super().__init__()
        self.progressions = self._validate_sequences(progressions)
        self.default_name = default_name or "main"

    def _validate_sequences(self, value: Any) -> Pile[Progression]:
        try:
            return flow_pile(value)
        except Exception as e:
            raise LionTypeError(f"Invalid sequences value. Error:{e}")

    def __list__(self) -> list[Progression]:
        return list(self.progressions)

    def __contains__(self, other):
        return SysUtil.get_id(other) in self.registry.values()

    @property
    def unique_items(self) -> list[Any]:
        return list({item for prog in self.progressions for item in prog})

    def get(self, prog=None, default=LN_UNDEFINED):
        if not prog:
            if self.default_name in self.registry:
                return self.progressions[self.registry[self.default_name]]
            if default not in [LN_UNDEFINED, PydanticUndefined]:
                return default
            raise ItemNotFoundError("No sequence found.")

        if prog in self:
            if not isinstance(prog, Progression):
                if isinstance(prog, str):
                    prog = self.registry[prog]
                else:
                    if default not in [LN_UNDEFINED, PydanticUndefined]:
                        return default
                    raise LionTypeError(
                        "progressions member must be of type or subclass of Progression."
                    )

        return self.progressions.get(prog, default)

    def __getitem__(self, prog: str | None = None) -> Progression:
        return self.get(prog)

    def __setitem__(self, prog: str, value: Any) -> None:
        try:
            self.progressions[prog] = value
            for i in self.progressions[value]:
                self.registry[i.name or i.ln_id] = i.ln_id
        except Exception as e:
            raise LionValueError from e

    def size(self) -> int:
        return len(
            to_list(
                [list(prog) for prog in self.progressions], flatten=True, dropna=True
            )
        )

    def clear(self) -> None:
        self.progressions.clear()
        self.registry.clear()

    def append(
        self,
        item: Any,
        prog: str | Progression = None,
    ) -> None:
        self[prog].append(item)

    def include(
        self,
        item: Any = None,  # if only item, we add it to default
        prog: (
            str | Progression | None
        ) = None,  # if both item and seq, we add item to seq
    ) -> bool:  # if not item, we include seq to flow
        if item:
            self.get().include(item)
            return

        elif prog and not item:
            if isinstance(prog, Progression):
                if prog.name and prog.name not in self.registry:
                    self.registry[prog.name] = prog.ln_id
                else:
                    self.registry[prog.ln_id] = prog.ln_id
            elif isinstance(prog, str):
                prog = self.get(prog, None)
                if prog:
                    prog.include(item)

    def exclude(
        self,
        item: Any | None = None,
        prog: str | Progression | None = None,
        how: Literal["all"] | None = None,  # "all" will exclude item from all sequences
    ):

        if item:
            if not how == "all":
                self[prog].exclude(item)
                return
            for _p in self.progressions:
                _p.exclude(item)
            return

        self.progressions.exclude(prog)
        self.registry.pop(prog.name or prog.ln_id)

    def popleft(self, prog) -> Any:
        return self[prog].popleft()

    def remove(
        self,
        item: Any,
        prog: str | Progression,
    ):
        return self[prog].remove(item)

    def __len__(self) -> int:
        return len(self.progressions)

    def __iter__(self):
        return iter(self.progressions)

    def __next__(self):
        return next(iter(self))

    def keys(self):
        return self.registry.keys()

    def values(self):
        return self.progressions.values()

    def items(self):
        return ((k, self[v]) for k, v in self.registry.items())


def flow(progressions: Any = None, default_name: str | None = "main") -> Flow:
    return Flow(progressions, default_name)


# File: lion_core/container/flow.py
