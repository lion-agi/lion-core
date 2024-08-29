import copy
import os
import random
from collections.abc import Sequence
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal, TypeVar

from lion_core.abc import Observable
from lion_core.exceptions import LionIDError
from lion_core.setting import (
    DEFAULT_LION_ID_CONFIG,
    DEFAULT_TIMEZONE,
    LionIDConfig,
)

T = TypeVar("T")


class SysUtil:
    """Utility class providing various system-related functionalities."""

    @staticmethod
    def time(
        *,
        tz: timezone = DEFAULT_TIMEZONE,
        type_: Literal["timestamp", "datetime", "iso", "custom"] = "timestamp",
        sep: str | None = "T",
        timespec: str | None = "auto",
        custom_format: str | None = None,
        custom_sep: str | None = None,
    ) -> float | str | datetime:
        """
        Get current time in various formats.

        Args:
            tz: Timezone for the time (default: utc).
            type_: Type of time to return (default: "timestamp").
                Options: "timestamp", "datetime", "iso", "custom".
            sep: Separator for ISO format (default: "T").
            timespec: Timespec for ISO format (default: "auto").
            custom_format: Custom strftime format string for
                type_="custom".
            custom_sep: Custom separator for type_="custom",
                replaces "-", ":", ".".

        Returns:
            Current time in the specified format.

        Raises:
            ValueError: If an invalid type_ is provided or if custom_format
                is not provided when type_="custom".
        """
        now = datetime.now(tz=tz)

        match type_:
            case "iso":
                return now.isoformat(sep=sep, timespec=timespec)

            case "timestamp":
                return now.timestamp()

            case "datetime":
                return now

            case "custom":
                if not custom_format:
                    raise ValueError(
                        "custom_format must be provided when type_='custom'"
                    )
                formatted_time = now.strftime(custom_format)
                if custom_sep is not None:
                    for old_sep in ("-", ":", "."):
                        formatted_time = formatted_time.replace(
                            old_sep, custom_sep
                        )
                return formatted_time

            case _:
                raise ValueError(
                    f"Invalid value <{type_}> for `type_`, must be"
                    " one of 'timestamp', 'datetime', 'iso', or 'custom'."
                )

    @staticmethod
    def copy(obj: T, /, *, deep: bool = True, num: int = 1) -> T | list[T]:
        """
        Create one or more copies of an object.

        Args:
            obj: The object to be copied.
            deep: If True, create a deep copy. Otherwise, create a shallow
                copy.
            num: The number of copies to create.

        Returns:
            A single copy if num is 1, otherwise a list of copies.

        Raises:
            ValueError: If num is less than 1.
        """
        if num < 1:
            raise ValueError("Number of copies must be at least 1")

        copy_func = copy.deepcopy if deep else copy.copy
        return (
            [copy_func(obj) for _ in range(num)] if num > 1 else copy_func(obj)
        )

    @staticmethod
    def id(
        n: int = DEFAULT_LION_ID_CONFIG.n,
        prefix: str | None = DEFAULT_LION_ID_CONFIG.prefix,
        postfix: str | None = DEFAULT_LION_ID_CONFIG.postfix,
        random_hyphen: bool = DEFAULT_LION_ID_CONFIG.random_hyphen,
        num_hyphens: int | None = DEFAULT_LION_ID_CONFIG.num_hyphens,
        hyphen_start_index: (
            int | None
        ) = DEFAULT_LION_ID_CONFIG.hyphen_start_index,
        hyphen_end_index: int | None = DEFAULT_LION_ID_CONFIG.hyphen_end_index,
    ) -> str:
        """
        Generate a unique identifier.

        Args:
            n: Length of the ID (excluding prefix and postfix).
            prefix: String to prepend to the ID.
            postfix: String to append to the ID.
            random_hyphen: If True, insert random hyphens into the ID.
            num_hyphens: Number of hyphens to insert if random_hyphen is True.
            hyphen_start_index: Start index for hyphen insertion.
            hyphen_end_index: End index for hyphen insertion.

        Returns:
            A unique identifier string.
        """
        _t = SysUtil.time(type_="iso").encode()
        _r = os.urandom(16)
        _id = sha256(_t + _r).hexdigest()[:n]

        if random_hyphen:
            _id = _insert_random_hyphens(
                s=_id,
                num_hyphens=num_hyphens,
                start_index=hyphen_start_index,
                end_index=hyphen_end_index,
            )

        if prefix:
            _id = f"{prefix}{_id}"
        if postfix:
            _id = f"{_id}{postfix}"

        return _id

    @staticmethod
    def get_id(
        item: Sequence[Observable] | Observable | str,
        /,
        *,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
    ) -> str:
        """
        Get the Lion ID of an item.

        Args:
            item: The item to get the ID from.
            config: Configuration dictionary for ID validation.

        Returns:
            The Lion ID of the item.

        Raises:
            LionIDError: If the item does not contain a valid Lion ID.
        """
        item_id = None
        if isinstance(item, Sequence) and len(item) == 1:
            item = item[0]

        if isinstance(item, Observable):
            item_id: str = item.ln_id
        else:
            item_id = item

        id_len = (
            (len(config.prefix) if config.prefix else 0)
            + config.n
            + config.num_hyphens
            + (len(config.postfix) if config.postfix else 0)
        )

        hyphen_check = (
            False
            if (config.num_hyphens and config.num_hyphens)
            != item_id.count("-")
            else True
        )
        hypen_start_check = (
            False
            if (
                config.hyphen_start_index
                and "-" in item_id[: config.hyphen_start_index]
            )
            else True
        )
        hypen_end_check = (
            False
            if (
                config.hyphen_end_index
                and "-" in item_id[config.hyphen_end_index :]  # noqa
            )
            else True
        )

        prefix_check = (
            False
            if (config.prefix and not item_id.startswith(config.prefix))
            else True
        )
        postfix_check = (
            False
            if (config.postfix and not item_id.endswith(config.postfix))
            else True
        )
        length_check = len(item_id) == id_len

        if all(
            (
                isinstance(item_id, str),
                hyphen_check,
                hypen_start_check,
                hypen_end_check,
                prefix_check,
                postfix_check,
                length_check,
            )
        ) or (len(item_id) == 32):
            return item_id
        raise LionIDError(
            f"The input object of type <{type(item).__name__}> does "
            "not contain or is not a valid Lion ID. Item must be an instance"
            " of `Observable` or a valid `ln_id`."
        )

    @staticmethod
    def is_id(
        item: Sequence[Observable] | Observable | str,
        /,
        *,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
    ) -> bool:
        """
        Check if an item is a valid Lion ID.

        Args:
            item: The item to check.
            config: Configuration dictionary for ID validation.

        Returns:
            True if the item is a valid Lion ID, False otherwise.
        """
        try:
            SysUtil.get_id(item, config=config)
            return True
        except LionIDError:
            return False


def _insert_random_hyphens(
    s: str,
    num_hyphens: int = 1,
    start_index: int | None = None,
    end_index: int | None = None,
) -> str:
    """Insert random hyphens into a string."""
    if len(s) < 2:
        return s

    prefix = s[:start_index] if start_index else ""
    postfix = s[end_index:] if end_index else ""
    modifiable_part = s[start_index:end_index] if start_index else s

    positions = random.sample(range(len(modifiable_part)), num_hyphens)
    positions.sort()

    for pos in reversed(positions):
        modifiable_part = modifiable_part[:pos] + "-" + modifiable_part[pos:]

    return prefix + modifiable_part + postfix


# File: lion_core/sys_util.py
