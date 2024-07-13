"""System utility module for the Lion framework."""

from __future__ import annotations
from collections.abc import Sequence
from typing import Any, Type
from pathlib import Path
import os
import copy
import sys
import subprocess
import importlib
import importlib.metadata
import platform
import re
import random
from functools import lru_cache
from hashlib import sha256
from datetime import datetime, timezone
import logging

from ..settings._setting import TIME_CONFIG
from .._abc import AbstractElement
from ..exceptions import LionIDError
from .undefined import LionUndefined


LN_UNDEFINED = LionUndefined()

class SysUtil:
    """Utility class providing various system-related functionalities."""

    @staticmethod
    def time(
        tz: timezone = TIME_CONFIG['tz'],
        type_: str = "timestamp",
        iso: bool = False,
        sep: str | None = "T",
        timespec: str | None = "auto",
    ) -> float | str | datetime:
        """Get current time in various formats."""
        now = datetime.now(tz=tz)
        if type_ == "timestamp":
            return now.timestamp()
        if iso:
            return now.isoformat(sep=sep, timespec=timespec) if sep else now.isoformat()
        return now

    @staticmethod
    def copy(obj: Any, deep: bool = True, num: int = 1) -> Any:
        """Create one or more copies of an object."""
        copy_func = copy.deepcopy if deep else copy.copy
        return [copy_func(obj) for _ in range(num)] if num > 1 else copy_func(obj)

    @staticmethod
    def id(
        n: int = 32,
        prefix: str | None = None,
        postfix: str | None = None,
        random_hyphen: bool = False,
        num_hyphens: int | None = None,
        hyphen_start_index: int | None = None,
        hyphen_end_index: int | None = None,
    ) -> str:
        """Generate a unique identifier."""
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
    def get_cpu_architecture() -> str:
        """Get the CPU architecture."""
        arch: str = platform.machine().lower()
        return "apple_silicon" if "arm" in arch or "aarch64" in arch else "other_cpu"

    @staticmethod
    def install_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
    ) -> None:
        """Attempt to import a package, installing it if not found."""
        pip_name = pip_name or package_name
        full_import_path = (
            f"{package_name}.{module_name}" if module_name else package_name
        )

        try:
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
            else:
                __import__(full_import_path)
            print(f"Successfully imported {import_name or full_import_path}.")
        except ImportError:
            print(f"Installing {pip_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
            else:
                __import__(full_import_path)

    @staticmethod
    def import_module(module_path: str):
        """Import a module by its path."""
        return importlib.import_module(module_path)

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """Check if a package is installed."""
        return importlib.util.find_spec(package_name) is not None

    @staticmethod
    @lru_cache
    def check_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
        attempt_install: bool = True,
        error_message: str = "",
    ) -> None:
        """Check if a package is installed, attempt to install if not."""
        try:
            if not SysUtil.is_package_installed(package_name):
                if attempt_install:
                    logging.info(
                        f"Package {package_name} not found. Attempting to install."
                    )
                    SysUtil.install_import(
                        package_name, module_name, import_name, pip_name
                    )
                else:
                    logging.info(f"Package {package_name} not found. {error_message}")
                    raise ImportError(
                        f"Package {package_name} not found. {error_message}"
                    )
        except ImportError as e:
            logging.error(f"Failed to import {package_name}. Error: {e}")
            raise ValueError(f"Failed to import {package_name}. Error: {e}") from e

    @staticmethod
    def list_installed_packages() -> list[str]:
        """List all installed packages."""
        return [dist.metadata["Name"] for dist in importlib.metadata.distributions()]

    @staticmethod
    def uninstall_package(package_name: str) -> None:
        """Uninstall a specified package."""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "uninstall", package_name, "-y"]
            )
            print(f"Successfully uninstalled {package_name}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to uninstall {package_name}. Error: {e}")

    @staticmethod
    def update_package(package_name: str) -> None:
        """Update a specified package."""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
            )
            print(f"Successfully updated {package_name}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to update {package_name}. Error: {e}")

    @staticmethod
    def new_path(
        directory: Path | str,
        filename: str,
        timestamp: bool = True,
        dir_exist_ok: bool = True,
        time_prefix: bool = False,
        timestamp_format: str | None = None,
        random_hash_digits: int = 0,
    ) -> Path:
        """Generate a new file path with optional timestamp and random hash."""
        directory = Path(directory)
        if not re.match(r"^[\w,\s-]+\.[A-Za-z]{1,5}$", filename):
            raise ValueError(
                "Invalid filename. Ensure it doesn't contain illegal characters and "
                "has a valid extension."
            )

        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        ext = f".{ext}" if ext else ""

        timestamp_str = ""
        if timestamp:
            timestamp_format = timestamp_format or "%Y%m%d%H%M%S"
            timestamp_str = datetime.now().strftime(timestamp_format)
            filename = (
                f"{timestamp_str}_{name}" if time_prefix else f"{name}_{timestamp_str}"
            )
        else:
            filename = name

        random_hash = (
            "-" + SysUtil.id(random_hash_digits) if random_hash_digits > 0 else ""
        )

        full_filename = f"{filename}{random_hash}{ext}"
        full_path = directory / full_filename
        full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)

        return full_path

    @staticmethod
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

    @staticmethod
    @lru_cache
    def get_lion_id(item: Any) -> str:
        """Get the Lion ID of an item."""
        if isinstance(item, Sequence) and len(item) == 1:
            item = item[0]
        if isinstance(item, str) and (
            (item.startswith("ln") and len(item) == 34) or
            (len(item) == 32)  # for backward compatibility
        ):
            return item
        if isinstance(item, AbstractElement):
            return item.ln_id
        raise LionIDError("Item must contain a lion id.")

    @staticmethod
    def is_same_dtype(
        input_: list | dict, dtype: Type | None = None, return_dtype: bool = False
    ) -> bool | tuple[bool, Type]:
        """Check if all elements in input have the same data type."""
        if not input_:
            return True if not return_dtype else (True, None)

        iterable = input_.values() if isinstance(input_, dict) else input_
        first_element_type = type(next(iter(iterable), None))

        dtype = dtype or first_element_type
        result = all(isinstance(element, dtype) for element in iterable)
        return (result, dtype) if return_dtype else result

    @staticmethod
    @lru_cache
    def mor(class_name: str) -> type:
        """
        Module Object Registry function for dynamic class loading.

        This function attempts to find and return a class based on its name.
        It searches through all loaded modules in sys.modules.

        Args:
            class_name: The name of the class to find.

        Returns:
            The requested class.

        Raises:
            ValueError: If the class is not found in any loaded module.
        """
        for module_name, module in sys.modules.items():
            if hasattr(module, class_name):
                return getattr(module, class_name)
        raise ValueError(f"Class '{class_name}' not found in any loaded module")


# File: lion_core/util/sysutil.py
