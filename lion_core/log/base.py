"""Base module for logging in the Lion framework."""

from __future__ import annotations
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_serializer


from lion_core.abc import ImmutableRecord

from lion_core.element import Element

DEFAULT_SERIALIZATION_INCLUDE: set[str] = {"ln_id", "timestamp", "content"}



class LogCategory(str, Enum):
    """
    Enum for categorizing log entries.

    This enum provides a standardized set of categories for log entries,
    allowing for consistent classification across the logging system.
    """

    INFERENCE = "inference"
    ACTION = "action"
    RULE = "rule"
    OTHER = "other"


class LogStatus(str, Enum):
    """
    Enum for log entry status.

    This enum defines possible statuses for log entries, providing a way to
    track the outcome or progress of the logged operation.
    """

    COMPLETED = "completed"
    FAILED = "failed"
    PASSED = "passed"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    
    
class LogLevel(str, Enum):
    """Log levels for categorizing the severity of log entries."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogContent(BaseModel):
    """Flexible content model for log entries."""

    level: LogLevel = Field(default=LogLevel.INFO)
    message: str = Field(...)


class BaseLog(Element, ImmutableRecord):
    """
    Base class for all logs in the Lion framework.

    Attributes:
        content: The main content of the log entry.
    """

    content: LogContent = Field(...)

    @classmethod
    def create(
        cls, message: str, level: LogLevel = LogLevel.INFO, **kwargs: Any
    ) -> BaseLog:
        """
        Create a new BaseLog instance.

        Args:
            message: The main log message.
            level: The severity level of the log entry.
            **kwargs: Additional keyword arguments for the log entry.

        Returns:
            A new BaseLog instance.
        """
        return cls(content=LogContent(message=message, level=level), **kwargs)

    @model_serializer
    def serialize(self, **kwargs: Any) -> dict[str, Any]:
        """Serialize the BaseLog to a dictionary."""
        kwargs["include"] = kwargs.get(
            "include", DEFAULT_SERIALIZATION_INCLUDE
        )
        return super().serialize(**kwargs)

    def __str__(self) -> str:
        """Return a string representation of the Log."""
        return (f"{self.__class__.__name__}(ln_id={self.ln_id[:8]}..., "
                f"level={self.content.level}, "
                f"message={self.content.message[:50]}...)")

# File: lion_core/log/base.py