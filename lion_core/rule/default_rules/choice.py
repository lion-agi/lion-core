from typing import override
from lion_core.libs import choose_most_similar
from lion_core.rule.base import Rule


class ChoiceRule(Rule):
    """
    Rule for validating that a value is within a set of predefined choices.

    Attributes:
        apply_type (str): The type of data to which the rule applies.
        keys (list): The list of valid choices.
    """

    base_config = {
        "apply_types": ["enum"],
    }

    @override
    def __init__(self, *, keys: list[str] = None, **kwargs):
        super().__init__(keys=keys, **kwargs)

    @property
    def keys(self):
        return self.rule_info.get(["keys"], [])

    @override
    async def validate(self, value: str, *args, **kwargs) -> str:
        """
        Validate that the value is within the set of predefined choices.

        Args:
            value (str): The value to validate.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The validated value.

        Raises:
            ValueError: If the value is not in the set of choices.
        """
        if not value in self.keys:
            raise ValueError(f"{value} is not in chocies {self.keys}")
        return value

    @override
    async def fix_field(self, value, *args, **kwargs):
        """
        Suggest a fix for a value that is not within the set of predefined choices.

        Args:
            value (str): The value to suggest a fix for.

        Returns:
            str: The most similar value from the set of predefined choices.
        """
        return choose_most_similar(value, self.keys)
