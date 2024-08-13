from typing import Any
from typing_extensions import override
from lion_core.libs import strip_lower
from lion_core.rule.base import Rule
from lion_core.exceptions import LionOperationError


class BooleanRule(Rule):
    """
    Rule for validating that a value is a boolean.

    Attributes:
        apply_type (str): The type of data to which the rule applies.
    """

    @override
    async def validate(self, value: Any) -> bool:
        """
        Validate that the value is a boolean.

        Args:
            value (Any): The value to validate.

        Returns:
            bool: The validated value.

        Raises:
            ValueError: If the value is not a valid boolean.
        """
        if isinstance(value, bool):
            return value
        raise LionOperationError(f"Invalid boolean value.")

    @override
    async def fix_field(self, value) -> bool:
        value = strip_lower(value)
        if value in ["true", "1", "correct", "yes"]:
            return True

        elif value in ["false", "0", "incorrect", "no", "none", "n/a"]:
            return False

        raise LionOperationError(f"Failed to convert {value} into a boolean value")
