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

from typing import Any
from typing_extensions import override
from collections.abc import Mapping
from lion_core.libs import validate_mapping
from lion_core.exceptions import (
    LionOperationError,
    LionValueError,
    LionTypeError,
)

from lion_core.rule.default_rules.choice import ChoiceRule


class MappingRule(ChoiceRule):

    @override
    async def check_value(self, value: dict, /) -> str:
        if not isinstance(value, Mapping):
            raise LionTypeError("Invalid mapping field type.")

        if self.keys:
            if (keys := set(value.keys())) != set(self.keys):
                raise LionValueError(
                    f"Invalid mapping keys. Current keys {[keys]} != {self.keys}"
                )

    @override
    async def fix_value(self, value: Any):

        if isinstance(value, list) and len(value) == 1:
            value = value[0]

        try:
            return validate_mapping(value, self.keys, **self.validation_kwargs)
        except ValueError as e:
            raise LionOperationError(f"Failed to fix {value} into a mapping.") from e
