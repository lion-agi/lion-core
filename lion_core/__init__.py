"""lion-core"""

import logging

from .log_manager import LogManager
from .setting import BASE_LION_FIELDS, LION_ID_CONFIG, LN_UNDEFINED
from .version import __version__

event_log_manager = LogManager(
    persist_dir="./data/logs",
    subfolder="events",
    file_prefix="event_",
)
global_log_manager = LogManager(
    persist_dir="./data/logs",
    subfolder="global",
)

__all__ = [
    "LN_UNDEFINED",
    "LION_ID_CONFIG",
    "BASE_LION_FIELDS",
    "event_log_manager",
    "global_log_manager",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
