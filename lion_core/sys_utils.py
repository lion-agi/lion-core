import copy
import importlib
import importlib.metadata
import importlib.util
import logging
import os
import platform
import random
import re
import subprocess
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from shutil import copy2
from typing import Any, Literal, TypeVar

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

    def id(
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        n: int = None,
        prefix: str = None,
        postfix: str = None,
        random_hyphen: bool = None,
        num_hyphens: int = None,
        hyphen_start_index: int = None,
        hyphen_end_index: int = None,
    ) -> str:
        _dict = {
            "n": n,
            "prefix": prefix,
            "postfix": postfix,
            "random_hyphen": random_hyphen,
            "num_hyphens": num_hyphens,
            "hyphen_start_index": hyphen_start_index,
            "hyphen_end_index": hyphen_end_index,
        }
        _dict = {k: v for k, v in _dict.items() if v is not None}
        config = {**config.to_dict(), **_dict}
        return SysUtil._id(**config)

    @staticmethod
    def _id(
        *,
        n: int,
        prefix: str = "",
        postfix: str = "",
        random_hyphen: bool = False,
        num_hyphens: int = 0,
        hyphen_start_index: int = 6,
        hyphen_end_index: int = -6,
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
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
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

        check = isinstance(item_id, str)
        if check:
            id_len = (
                (len(config.prefix) if config.prefix else 0)
                + config.n
                + config.num_hyphens
                + (len(config.postfix) if config.postfix else 0)
            )
            if len(item_id) != id_len:
                check = False
        if check and config.prefix:
            if item_id.startswith(config.prefix):
                item_id = item_id[len(config.prefix) :]  # noqa
            else:
                check = False
        if check and config.postfix:
            if item_id.endswith(config.postfix):
                item_id = item_id[: -len(config.postfix)]
            else:
                check = False
        if check and config.num_hyphens:
            if config.num_hyphens != item_id.count("-"):
                check = False
        if check and config.hyphen_start_index:
            idx = config.hyphen_start_index - len(config.prefix)
            if idx > 0 and "-" in item_id[:idx]:
                check = False
        if check and config.hyphen_end_index:
            if config.hyphen_end_index < 0:
                idx = config.hyphen_end_index + id_len
            idx -= len(config.prefix + config.postfix)
            if idx < 0 and "-" in item_id[idx:]:
                check = False

        if check:
            return config.prefix + item_id + config.postfix
        if (
            isinstance(item_id, str) and len(item_id) == 32
        ):  # for backward compatibility
            return item_id
        raise LionIDError(
            f"The input object of type <{type(item).__name__}> does "
            "not contain or is not a valid Lion ID. Item must be an instance"
            " of `Observable` or a valid `ln_id`."
        )

    @staticmethod
    def is_id(
        item: Sequence[Observable] | Observable | str,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
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
            SysUtil.get_id(item, config)
            return True
        except LionIDError:
            return False

    @staticmethod
    def clear_path(
        path: Path | str,
        /,
        recursive: bool = False,
        exclude: list[str] | None = None,
    ) -> None:
        """
        Clear all files and directories in the specified path.

        Args:
            path: The path to the directory to clear.
            recursive: If True, clears directories recursively.
            exclude: A list of string patterns to exclude from deletion.

        Raises:
            FileNotFoundError: If the specified directory does not exist.
            PermissionError: If there are insufficient permissions to delete
                files.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"The specified directory {path} does not exist."
            )

        exclude = exclude or []
        exclude_pattern = re.compile("|".join(exclude)) if exclude else None

        for file_path in path.iterdir():
            if exclude_pattern and exclude_pattern.search(file_path.name):
                logging.info(f"Excluded from deletion: {file_path}")
                continue

            try:
                if file_path.is_dir():
                    if recursive:
                        SysUtil.clear_path(
                            file_path, recursive=True, exclude=exclude
                        )
                        file_path.rmdir()
                    else:
                        continue
                else:
                    file_path.unlink()
                logging.info(f"Successfully deleted {file_path}")
            except PermissionError as e:
                logging.error(
                    f"Permission denied when deleting {file_path}: {e}"
                )
            except Exception as e:
                logging.error(f"Failed to delete {file_path}: {e}")

    @staticmethod
    def create_path(
        directory: Path | str,
        filename: str,
        timestamp: bool = False,
        dir_exist_ok: bool = True,
        file_exist_ok: bool = False,
        time_prefix: bool = False,
        timestamp_format: str | None = None,
        random_hash_digits: int = 0,
    ) -> Path:
        """
        Generate a new file path with optional timestamp and random hash.

        Args:
            directory: The directory where the file will be created.
            filename: The base name of the file to create.
            timestamp: If True, adds a timestamp to the filename.
            dir_exist_ok: If True, doesn't raise an error if the directory
                exists.
            file_exist_ok: If True, allows overwriting of existing files.
            time_prefix: If True, adds the timestamp as a prefix instead of
                a suffix.
            timestamp_format: Custom format for the timestamp.
            random_hash_digits: Number of digits for the random hash.

        Returns:
            The full path to the new or existing file.

        Raises:
            ValueError: If the filename contains illegal characters.
            FileExistsError: If the file exists and file_exist_ok is False.
        """
        if "/" in filename or "\\" in filename:
            raise ValueError("Filename cannot contain directory separators.")
        directory = Path(directory)
        name, ext = (
            filename.rsplit(".", 1) if "." in filename else (filename, "")
        )
        if not ext:
            raise ValueError("Filename must contain an extension.")
        ext = f".{ext}" if ext else ""

        if timestamp:
            timestamp_str = datetime.now().strftime(
                timestamp_format or "%Y%m%d%H%M%S"
            )
            name = (
                f"{timestamp_str}_{name}"
                if time_prefix
                else f"{name}_{timestamp_str}"
            )

        if random_hash_digits > 0:
            random_hash = "-" + _unique_hash(random_hash_digits)
            name = f"{name}{random_hash}"

        full_filename = f"{name}{ext}"
        full_path = directory / full_filename

        if full_path.exists():
            if file_exist_ok:
                return full_path
            raise FileExistsError(
                f"File {full_path} already exists and file_exist_ok is False."
            )
        full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)
        return full_path

    @staticmethod
    def _get_path_kwargs(
        persist_path: str | Path, postfix: str, **path_kwargs: Any
    ) -> dict[str, Any]:
        """
        Generate keyword arguments for path creation.

        Args:
            persist_path: The base path to use.
            postfix: The file extension to use.
            **path_kwargs: Additional keyword arguments to override defaults.

        Returns:
            A dictionary of keyword arguments for path creation.
        """
        persist_path = Path(persist_path)
        postfix = f".{postfix.strip('.')}"

        if persist_path.suffix != postfix:
            dirname = persist_path
            filename = f"new_file{postfix}"
        else:
            dirname, filename = persist_path.parent, persist_path.name

        return {
            "timestamp": path_kwargs.get("timestamp", False),
            "file_exist_ok": path_kwargs.get("file_exist_ok", True),
            "directory": path_kwargs.get("directory", dirname),
            "filename": path_kwargs.get("filename", filename),
        }

    @staticmethod
    def list_files(
        dir_path: Path | str, extension: str | None = None
    ) -> list[Path]:
        """
        List all files in a specified directory with an optional extension
        filter, including files in subdirectories.

        Args:
            dir_path: The directory path where files are listed.
            extension: Filter files by extension.

        Returns:
            A list of Path objects representing files in the directory.

        Raises:
            NotADirectoryError: If the provided dir_path is not a directory.
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{dir_path} is not a directory.")

        pattern = f"*.{extension}" if extension else "*"
        return [f for f in dir_path.rglob(pattern) if f.is_file()]

    @staticmethod
    def split_path(path: Path | str) -> tuple[Path, str]:
        """
        Split a path into its directory and filename components.

        Args:
            path: The path to split.

        Returns:
            A tuple containing the directory and filename.
        """
        path = Path(path)
        return path.parent, path.name

    @staticmethod
    def copy_file(src: Path | str, dest: Path | str) -> None:
        """
        Copy a file from a source path to a destination path.

        Args:
            src: The source file path.
            dest: The destination file path.

        Raises:
            FileNotFoundError: If the source file does not exist or is not
                a file.
            PermissionError: If there are insufficient permissions to copy
                the file.
            OSError: If there's an OS-level error during the copy operation.
        """
        src_path, dest_path = Path(src), Path(dest)
        if not src_path.is_file():
            raise FileNotFoundError(
                f"{src_path} does not exist or is not a file."
            )

        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            copy2(src_path, dest_path)
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied when copying {src_path} to {dest_path}"
            ) from e
        except OSError as e:
            raise OSError(
                f"Failed to copy {src_path} to {dest_path}: {e}"
            ) from e

    @staticmethod
    def get_file_size(path: Path | str) -> int:
        """
        Get the size of a file or total size of files in a directory.

        Args:
            path: The file or directory path.

        Returns:
            The size in bytes.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If there are insufficient permissions
                to access the path.
        """
        path = Path(path)
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                return sum(
                    f.stat().st_size for f in path.rglob("*") if f.is_file()
                )
            else:
                raise FileNotFoundError(f"{path} does not exist.")
        except PermissionError as e:
            raise PermissionError(
                f"Permission denied when accessing {path}"
            ) from e

    @staticmethod
    def save_to_file(
        text: str,
        directory: Path | str,
        filename: str,
        timestamp: bool = False,
        dir_exist_ok: bool = True,
        file_exist_ok: bool = False,
        time_prefix: bool = False,
        timestamp_format: str | None = None,
        random_hash_digits: int = 0,
        verbose: bool = True,
    ) -> Path:
        """
        Save text to a file within a specified directory, optionally adding a
        timestamp, hash, and verbose logging.

        Args:
            text: The text to save.
            directory: The directory path to save the file.
            filename: The filename for the saved text.
            timestamp: If True, append a timestamp to the filename.
            dir_exist_ok: If True, creates the directory if it does not exist.
            time_prefix: If True, prepend the timestamp instead of appending.
            timestamp_format: A custom format for the timestamp.
            random_hash_digits: Number of random hash digits to append
                to filename.
            verbose: If True, logs the file path after saving.

        Returns:
            Path: The path to the saved file.

        Raises:
            OSError: If there's an error creating the directory or
                writing the file.
        """
        try:
            file_path = SysUtil.create_path(
                directory=directory,
                filename=filename,
                timestamp=timestamp,
                dir_exist_ok=dir_exist_ok,
                file_exist_ok=file_exist_ok,
                time_prefix=time_prefix,
                timestamp_format=timestamp_format,
                random_hash_digits=random_hash_digits,
            )
            with file_path.open("w", encoding="utf-8") as file:
                file.write(text)
            if verbose:
                logging.info(f"Text saved to: {file_path}")
            return file_path

        except OSError as e:
            logging.error(f"Failed to save file {filename}: {e}")
            raise

    @staticmethod
    def read_file(path: Path | str, /) -> str:
        """
        Read the contents of a file.

        Args:
            path: The path to the file to read.

        Returns:
            str: The contents of the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If there are insufficient permissions to read
                the file.
        """
        try:
            return Path(path).read_text(encoding="utf-8")
        except FileNotFoundError as e:
            logging.error(f"File not found: {path}: {e}")
            raise
        except PermissionError as e:
            logging.error(f"Permission denied when reading file: {path}: {e}")
            raise

    @staticmethod
    def get_cpu_architecture() -> str:
        """
        Get the CPU architecture.

        Returns:
            str: 'arm64' if ARM-based, 'x86_64' for Intel/AMD 64-bit, or the
                actual architecture string for other cases.
        """
        arch: str = platform.machine().lower()
        if "arm" in arch or "aarch64" in arch:
            return "arm64"
        elif "x86_64" in arch or "amd64" in arch:
            return "x86_64"
        else:
            return arch

    @staticmethod
    def install_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
    ):
        """
        Attempt to import a package, installing it if not found.

        Args:
            package_name: The name of the package to import.
            module_name: The specific module to import (if any).
            import_name: The specific name to import from the module (if any).
            pip_name: The name to use for pip installation (if different).

        Raises:
            ImportError: If the package cannot be imported or installed.
            subprocess.CalledProcessError: If pip installation fails.
        """
        pip_name = pip_name or package_name

        try:
            return SysUtil.import_module(
                package_name=package_name,
                module_name=module_name,
                import_name=import_name,
            )
        except ImportError:
            logging.info(f"Installing {pip_name}...")
            try:
                _run_pip_command(["install", pip_name])
                return SysUtil.import_module(
                    package_name=package_name,
                    module_name=module_name,
                    import_name=import_name,
                )
            except subprocess.CalledProcessError as e:
                raise ImportError(f"Failed to install {pip_name}: {e}") from e
            except ImportError as e:
                raise ImportError(
                    f"Failed to import {pip_name} after installation: {e}"
                ) from e

    @staticmethod
    def import_module(
        package_name: str,
        module_name: str = None,
        import_name: str | list = None,
    ) -> Any:
        """
        Import a module by its path.

        Args:
            module_path: The path of the module to import.

        Returns:
            The imported module.

        Raises:
            ImportError: If the module cannot be imported.
        """
        try:
            full_import_path = (
                f"{package_name}.{module_name}"
                if module_name
                else package_name
            )

            if import_name:
                import_name = (
                    [import_name]
                    if not isinstance(import_name, list)
                    else import_name
                )
                a = __import__(
                    full_import_path,
                    fromlist=import_name,
                )
                if len(import_name) == 1:
                    return getattr(a, import_name[0])
                return [getattr(a, name) for name in import_name]
            else:
                return __import__(full_import_path)

        except ImportError as e:
            raise ImportError(
                f"Failed to import module {full_import_path}: {e}"
            ) from e

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """
        Check if a package is installed.

        Args:
            package_name: The name of the package to check.

        Returns:
            bool: True if the package is installed, False otherwise.
        """
        return importlib.util.find_spec(package_name) is not None

    @staticmethod
    def check_import(
        package_name: str,
        module_name: str | None = None,
        import_name: str | None = None,
        pip_name: str | None = None,
        attempt_install: bool = True,
        error_message: str = "",
    ):
        """
        Check if a package is installed, attempt to install if not.

        Args:
            package_name: The name of the package to check.
            module_name: The specific module to import (if any).
            import_name: The specific name to import from the module (if any).
            pip_name: The name to use for pip installation (if different).
            attempt_install: Whether to attempt installation if not found.
            error_message: Custom error message to use if package not found.

        Raises:
            ImportError: If the package is not found and not installed.
            ValueError: If the import fails after installation attempt.
        """
        if not SysUtil.is_package_installed(package_name):
            if attempt_install:
                logging.info(
                    f"Package {package_name} not found. Attempting "
                    "to install.",
                )
                try:
                    return SysUtil.install_import(
                        package_name=package_name,
                        module_name=module_name,
                        import_name=import_name,
                        pip_name=pip_name,
                    )
                except ImportError as e:
                    raise ValueError(
                        f"Failed to install {package_name}: {e}"
                    ) from e
            else:
                logging.info(
                    f"Package {package_name} not found. {error_message}",
                )
                raise ImportError(
                    f"Package {package_name} not found. {error_message}",
                )

        return SysUtil.import_module(
            package_name=package_name,
            module_name=module_name,
            import_name=import_name,
        )

    @staticmethod
    def list_installed_packages() -> list[str]:
        """
        List all installed packages.

        Returns:
            List[str]: A list of names of installed packages.
        """
        try:
            return [
                dist.metadata["Name"]
                for dist in importlib.metadata.distributions()
            ]
        except Exception as e:
            logging.error(f"Failed to list installed packages: {e}")
            return []

    @staticmethod
    def uninstall_package(package_name: str) -> None:
        """
        Uninstall a specified package.

        Args:
            package_name: The name of the package to uninstall.

        Raises:
            subprocess.CalledProcessError: If the uninstallation fails.
        """
        try:
            _run_pip_command(["uninstall", package_name, "-y"])
            logging.info(f"Successfully uninstalled {package_name}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to uninstall {package_name}. Error: {e}")
            raise

    @staticmethod
    def update_package(package_name: str) -> None:
        """
        Update a specified package.

        Args:
            package_name: The name of the package to update.

        Raises:
            subprocess.CalledProcessError: If the update fails.
        """
        try:
            _run_pip_command(["install", "--upgrade", package_name])
            logging.info(f"Successfully updated {package_name}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to update {package_name}. Error: {e}")
            raise


def _unique_hash(n: int = 32) -> str:
    """unique random hash"""
    current_time = datetime.now().isoformat().encode("utf-8")
    random_bytes = os.urandom(42)
    return sha256(current_time + random_bytes).hexdigest()[:n]


def _run_pip_command(
    args: Sequence[str],
) -> subprocess.CompletedProcess[bytes]:
    """Run a pip command."""
    return subprocess.run(
        [sys.executable, "-m", "pip"] + list(args),
        check=True,
        capture_output=True,
    )


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
