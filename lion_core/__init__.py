"""lion-core"""

import logging

from .log_manager import event_log_manager, global_log_manager
from .setting import BASE_LION_FIELDS, LION_ID_CONFIG, LN_UNDEFINED
from .version import __version__

__all__ = [
    "log_manager",
    "LN_UNDEFINED",
    "LION_ID_CONFIG",
    "BASE_LION_FIELDS",
    "event_log_manager",
    "global_log_manager",
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
