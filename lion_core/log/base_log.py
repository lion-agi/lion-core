from lion_core.abc.concept import Element


class BaseLog(Element):
    """Base class for all logs in the Lion framework.

    This class extends Element and provides a foundation for creating
    and managing logs within the Lion framework.

    Attributes:
        message (str): A message to be logged.
        log_level (str): The log level of the message.
        timestamp (float): Creation timestamp of the log.

    Class Attributes:
        model_config (ConfigDict): Configuration for the Pydantic model.
    """

    message: str
    log_level: str
    timestamp: float

    def __str__(self) -> str:
        """Return a string representation of the Log.

        Returns:
            str: A string representation of the Log.
        """
        return f"{self.log_level}: {self.message}"
