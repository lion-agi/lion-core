class LionError(Exception):
    """Base class for all exceptions in the Lion system."""

    def __init__(self, message=None):
        if message is None:
            message = "An unspecified error occurred in the Lion system."
        super().__init__(message)
        
        
class LionIDError(LionError):
    """Exception raised for errors in the Lion ID."""

    def __init__(self, message=None):
        if message is None:
            message = "Invalid Lion ID."
        super().__init__(message)


class LionTypeError(LionError):
    """Exception raised for type mismatch or type checking errors."""

    def __init__(self, message=None):
        if message is None:
            message = "Incorrect type."
        super().__init__(message)


class LionValueError(LionError):
    """Exception raised for errors in the input value."""

    def __init__(self, message=None):
        if message is None:
            message = "Incorrect value."
        super().__init__(message)


class LionEntityError(LionError):
    """Exception raised for errors in the Lion entity."""

    def __init__(self, message=None):
        if message is None:
            message = "Invalid lion entity."
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
