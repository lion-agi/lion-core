import os
import copy
import sys
import subprocess
import importlib
import platform
from pathlib import Path
import re

from hashlib import sha256
import random
from datetime import datetime, timezone
import logging
from typing import Any


class SysUtils:

    @staticmethod
    def time(
        tz: timezone = timezone.utc,
        type_: str = "timestamp",  # timestamp, datetime
        iso: bool = False,
        sep: str = ...,
        timespec: str = ...,
    ):

        match type_:
            case "timestamp":
                return datetime.now(tz=tz).timestamp()
            case "datetime":
                if iso:
                    return datetime.now(tz=tz).isoformat(sep=sep, timespec=timespec)
                return datetime.now(tz=tz)

    @staticmethod
    def copy(
        obj: Any,
        deep: bool = True,
        num: int = 1,
    ):
        def _copy():
            if deep:
                return copy.deepcopy(obj)
            return copy.copy(obj)

        return [_copy() for _ in range(num)] if num > 1 else _copy()

    @staticmethod
    def id(
        n: int = 32,  # the number of characters to be generated
        prefix: str = None,  # the prefix of the generated id
        postfix: str = None,  # the postfix of the generated id
        random_hyphen: bool = False,  # whether to insert random hyphens
        num_hyphens: int = None,  # the number of hyphens to insert
        hyphen_start_index: int = None,  # the index where the hyphens can start being inserted
        hyphen_end_index: int = None,  # the index where the hyphens need to stop being inserted
    ):
        _t = SysUtils.time(type_="datetime", iso=True).encode()
        _r = os.urandom(16)
        _id = sha256(_t + _r).hexdigest()[:n]

        if random_hyphen:
            _id = SysUtils._insert_random_hyphens(
                s=_id,
                num_hyphens=num_hyphens,
                start_index=hyphen_start_index,
                end_index=hyphen_end_index,
            )

        if prefix:
            _id = prefix + _id

        if postfix:
            _id = _id + postfix

        return _id

    @staticmethod
    def install(
        package_name: str,
        module_name: str = None,
        import_name: str = None,
        pip_name: str = None,
        attempt_install: bool = True,
        error_message: str = "",
    ):

        try:
            if (a := importlib.util.find_spec(package_name)) is not None:
                if attempt_install:
                    logging.info(
                        f"Package {package_name} not found. Attempting to install."
                    )
                    SysUtils._install(package_name, module_name, import_name, pip_name)
                else:
                    logging.info(f"Package {package_name} not found. {error_message}")
                    raise ImportError(
                        f"Package {package_name} not found. {error_message}"
                    )
        except ImportError as e:  # More specific exception handling
            logging.error(f"Failed to import {package_name}. Error: {e}")
            raise ValueError(f"Failed to import {package_name}. Error: {e}") from e

    @staticmethod
    def new_path(
        directory: Path | str,
        filename: str,
        timestamp: bool = True,
        dir_exist_ok: bool = True,
        time_prefix: bool = False,
        timestamp_format: str | None = None,
        random_hash_digits=0,
    ) -> Path:

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
            "-" + SysUtils.id(random_hash_digits) if random_hash_digits > 0 else ""
        )

        full_filename = f"{filename}{random_hash}{ext}"
        full_path = directory / full_filename
        full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)

        return full_path

    @staticmethod
    def _insert_random_hyphens(
        s: str,  # the string to insert hyphens into
        num_hyphens: int = 1,  # the number of hyphens to insert
        start_index: int = None,  # where the hyphens can start being inserted
        end_index: int = None,  # where the hyphens need to stop being inserted
    ) -> str:

        if len(s) < 2:
            return s

        prefix = s[:start_index] if start_index else ""
        postfix = s[end_index:] if end_index else ""
        modifiable_part = s[start_index:end_index] if start_index else s

        # Determine positions to insert the hyphens
        positions = random.sample(range(len(modifiable_part)), num_hyphens)
        positions.sort()

        # Insert hyphens at the chosen positions
        for pos in reversed(positions):
            modifiable_part = modifiable_part[:pos] + "-" + modifiable_part[pos:]

        # Combine the unmodifiable prefix with the modified part
        return prefix + modifiable_part + postfix

    @staticmethod
    def _get_cpu_architecture() -> str:
        arch: str = platform.machine().lower()
        return "apple_silicon" if "arm" in arch or "aarch64" in arch else "other_cpu"

    @staticmethod
    def _install(
        package_name: str,
        module_name: str = None,
        import_name: str = None,
        pip_name: str = None,
    ):

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
            print(
                f"Module {full_import_path} or attribute {import_name} not found. "
                f"Installing {pip_name}..."
            )
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

            # Retry the import after installation
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
            else:
                __import__(full_import_path)
