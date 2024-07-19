"""System utility module for the Lion framework.

This module provides utility functions for time operations, object copying,
and unique identifier generation used throughout the Lion framework.
"""

from __future__ import annotations
from collections.abc import Sequence
from typing import Any, Literal, TypeVar
import os
import copy
from functools import lru_cache
from hashlib import sha256
from datetime import datetime, timezone

from .setting import TIME_CONFIG, LION_ID_CONFIG
from .exceptions import LionIDError

T = TypeVar("T")


class SysUtil:
    """Utility class providing various system-related functionalities."""

    @staticmethod
    def time(
        tz: timezone = TIME_CONFIG["tz"],
        type_: Literal["timestamp", "datetime", "iso", "custom"] = "timestamp",
        iso: bool = False,
        sep: str | None = "T",
        timespec: str | None = "auto",
        custom_format: str | None = None,
        custom_sep: str | None = None,
    ) -> float | str | datetime:
        """
        Get current time in various formats.

        Args:
            tz: Timezone for the time (default: TIME_CONFIG["tz"]).
            type_: Type of time to return (default: "timestamp").
                Options: "timestamp", "datetime", "iso", "custom".
            iso: If True, returns ISO format string (deprecated, use type_="iso").
            sep: Separator for ISO format (default: "T").
            timespec: Timespec for ISO format (default: "auto").
            custom_format: Custom strftime format string for type_="custom".
            custom_sep: Custom separator for type_="custom", replaces "-", ":", ".".

        Returns:
            Current time in the specified format.

        Raises:
            ValueError: If an invalid type_ is provided or if custom_format
                is not provided when type_="custom".
        """
        now = datetime.now(tz=tz)

        if type_ == "timestamp":
            return now.timestamp()

        if type_ == "datetime":
            return now

        if type_ == "iso" or iso:
            return now.isoformat(sep=sep, timespec=timespec)

        if type_ == "custom":
            if not custom_format:
                raise ValueError("custom_format must be provided when type_='custom'")
            formatted_time = now.strftime(custom_format)
            if custom_sep is not None:
                for old_sep in ("-", ":", "."):
                    formatted_time = formatted_time.replace(old_sep, custom_sep)
            return formatted_time

        raise ValueError(
            f"Invalid type_: {type_}. "
            "Must be 'timestamp', 'datetime', 'iso', or 'custom'."
        )

    @staticmethod
    def copy(obj: T, deep: bool = True, num: int = 1) -> T | list[T]:
        """
        Create one or more copies of an object.

        Args:
            obj: The object to be copied.
            deep: If True, create a deep copy. Otherwise, create a shallow copy.
            num: The number of copies to create.

        Returns:
            A single copy if num is 1, otherwise a list of copies.

        Raises:
            ValueError: If num is less than 1.
        """
        if num < 1:
            raise ValueError("Number of copies must be at least 1")

        copy_func = copy.deepcopy if deep else copy.copy
        return [copy_func(obj) for _ in range(num)] if num > 1 else copy_func(obj)

    @staticmethod
    def id(
        n: int = LION_ID_CONFIG["n"],
        prefix: str | None = LION_ID_CONFIG["prefix"],
        postfix: str | None = None,
        random_hyphen: bool = LION_ID_CONFIG["random_hyphen"],
        num_hyphens: int | None = LION_ID_CONFIG["num_hyphens"],
        hyphen_start_index: int | None = LION_ID_CONFIG["hyphen_start_index"],
        hyphen_end_index: int | None = LION_ID_CONFIG["hyphen_end_index"],
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
        _t = SysUtil.time(type_="datetime", iso=True).encode()
        _r = os.urandom(16)
        _id = sha256(_t + _r).hexdigest()[:n]

        if random_hyphen:
            _id = SysUtil._insert_random_hyphens(
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
    @lru_cache
    def get_id(item: Any, /, *, config: dict = LION_ID_CONFIG) -> str:
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
        if isinstance(item, Sequence) and len(item) == 1:
            item = item[0]

        prefix = config["prefix"]
        n = int(config["n"])
        n_hyphens = int(config["num_hyphens"])

        if isinstance(item, str) and (
            (item.startswith(prefix) and len(item) == (len(prefix) + n + n_hyphens))
            or (len(item) == 32)  # for backward compatibility
        ):
            return item

        if hasattr(item, "ln_id"):
            return item.ln_id

        raise LionIDError("Item must contain a Lion ID.")

    @staticmethod
    @lru_cache
    def is_id(item: Any, /, *, config: dict = LION_ID_CONFIG) -> bool:
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


# File: lion_core/sys_util.py
