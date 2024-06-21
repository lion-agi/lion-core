"""
Optimized system utilities for common operations in the LionAGI system.

This module provides essential utility functions for system operations,
focusing on the most commonly used and necessary functionalities.
"""

import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Union, Optional

class SystemUtils:
    @staticmethod
    def create_id(n: int = 32) -> str:
        """Generates a unique identifier."""
        current_time = datetime.now().isoformat().encode("utf-8")
        random_bytes = os.urandom(42)
        return sha256(current_time + random_bytes).hexdigest()[:n]

    @staticmethod
    def check_import(
        package_name: str,
        module_name: Optional[str] = None,
        import_name: Optional[str] = None,
        pip_name: Optional[str] = None,
        attempt_install: bool = True,
        error_message: str = "",
    ) -> None:
        """Checks if a package is installed; if not, attempts to install and import it."""
        try:
            if module_name:
                module = __import__(f"{package_name}.{module_name}", fromlist=[import_name or ""])
            else:
                module = __import__(package_name)
            
            if import_name:
                getattr(module, import_name)
        except ImportError:
            if attempt_install:
                logging.info(f"Package {package_name} not found. Attempting to install.")
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name or package_name])
                # Retry import after installation
                if module_name:
                    module = __import__(f"{package_name}.{module_name}", fromlist=[import_name or ""])
                else:
                    module = __import__(package_name)
                if import_name:
                    getattr(module, import_name)
            else:
                logging.info(f"Package {package_name} not found. {error_message}")
                raise ImportError(f"Package {package_name} not found. {error_message}")

    @staticmethod
    def get_timestamp(tz: timezone = timezone.utc, sep: Optional[str] = "_") -> str:
        """Returns a timestamp string with optional custom separators and timezone."""
        timestamp = datetime.now(tz=tz).isoformat()
        if sep is not None:
            for sym in ["-", ":", "."]:
                timestamp = timestamp.replace(sym, sep)
        return timestamp

    @staticmethod
    def create_path(
        directory: Union[Path, str],
        filename: str,
        timestamp: bool = True,
        time_prefix: bool = False,
        random_hash_digits: int = 0,
    ) -> Path:
        """Creates a path with optional timestamp and random hash."""
        directory = Path(directory)
        name, ext = os.path.splitext(filename)
        
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
            name = f"{timestamp_str}_{name}" if time_prefix else f"{name}_{timestamp_str}"
        
        if random_hash_digits > 0:
            name += f"-{SystemUtils.create_id(random_hash_digits)}"
        
        full_filename = f"{name}{ext}"
        full_path = directory / full_filename
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        return full_path

    @staticmethod
    def save_to_file(
        text: str,
        directory: Union[Path, str],
        filename: str,
        timestamp: bool = True,
        time_prefix: bool = False,
        random_hash_digits: int = 0,
        verbose: bool = True,
    ) -> bool:
        """Saves text to a file with optional timestamp and random hash."""
        file_path = SystemUtils.create_path(
            directory=directory,
            filename=filename,
            timestamp=timestamp,
            time_prefix=time_prefix,
            random_hash_digits=random_hash_digits,
        )

        with open(file_path, "w") as file:
            file.write(text)

        if verbose:
            print(f"Text saved to: {file_path}")

        return True

