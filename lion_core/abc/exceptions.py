# lion_core/abc/exceptions.py


class LionError(Exception):
    """Base class for all exceptions in the LION system."""

    def __init__(self, message=None):
        if message is None:
            message = "An error occurred in the LION system."
        super().__init__(message)


class LionIDError(LionError):
    """Exception raised for errors in the Lion ID."""

    def __init__(self, message=None):
        if message is None:
            message = "Invalid Lion ID."
        super().__init__(message)


class LionElementError(LionError):
    """Exception raised for errors in the Lion element."""

    def __init__(self, message=None):
        if message is None:
            message = "Invalid Lion element."
        super().__init__(message)


class ItemExistedError(LionElementError):
    """Exception raised when an entity already exists."""

    def __init__(self, message=None):
        if message is None:
            message = "Entity already exists."
        super().__init__(message)


class ItemNotFoundError(LionElementError):
    """Exception raised when an entity does not exist."""

    def __init__(self, message=None):
        if message is None:
            message = "Entity does not exist."
        super().__init__(message)


class LionValueError(LionError):
    """Exception raised for errors in the input value."""

    def __init__(self, message=None):
        if message is None:
            message = "Incorrect value."
        super().__init__(message)


class LionValidationError(LionValueError):
    """Exception raised for errors in the Lion validation."""

    def __init__(self, message=None):
        if message is None:
            message = "Validation failed."
        super().__init__(message)


class LionOperationError(LionError):
    """Exception raised for errors in the Lion operation."""

    def __init__(self, message=None):
        if message is None:
            message = "Operation failed."
        super().__init__(message)


class LionRelationError(LionError):
    """Exception raised for errors in the Lion relation."""

    def __init__(self, message=None):
        if message is None:
            message = "Relation failed."
        super().__init__(message)


class LionQuantumError(LionError):
    """Exception raised for errors in the Lion quantum system."""

    def __init__(self, message=None):
        if message is None:
            message = "Quantum error occurred."
        super().__init__(message)
