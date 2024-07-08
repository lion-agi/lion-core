from typing import Any, Callable
from lion_core.abc.event import Action
from lion_core.libs import ucall


class FunctionCalling(Action):
    """Represents a callable function with its arguments.

    This class encapsulates a function and its arguments, allowing for
    delayed execution. It inherits from the Action class, making it
    suitable for use in event-driven scenarios.

    Attributes:
        function: The function to be called.
        arguments: Arguments to pass to the function.
    """

    def __init__(
        self,
        function: Callable[..., Any],
        arguments: dict[str, Any] | None = None
    ) -> None:
        """Initialize a new instance of FunctionCalling.

        Args:
            function: The function to be called.
            arguments: Arguments to pass to the function. Defaults to None.
        """
        super().__init__()
        self.function: Callable[..., Any] = function
        self.arguments: dict[str, Any] = arguments or {}

    async def invoke(self) -> Any:
        """Asynchronously invoke the stored function with the arguments.

        Returns:
            The result of the function call.

        Raises:
            Exception: Any exception that occurs during function execution.
        """
        return await ucall(self.function, **self.arguments)

    def __str__(self) -> str:
        """Return a string representation of the function call.

        Returns:
            A string representation of the function call.
        """
        return f"{self.function.__name__}({self.arguments})"

    def __repr__(self) -> str:
        """Return a string representation of the FunctionCalling object.

        Returns:
            A string representation of the FunctionCalling object.
        """
        return (f"FunctionCalling(function={self.function.__name__}, "
                f"arguments={self.arguments})")