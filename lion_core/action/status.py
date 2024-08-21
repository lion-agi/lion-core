from enum import Enum


class ActionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


__all__ = ["ActionStatus"]
# File lion_core/action/status.py
