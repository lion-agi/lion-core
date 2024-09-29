"""lion-core."""

import logging

from .log_manager import LogManager
from .setting import BASE_LION_FIELDS, DEFAULT_LION_ID_CONFIG, LN_UNDEFINED
from .version import __version__

__all__ = [
    "BASE_LION_FIELDS",
    "DEFAULT_LION_ID_CONFIG",
    "LN_UNDEFINED",
    "LogManager",
    "__version__",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
