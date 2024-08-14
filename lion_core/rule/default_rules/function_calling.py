"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing_extensions import override
from lion_core.libs import fuzzy_parse_json, to_dict, to_list
from lion_core.exceptions import LionOperationError

from lion_core.rule.default_rules.mapping import MappingRule


class FunctionCallingRule(MappingRule):
    """
    Rule for validating and fixing action requests.

    Inherits from `MappingRule` and provides specific validation and fix logic
    for action requests.

    Attributes:
        discard (bool): Indicates whether to discard invalid action requests.
    """

    @property
    def discard(self):
        return self.info.get(["discard"], True)

    @override
    async def validate(self, value):
        """
        Validates the action request.

        Args:
            value (Any): The value of the action request.

        Returns:
            Any: The validated action request.

        Raises:
            ActionError: If the action request is invalid.
        """

        try:
            return await super().validate(value)
        except LionOperationError as e:
            raise LionOperationError(f"Invalid action request: ") from e

    # we do not attempt to fix the keys
    # because if the keys are wrong, action is not safe to operate, and is meaningless
    @override
    async def fix_value(self, value):
        corrected = []
        if isinstance(value, str):
            value = fuzzy_parse_json(value)

        try:
            value = to_list(value, flatten=True, dropna=True)
            for i in value:
                i = to_dict(i, **self.validation_kwargs)
                if list(i.keys()) >= ["function", "arguments"]:
                    corrected.append(i)
                elif not self.discard:
                    raise LionOperationError(f"Invalid action request: {i}")
        except Exception as e:
            raise LionOperationError(f"Invalid action field: ") from e

        return corrected
