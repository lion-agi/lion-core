from typing import Any


class LionException(Exception):
    """Base exception for all Lion-specific errors."""

    def __init__(
        self, message: str = "An error occurred in the Lion framework."
    ):
        self.message = message
        super().__init__(self.message)


class LionValueError(LionException, ValueError):
    """Exception raised for errors in input values or item attributes."""

    def __init__(
        self, message: str = "Invalid value.", value: Any | None = None
    ):
        self.value = value
        value_info = f" Value: {value}" if value is not None else ""
        super().__init__(f"{message}{value_info}")


class LionTypeError(LionException, TypeError):
    """Exception raised for unexpected types or type mismatches."""

    def __init__(
        self,
        message: str = "Type error.",
        expected_type: type | None = None,
        actual_type: type | None = None,
    ):
        self.expected_type = expected_type
        self.actual_type = actual_type
        type_info = ""
        if expected_type and actual_type:
            type_info = f" Expected: {expected_type}, Actual: {actual_type}"
        super().__init__(f"{message}{type_info}")


class LionOperationError(LionException):
    """Exception raised for errors during general Lion operations."""

    def __init__(
        self, message: str = "Operation failed.", operation: str | None = None
    ):
        self.operation = operation
        op_info = f" Operation: {operation}" if operation else ""
        super().__init__(f"{message}{op_info}")


class LionItemError(LionException):
    """Base exception for errors related to framework items."""

    def __init__(
        self, message: str = "Item error.", item_id: str | None = None
    ):
        self.item_id = item_id
        item_info = f" Item ID: {item_id}" if item_id else ""
        super().__init__(f"{message}{item_info}")


class LionIDError(LionItemError):
    """Exception raised when an item does not have a Lion ID."""

    def __init__(
        self,
        message: str = "Item must contain a Lion ID.",
        item_id: str | None = None,
    ):
        super().__init__(message, item_id)


class ItemNotFoundError(LionItemError):
    """Exception raised when an item is not found."""

    def __init__(
        self, message: str = "Item not found.", item_id: str | None = None
    ):
        super().__init__(message, item_id)


class ItemExistsError(LionItemError):
    """Exception raised when an item already exists."""

    def __init__(
        self, message: str = "Item already exists.", item_id: str | None = None
    ):
        super().__init__(message, item_id)


class LionRelationError(LionItemError):
    """Exception raised for errors in item relationships."""

    def __init__(
        self,
        message: str = "Relation error.",
        source_id: str | None = None,
        target_id: str | None = None,
    ):
        self.source_id = source_id
        self.target_id = target_id
        relation_info = ""
        if source_id and target_id:
            relation_info = f" Source: {source_id}, Target: {target_id}"
        super().__init__(f"{message}{relation_info}")


class LionAccessError(LionException):
    """Exception raised when accessing without proper permissions."""

    def __init__(
        self, message: str = "Access error.", resource_id: str | None = None
    ):
        self.resource_id = resource_id
        resource_info = f" Resource ID: {resource_id}" if resource_id else ""
        super().__init__(f"{message}{resource_info}")


class LionQuantumError(LionException):
    """Exception raised for errors in quantum-related operations."""

    def __init__(
        self,
        message: str = "Quantum operation error.",
        state: Any | None = None,
    ):
        self.state = state
        state_info = f" State: {state}" if state is not None else ""
        super().__init__(f"{message}{state_info}")


class LionResourceError(LionException):
    """Exception raised for errors in resource-related operations."""

    def __init__(
        self,
        message: str = "Resource operation error.",
        resource_id: str | None = None,
    ):
        self.resource_id = resource_id
        resource_info = f" Resource ID: {resource_id}" if resource_id else ""
        super().__init__(f"{message}{resource_info}")
