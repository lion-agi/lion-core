"""DataLog module for the Lion framework."""

from __future__ import annotations
from typing import Any

from pydantic import Field

from lion_core.log.base import BaseLog, LogLevel, LogContent


class DataLogContent(LogContent):
    """Extended content model for data log entries."""

    input_data: Any = Field(default=None)
    output_data: Any = Field(default=None)


class DataLog(BaseLog):
    """
    Specialized log class for data processing activities.

    Extends BaseLog to include input and output data fields.
    """

    content: DataLogContent = Field(...)

    @classmethod
    def create(
        cls,
        message: str,
        level: LogLevel = LogLevel.INFO,
        input_data: Any = None,
        output_data: Any = None,
        **kwargs: Any
    ) -> DataLog:
        """
        Create a new DataLog instance.

        Args:
            message: The main log message.
            level: The severity level of the log entry.
            input_data: The input data related to the log entry.
            output_data: The output data related to the log entry.
            **kwargs: Additional keyword arguments for the log entry.

        Returns:
            A new DataLog instance.
        """
        return cls(
            content=DataLogContent(
                message=message,
                level=level,
                input_data=input_data,
                output_data=output_data
            ),
            **kwargs
        )

# File: lion_core/log/d_log.py