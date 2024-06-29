"""
This module defines the FunctionCalling class, which facilitates dynamic
invocation of functions based on various input types. It supports initializing
function calls from tuples, dictionaries, ActionRequest objects, or JSON strings.

Note:
    Function Calling object is the only way for AI system to call functions.
"""

from functools import singledispatchmethod
from typing import Any, Callable, Dict


from lion_core.libs import ucall, fuzzy_parse_json
from lion_core.core.generic.concepts import Actionable
from lion_core.core.sendable.action_request import ActionRequest


class FunctionCalling(Actionable):
    """
    A class for dynamically invoking functions based on various input types,
    allowing for specification of the function and arguments through multiple
    formats including tuples, dictionaries, ActionRequests, or JSON strings.
    """

    def __init__(self, function: Callable, arguments: Dict[str, Any] = None):
        """
        Initializes a new instance of FunctionCalling with the given function
        and optional arguments.

        Args:
            function (Callable): The function to be called.
            arguments (Dict[str, Any]): Arguments to pass to the function.
                Defaults to an empty dictionary.
        """
        self.function = function
        self.arguments = arguments or {}

    @property
    def func_name(self) -> str:
        """
        Returns the name of the function.

        Returns:
            str: The function's name.
        """
        return self.function.__name__

    @singledispatchmethod
    @classmethod
    def create(cls, func_call: Any) -> "FunctionCalling":
        """
        Creates an instance of FunctionCalling based on the type of input.

        Args:
            func_call (Any): The function call description, which can be a tuple, dict,
                ActionRequest, or JSON string.

        Returns:
            FunctionCalling: An instance of FunctionCalling prepared to invoke
                the specified function.

        Raises:
            TypeError: If the input type is not supported.
        """
        raise TypeError(f"Unsupported type {type(func_call)}")

    @create.register(tuple)
    def _(cls, function_calling: tuple) -> "FunctionCalling":
        if len(function_calling) == 2:
            return cls(function=function_calling[0], arguments=function_calling[1])
        else:
            raise ValueError(f"Invalid function call {function_calling}")

    @create.register(dict)
    def _(cls, function_calling: Dict[str, Any]) -> "FunctionCalling":
        if len(function_calling) == 2 and (
            {"function", "arguments"} <= function_calling.keys()
        ):
            return cls.create(
                (function_calling["function"], function_calling["arguments"])
            )
        raise ValueError(f"Invalid function call {function_calling}")

    @create.register(ActionRequest)
    def _(cls, function_calling: ActionRequest) -> "FunctionCalling":
        return cls.create((function_calling.function, function_calling.arguments))

    @create.register(str)
    def _(cls, function_calling: str) -> "FunctionCalling":
        _call = None
        try:
            _call = fuzzy_parse_json(function_calling)
        except Exception as e:
            raise ValueError(f"Invalid function call {function_calling}") from e

        if isinstance(_call, dict):
            return cls.create(_call)
        raise ValueError(f"Invalid function call {function_calling}")

    async def invoke(self) -> Any:
        """
        Asynchronously invokes the stored function with the provided arguments.

        Returns:
            Any: The result of the function call.
        """
        return await ucall(self.function, **self.arguments)

    def __str__(self) -> str:
        """
        Returns a string representation of the function call.

        Returns:
            str: String representation of the function call.
        """
        return f"{self.func_name}({self.arguments})"

    def __repr__(self) -> str:
        return self.__str__()
