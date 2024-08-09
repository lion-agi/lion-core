"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from collections.abc import Mapping
from collections import deque
from typing import Tuple
from pydantic import Field
from pydantic_core import PydanticUndefined
from lion_core.setting import LN_UNDEFINED

import contextlib

from lion_core.exceptions import ItemNotFoundError, LionTypeError, LionValueError
from lion_core.generic.element import Element
from lion_core.abc import Collective


from lion_core.generic.pile import Pile, pile
from lion_core.generic.progression import Progression, prog


class Flow(Element):

    progressions: Pile[Progression] = Field(
        default_factory=lambda: pile({}, Progression)
    )

    registry: dict = Field(default_factory=dict)
    default_name: str = Field(None)

    def __init__(self, progressions=None, default_name=None):
        """
        Initializes a Flow instance.

        Args:
            sequences (optional): Initial sequences to include in the flow.
            default_name (optional): Default name for the flow.
        """
        super().__init__()
        self.progressions = self._validate_progressions(progressions)

        if default_name:
            self.default_name = default_name

        # if mapping we assume a dictionary of in {name: data} format
        if isinstance(progressions, (Mapping, Collective)):
            for name, prog_ in progressions.items():
                if not isinstance(prog_, Progression):
                    try:
                        prog_ = prog(prog_, name)
                    except Exception as e:
                        raise e
                if (a := name or prog_.name) is not None:
                    self.register(prog_, a)
                else:
                    self.register(prog_, prog_.ln_id)
            return

        for prog_ in progressions:
            if not isinstance(prog_, Progression):
                try:
                    prog_ = prog(prog_)
                except Exception as e:
                    raise e
            self.register(prog_)

    def _validate_progressions(self, value):
        try:
            if isinstance(value, Collective):
                value = list(value)
            return pile(value, {Progression})
        except Exception as e:
            raise LionValueError(f"Invalid progressions: {e}")

    def all_orders(self) -> list[list[str]]:
        return [list(seq) for seq in self.progressions]

    def unique(self) -> Tuple[str]:
        return list({item for seq in self.progressions for item in seq})

    def keys(self):
        yield from self.progressions.keys()

    def values(self):
        yield from self.progressions.values()

    def items(self):
        yield from self.progressions.items()

    def __getitem__(self, prog_=None, default=LN_UNDEFINED):
        return self.get(prog_, default)

    def __setitem__(self, prog_, index=None, value=None, /):
        if prog_ not in self:
            raise ItemNotFoundError(f"Sequence {prog_}")

        if index:
            self.progressions[prog_][index] = value
            return

        self.progressions[prog_] = value

    def __contains__(self, item):
        return (
            item in self.registry or item in self.progressions or item in self.unique()
        )

    def shape(self):
        return (len(self.all_orders()), [len(i) for i in self.all_orders()])

    def size(self):
        return sum(len(seq) for seq in self.all_orders())

    def clear(self):
        self.progressions.clear()
        self.registry.clear()

    def include(self, prog_=None, item=None, name=None):
        _sequence = self._find_prog(prog_, None) or self._find_prog(name, None)
        if not _sequence:
            if not item and not name:
                """None is not in the registry or sequencees."""
                return False
            if item:
                self.append(item, name)
                return item in self

        else:
            if _sequence in self:
                if not item and not name:
                    return True
                if item:
                    self.append(item, _sequence)
                    return item in self
                return True  # will ignore name if sequence is already found

            else:
                if isinstance(prog_, Progression):
                    if item and prog_.include(item):
                        self.register(prog_, name)
                    return prog_ in self

                return False

    def exclude(self, seq=None, item=None, name=None):
        # if sequence is not None, we will not check the name
        if seq is not None:

            with contextlib.suppress(ItemNotFoundError, AttributeError):
                if item:
                    # if there is item, we exclude it from the sequence
                    self.progressions[self.registry[seq]].exclude(item)
                    return item not in self.progressions[self.registry[seq]]
                else:
                    # if there is no item, we exclude the sequence
                    a = self.registry.pop(seq.name or seq.ln_id, None)
                    return a is not None and self.progressions.exclude(seq)
            return False

        elif name is not None:

            with contextlib.suppress(ItemNotFoundError):
                if item:
                    # if there is item, we exclude it from the sequence
                    return self.progressions[self.registry[name]].exclude(item)
                else:
                    # if there is no item, we exclude the sequence
                    a = self.registry.pop(name, None)
                    return a is not None and self.progressions.exclude(a)
            return False

    def register(self, prog_: Progression, name: str = None):
        if not isinstance(prog_, Progression):
            raise LionTypeError(f"Sequence must be of type Progression.")

        name = name or prog_.name
        if not name:
            if self.default_name in self.registry:
                name = prog_.ln_id
            else:
                name = self.default_name

        if name in self.registry:
            raise ValueError(f"Sequence '{name}' already exists.")

        self.progressions.include(prog_)
        self.registry[name] = prog_.ln_id

    def append(self, item, prog_=None, /):
        if not prog_:
            if self.default_name in self.registry:
                prog_ = self.registry[self.default_name]
                self.progressions[prog_].include(item)
                return

            p = prog(item, self.default_name)
            self.register(p)
            return

        if prog_ in self.progressions:
            self.progressions[prog_].include(item)
            return

        if prog_ in self.registry:
            self.progressions[self.registry[prog_]].include(item)
            return

        p = prog(item, prog_ if isinstance(prog_, str) else None)
        self.register(p)

    def popleft(self, prog_=None, /):
        prog_ = self._find_prog(prog_)
        return self.progressions[prog_].popleft()

    def shape(self):
        return {
            key: len(self.progressions[value]) for key, value in self.registry.items()
        }

    def get(self, prog_=None, default=LN_UNDEFINED) -> deque[str] | None:
        prog_ = getattr(prog_, "ln_id", None) or prog_

        if prog_ is None:
            if self.default_name in self.registry:
                return self.progressions[self.registry[self.default_name]]
            if default in [LN_UNDEFINED, PydanticUndefined]:
                raise ItemNotFoundError("No progression found.")

        if prog_ in self.registry:
            return self.progressions[self.registry[prog_]]

        try:
            return self.progressions[prog_]
        except KeyError as e:
            if default in [LN_UNDEFINED, PydanticUndefined]:
                raise e
            return default

    def remove(self, item, prog_="all"):
        if prog_ == "all":
            for seq in self.progressions:
                seq.remove(item)
            return

        prog_ = self._find_prog(prog_)
        self.progressions[prog_].remove(item)

    def __len__(self):
        return len(self.progressions)

    def __iter__(self):
        return iter(self.progressions)

    def __next__(self):
        return next(self.__iter__())

    def _find_prog(self, prog_=None, default=LN_UNDEFINED):

        if not prog_:
            if self.default_name in self.registry:
                return self.registry[self.default_name]
            if default not in [LN_UNDEFINED, PydanticUndefined]:
                return default
            raise ItemNotFoundError("No progression found.")

        if prog_ in self.progressions:
            return prog_.ln_id if isinstance(prog_, Progression) else prog_

        if prog_ in self.registry:
            return self.registry[prog_]

    def to_dict(self):
        return {
            "progressions": self.progressions.to_dict(),
            "default_name": self.default_name,
        }

    @classmethod
    def from_dict(cls, data):
        progressions = Pile.from_dict(data["progressions"])
        return cls(progressions, data["default_name"])


def flow(progressions=None, default_name=None):
    return Flow(progressions, default_name)
