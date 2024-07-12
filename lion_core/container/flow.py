from collections.abc import Mapping
from collections import deque
from typing import Tuple, Any

import contextlib
from pydantic import Field

from lion_core.abc.element import Element
from lion_core.exceptions import LionTypeError, ItemNotFoundError
from .base import Collective
from .progression import Progression, progression
from .pile import Pile, pile


class Flow(Element):
    """
    Represents a flow of categorical sequences.

    Attributes:
        sequences (Pile[Progression]): A collection of progression sequences.
        registry (dict[str, str]): A registry mapping sequence names to IDs.
        default_name (str): The default name for the flow.
    """

    sequences: Pile[Progression] = Field(
        default_factory=lambda: pile({}, Progression, use_obj=True)
    )
    registry: dict[str, str] = Field(default_factory=dict)
    default_name: str = "main"

    def __init__(self, sequences: Any = None, default_name: str | None = None):
        """
        Initializes a Flow instance.

        Args:
            sequences: Initial sequences to include in the flow.
            default_name: Default name for the flow.
        """
        super().__init__()
        self.sequences = self._validate_sequences(sequences)
        self.default_name = default_name or "main"

    def _validate_sequences(self, value: Any) -> Pile[Progression]:
        """
        Validates and initializes the sequences.

        Args:
            value: Sequences to validate and initialize.

        Returns:
            Pile[Progression]: A pile of progression sequences.
        """
        if not value:
            return pile({}, Progression, use_obj=True)
        if isinstance(value, dict):
            return pile(value, Progression, use_obj=True)
        if isinstance(value, list) and value and isinstance(value[0], Progression):
            return pile({i.ln_id: i for i in value}, Progression, use_obj=True)
        return pile({}, Progression, use_obj=True)

    def all_orders(self) -> list[list[str]]:
        """
        Retrieves all orders in the flow.

        Returns:
            list[list[str]]: A list of lists containing sequence orders.
        """
        return [list(seq) for seq in self.sequences]

    def all_unique_items(self) -> Tuple[str, ...]:
        """
        Retrieves all unique items across sequences.

        Returns:
            Tuple[str, ...]: A tuple of unique items.
        """
        return tuple({item for seq in self.sequences for item in seq})

    def keys(self):
        yield from self.sequences.keys()

    def values(self):
        yield from self.sequences.values()

    def items(self):
        yield from self.sequences.items()

    def get(self, seq: str | None = None, default: Any = ...) -> Progression | None:
        """
        Retrieves a sequence by name or returns the default sequence.

        Args:
            seq: The name of the sequence.
            default: Default value if sequence is not found.

        Returns:
            Progression: The requested sequence.

        Raises:
            ItemNotFoundError: If no sequence is found and no default is provided.
            LionTypeError: If the sequence is not of type Progression.
        """
        if seq is None:
            if self.default_name in self.registry:
                seq = self.registry[self.default_name]
                return self.sequences[seq]
            raise ItemNotFoundError("No sequence found.")

        if seq in self:
            if not isinstance(seq, (str, Progression)):
                raise LionTypeError("Sequence must be of type Progression.")

            if isinstance(seq, str):
                seq = self.registry[seq]

        return (
            self.sequences[seq] if default == ... else self.sequences.get(seq, default)
        )

    def __getitem__(self, seq: str | None = None) -> Progression:
        return self.get(seq)

    def __setitem__(self, seq: str, value: Any) -> None:
        if seq not in self:
            raise ItemNotFoundError(f"Sequence {seq}")

        self.sequences[seq] = value

    def __contains__(self, item: Any) -> bool:
        return (
            item in self.registry
            or item in self.sequences
            or item in self.all_unique_items()
        )

    def shape(self) -> dict[str, int]:
        return {key: len(self.sequences[value]) for key, value in self.registry.items()}

    def size(self) -> int:
        return sum(len(seq) for seq in self.all_orders())

    def clear(self) -> None:
        self.sequences.clear()
        self.registry.clear()

    def include(
        self, seq: Any = None, item: Any = None, name: str | None = None
    ) -> bool:
        _sequence = self._find_sequence(seq, None) or self._find_sequence(name, None)
        if not _sequence:
            if not item and not name:
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
                return True

            else:
                if isinstance(seq, Progression):
                    if item and seq.include(item):
                        self.register(seq, name)
                    return seq in self

                return False

    def exclude(
        self, seq: Any = None, item: Any = None, name: str | None = None
    ) -> bool:
        """
        Excludes an item or sequence from the flow.

        Args:
            seq: The sequence to exclude from.
            item: The item to exclude.
            name: The name of the sequence.

        Returns:
            bool: True if exclusion was successful, False otherwise.
        """
        if seq is not None:
            with contextlib.suppress(ItemNotFoundError, AttributeError):
                if item:
                    self.sequences[self.registry[seq]].exclude(item)
                    return item not in self.sequences[self.registry[seq]]
                else:
                    a = self.registry.pop(seq.name or seq.ln_id, None)
                    return a is not None and self.sequences.exclude(seq)
            return False

        elif name is not None:
            with contextlib.suppress(ItemNotFoundError):
                if item:
                    return self.sequences[self.registry[name]].exclude(item)
                else:
                    a = self.registry.pop(name, None)
                    return a is not None and self.sequences.exclude(a)
            return False

    def register(self, sequence: Progression, name: str | None = None) -> None:
        """
        Registers a sequence with a name.

        Args:
            sequence: The sequence to register.
            name: The name for the sequence.

        Raises:
            LionTypeError: If the sequence is not of type Progression.
            ValueError: If the sequence name already exists.
        """
        if not isinstance(sequence, Progression):
            raise LionTypeError("Sequence must be of type Progression.")

        name = name or sequence.name
        if not name:
            if self.default_name in self.registry:
                name = sequence.ln_id
            else:
                name = self.default_name

        if name in self.registry:
            raise ValueError(f"Sequence '{name}' already exists.")

        self.sequences.include(sequence)
        self.registry[name] = sequence.ln_id

    def append(self, item: Any, sequence: Any = None) -> None:
        """
        Appends an item to a sequence.

        Args:
            item: The item to append.
            sequence: The sequence to append to.
        """
        if not sequence:
            if self.default_name in self.registry:
                sequence = self.registry[self.default_name]
                self.sequences[sequence].include(item)
                return

            p = progression(item, self.default_name)
            self.register(p)
            return

        if sequence in self.sequences:
            self.sequences[sequence].include(item)
            return

        if sequence in self.registry:
            self.sequences[self.registry[sequence]].include(item)
            return

        p = progression(item, sequence if isinstance(sequence, str) else None)
        self.register(p)

    def popleft(self, sequence: Any = None) -> Any:
        """
        Removes and returns an item from the left end of a sequence.

        Args:
            sequence: The sequence to remove the item from.

        Returns:
            The removed item.
        """
        sequence = self._find_sequence(sequence)
        return self.sequences[sequence].popleft()

    def remove(self, item: Any, sequence: str = "all") -> None:
        """
        Removes an item from a sequence or all sequences.

        Args:
            item: The item to remove.
            sequence: The sequence to remove the item from. Defaults to "all".
        """
        if sequence == "all":
            for seq in self.sequences:
                seq.remove(item)
            return

        sequence = self._find_sequence(sequence)
        self.sequences[sequence].remove(item)

    def __len__(self) -> int:
        return len(self.sequences)

    def __iter__(self):
        return iter(self.sequences)

    def __next__(self):
        return next(iter(self))

    def _find_sequence(self, sequence: Any = None, default: Any = ...) -> str | None:
        """
        Finds the sequence ID in the registry or sequences.

        Args:
            sequence: The sequence to find.
            default: The default value if sequence is not found.

        Returns:
            The found sequence ID.

        Raises:
            ItemNotFoundError: If no sequence is found.
        """
        if not sequence:
            if self.default_name in self.registry:
                return self.registry[self.default_name]
            if default != ...:
                return default
            raise ItemNotFoundError("No sequence found.")

        if sequence in self.sequences:
            return sequence.ln_id if isinstance(sequence, Progression) else sequence

        if sequence in self.registry:
            return self.registry[sequence]

        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequences": self.sequences.to_dict(),
            "registry": self.registry,
            "default_name": self.default_name,
        }

    def to_df(self):
        return self.sequences.to_df()


def flow(sequences: Any = None, default_name: str | None = None) -> Flow:
    """
    Creates a new Flow instance.

    Args:
        sequences: Initial sequences to include in the flow.
        default_name: Default name for the flow.

    Returns:
        Flow: A new Flow instance.
    """
    if sequences is None:
        return Flow()

    flow = Flow()
    if default_name:
        flow.default_name = default_name

    if isinstance(sequences, (Mapping, Collective)):
        for name, seq in sequences.items():
            if not isinstance(seq, Progression):
                try:
                    seq = progression(seq, name)
                except Exception as e:
                    raise e
            if (a := name or seq.name) is not None:
                flow.register(seq, a)
            else:
                flow.register(seq, seq.ln_id)
        return flow

    for seq in sequences:
        if not isinstance(seq, Progression):
            try:
                seq = progression(seq)
            except Exception as e:
                raise e
        flow.register(seq)
    return flow


# File: lion_core/container/flow.py
