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

from lion_core.abc import Condition, Observable, Temporal, Action
from lion_core.exceptions import LionOperationError
from lion_core.sys_utils import SysUtil
from lion_core.libs import ucall
from lion_core.record.form import Form


class Rule(Condition, Action, Observable, Temporal):

    fix: bool = False
    validation_kwargs: dict = {}
    apply_types: list[str] | None = None
    exclude_types: list[str] | None = None

    def __init__(
        self,
        fix=None,
        apply_types=None,
        exclude_types=None,
        apply_fields=None,
        exclude_fields=None,
        **kwargs,
    ) -> None:
        """
        Initialize a Rule instance.

        Args:
            fix: Whether to attempt fixing invalid values.
            apply_types: Types of fields to apply the rule to.
            exclude_types: Types of fields to exclude from the rule.
            apply_fields: Specific fields to apply the rule to.
            exclude_fields: Specific fields to exclude from the rule.
            **kwargs: Additional keyword arguments for validation.
        """
        self.ln_id = SysUtil.id()
        self.timestamp = SysUtil.time(type_="timestamp")
        self._is_active = False
        self.accepted_fields = apply_fields or []
        self.exclude_fields = exclude_fields or []
        if fix:
            self.fix = fix
        if apply_types:
            self.apply_types = apply_types
        if exclude_types:
            self.exclude_types = exclude_types
        if kwargs:
            self.validation_kwargs = {**self.validation_kwargs, **kwargs}

    async def apply(
        self,
        field: str,
        value: Any,
        form: Form,
        *args,
        apply_fields: list[str] = None,
        exclude_fields: list[str] = None,
        annotation: list | str = None,
        check_func: Callable = None,  # takes priority over annotation and self.rule_condition
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

        apply_fields = apply_fields or self.accepted_fields
        exclude_fields = exclude_fields or self.exclude_fields

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
                if i in self.apply_types and i not in self.exclude_types:
                    return True
            return False

        return False

    async def invoke(self, field: str, value: Any, form: Any) -> Any:
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
            if self.fix:
                try:
                    a = await self.perform_fix(value, **self.validation_kwargs)
                    return a
                except Exception as e2:
                    raise LionOperationError("failed to fix field") from e2
            raise LionOperationError("failed to validate field") from e1

    async def rule_condition(
        self, field: str, value: Any, form: Form, *args, **kwargs
    ) -> bool:
        """
        Default rule condition method.

        This method can be optionally overridden in subclasses to implement
        specific condition checking logic.

        Returns:
            bool: Always returns False in the base implementation.
        """
        return False

    async def perform_fix(self, value: Any, *args, **kwargs) -> Any:
        """
        Perform a fix on an invalid value.

        This method should be overridden in subclasses to implement
        specific fixing logic.

        Args:
            value: The value to fix.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The fixed value (returns the original value by default).
        """
        return value

    @abstractmethod
    async def validate(self, value: Any, *args, **kwargs) -> Any:
        """
        either return a correct value, or raise error,
        if raise error will attempt to fix it if fix is True
        """
        pass


# File: lion_core/rule/base.py
