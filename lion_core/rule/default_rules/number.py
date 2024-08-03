from typing import Any, override
from lion_core.libs import to_num
from lion_core.exceptions import LionTypeError
from lion_core.rule.base import Rule


class NumberRule(Rule):

    base_config = {
        "apply_types": ["int", "float", "complex"],
        "upper_bound": None,
        "lower_bound": None,
        "num_type": "float",
        "precision": None,
        "num_count": 1,
    }

    @override
    async def validate(self, value: Any) -> Any:
        """
        Validate that the value is a number.

        Args:
            value (Any): The value to validate.

        Returns:
            Any: The validated value.

        Raises:
            ValueError: If the value is not a valid number.
        """
        if isinstance(value, (int, float, complex)):
            return value
        raise LionTypeError(f"Invalid number field type: {type(value)}")

    @override
    async def fix_field(self, value: Any, *args, **kwargs) -> Any:
        """
        Attempt to fix the value by converting it to a number.

        Args:
            value (Any): The value to fix.

        Returns:
            Any: The fixed value.

        Raises:
            ValueError: If the value cannot be converted to a number.
        """
        return to_num(value, **self["validation_kwargs"])
