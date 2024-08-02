from typing import override, Any
from lion_core.libs import to_str
from lion_core.rule.base import Rule


class StringRule(Rule):
    """
    Rule for validating and converting string values.

    Attributes:
        fields (list[str]): The list of fields to which the rule applies.
        apply_type (str): The type of data to which the rule applies.
    """

    base_config = {
        "use_model_dump": True,
        "strip_lower": False,
        "chars": None,
        "apply_types": ["str"],
    }

    @override
    async def validate(self, value):
        """
        Validate that the value is a string.

        Args:
            value: The value to validate.

        Returns:
            str: The validated string value.

        Raises:
            ValueError: If the value is not a string or is an empty string.
        """
        if isinstance(value, str):
            return value
        raise ValueError(f"Invalid string field type.")

    @override
    async def perform_fix(self, value):
        """
        Attempt to convert a value to a string.

        Args:
            value: The value to convert to a string.

        Returns:
            str: The value converted to a string.

        Raises:
            ValueError: If the value cannot be converted to a string.
        """
        try:
            return to_str(value, **self.validation_kwargs)
        except Exception as e:
            value = str(value)[30] + ".." if len(str(value)) > 30 else str(value)
            raise ValueError(f"Failed to convert {value} into a string value") from e
