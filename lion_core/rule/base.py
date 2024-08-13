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

from abc import abstractmethod
from typing import Any, Callable
from typing_extensions import override


from lion_core.abc import Condition, Observable, Temporal, Action
from lion_core.exceptions import LionOperationError
from lion_core.sys_utils import SysUtil
from lion_core.libs import ucall
from lion_core.generic.note import Note
from lion_core.form.base import BaseForm


class Rule(Condition, Action, Observable, Temporal):

    base_config = {}

    def __init__(
        self,
        fix: bool = False,
        apply_types: list[str] | None = None,
        exclude_types: list[str] | None = None,
        apply_fields: list[str] = None,
        exclude_fields: list[str] = None,
        **kwargs,  # validation_kwargs
    ):
        super().__init__()
        self.ln_id = SysUtil.id()
        self.timestamp = SysUtil.time(type_="timestamp")
        config = {**self.base_config, **kwargs}
        self.rule_info = Note(
            **{
                "fix": fix,
                "apply_types": apply_types or config.pop("apply_types", []),
                "exclude_types": exclude_types or [],
                "apply_fields": apply_fields or [],
                "exclude_fields": exclude_fields or [],
                **config,
            }
        )

    @property
    def validation_kwargs(self) -> dict:
        return {
            k: v
            for k, v in self.rule_info.to_dict().items()
            if k
            not in [
                "fix",
                "apply_types",
                "exclude_types",
                "apply_fields",
                "exclude_fields",
            ]
        }

    # must only return True or False
    @override
    async def apply(
        self,
        field: str,
        value: Any,
        form: BaseForm,
        *args,
        apply_fields: list[str] = None,
        exclude_fields: list[str] = None,
        annotation: list | str = None,
        check_func: (
            Callable | Any
        ) = None,  # takes priority over annotation and self.rule_condition
        **kwargs,  # additional kwargs for custom check func or self.rule_condition
    ) -> bool:
        """
        Apply the rule to a specific field.

        Args:
            field: The field to apply the rule to.
            value: The value of the field.
            form: The form containing the field.
            apply_fields: Fields to apply the rule to (overrides instance setting).
            exclude_fields: Fields to exclude from the rule (overrides instance setting).
            annotation: Field annotation for type-based rule application.
            check_func: Custom function for condition checking.
            **kwargs: Additional arguments for the check function.

        Returns:
            bool: True if the rule should be applied, False otherwise.

        Raises:
            LionOperationError: If an invalid check function is provided.
        """
        if field not in form.work_fields:
            return False

        apply_fields: list = apply_fields or self.rule_info.get(["apply_fields"], [])
        exclude_fields: list = exclude_fields or self.rule_info.get(
            ["exclude_fields"], []
        )

        if exclude_fields and field in exclude_fields:
            return False
        if apply_fields and field in apply_fields:
            return True

        if self.rule_condition != Rule.rule_condition:
            check_func = check_func or self.rule_condition
            if not isinstance(check_func, Callable):
                raise LionOperationError("Invalid check function provided")
            try:
                a = await ucall(check_func, field, value, form, *args, **kwargs)
                if isinstance(a, bool):
                    return a
            except Exception:
                return False

        # if not in custom fields, nor using custom validation condition
        # we will resort to use field annotation
        annotation = annotation or form._get_field_annotation(field)
        if isinstance(annotation, dict) and field in annotation:
            annotation = annotation[field]
        annotation = [annotation] if isinstance(annotation, str) else annotation

        if annotation and len(annotation) > 0:
            for i in annotation:
                if i in self.rule_info.get(
                    ["apply_types"], []
                ) and i not in self.rule_info.get(["exclude_types"], []):
                    return True
            return False

        return False

    @override
    async def invoke(self, value) -> Any:
        """
        Invoke the rule on a field value.

        This method attempts to validate the value and fix it if necessary.

        Args:
            field: The field being processed.
            value: The value to validate or fix.
            form: The form containing the field.

        Returns:
            Any: The validated or fixed value.

        Raises:
            LionOperationError: If validation or fixing fails.
        """
        try:
            return await self.validate(value, **self.validation_kwargs)

        except Exception as e1:
            if self["fix"]:
                try:
                    a = await self.perform_fix(value, **self.validation_kwargs)
                    return a
                except Exception as e2:
                    raise LionOperationError("failed to fix field") from e2
            raise LionOperationError("failed to validate field") from e1

    # must only return True or False
    async def rule_condition(
        self,
        field: str,
        value: Any,
        form: BaseForm,
        *args,
        **kwargs,
    ) -> bool:
        """
        Default rule condition method.

        This method can be optionally overridden in subclasses to implement
        specific condition checking logic.

        Returns:
            bool: Always returns False in the base implementation.
        """
        return False

    # can return corrected value, raise error, or return None (suppress)
    async def perform_fix(
        self,
        value: Any,
        *args,
        suppress=False,
        **kwargs,
    ) -> Any:
        try:
            return await self.fix_field(value, *args, **kwargs)
        except Exception as e:
            if suppress:
                return None
            raise LionOperationError("Failed to fix field") from e

    # must return corrected value or raise error
    async def fix_field(
        self,
        value: Any,
        *args,
        **kwargs,
    ):
        return value

    # must return correct value as is or raise error
    @abstractmethod
    async def validate(
        self,
        value: Any,
        *args,
        **kwargs,
    ) -> Any:
        """
        either return a correct value, or raise error,
        if raise error will attempt to fix it if fix is True
        """
        pass


# File: lion_core/rule/base.py
