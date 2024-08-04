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

from functools import singledispatchmethod
from collections import deque
from typing import Any, override

from pydantic import Field

from lion_core.setting import BASE_LION_FIELDS, LN_UNDEFINED
from lion_core.libs import to_dict
from lion_core.abc import MutableRecord
from lion_core.exceptions import LionTypeError, LionValueError
from lion_core.generic.component import Component
from lion_core.generic.pile import Pile
from lion_core.task.utils import get_input_output_fields


class Form(Component, MutableRecord):

    template_name: str = "default_form"

    assignment: str = Field(
        ...,
        description="The objective of the form specifying input/output fields.",
        examples=["input1, input2 -> output"],
    )

    request_fields: list[str] = Field(
        default_factory=list,
        description="Fields required to carry out the objective of the form.",
    )

    requested_fields: list[str] = Field(
        default_factory=list,
        description="Fields requested to be filled by the user.",
    )

    task: Any = Field(
        default_factory=str,
        description="The work to be done by the form, including custom instructions.",
    )

    validation_kwargs: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional validation constraints for the form fields.",
        examples=[{"field": {"config1": "a", "config2": "b"}}],
    )

    @override
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize a new instance of the Form.

        Sets up input and requested fields based on the form's assignment.

        Args:
            **kwargs: Arbitrary keyword arguments for the parent class.
        """
        super().__init__(**kwargs)
        self.request_fields, self.requested_fields = get_input_output_fields(
            self.assignment
        )

        for i in self.request_fields:
            self.append_to_input(i)

        for i in self.request_fields + self.requested_fields:
            if i not in self.all_fields:
                self.add_field(i, value=LN_UNDEFINED)

    @property
    def work_fields(self) -> dict[str, Any]:
        """
        Get the fields relevant to the current task, including input and
        requested fields.

        Returns:
            dict[str, Any]: The fields relevant to the current task.
        """
        dict_ = self.to_dict()
        return {
            k: v
            for k, v in dict_.items()
            if k not in BASE_LION_FIELDS
            and k in self.request_fields + self.requested_fields
        }

    def append_to_request(self, field: str, value: Any = LN_UNDEFINED) -> None:
        """Append a field to the requested fields.

        Adds a new field to the list of requested fields. If the field
        contains commas, it's split into multiple fields.

        Args:
            field: The name of the field(s) to be requested.
            value: The default value for the field.
        """
        if "," in field:
            field = field.split(",")
        if not isinstance(field, list):
            field = [field]

        for i in field:
            i = i.strip()
            if i not in self.all_fields:
                self.add_field(i, value=value)

            if i not in self.requested_fields:
                self.requested_fields.append(i)
                self.validation_kwargs[i] = getattr(
                    self.all_fields[i], "validation_kwargs", {}
                )

    def append_to_input(self, field: str, value: Any = LN_UNDEFINED) -> None:
        """Append a field to the input fields.

        Adds a new field to the list of input fields. If the field
        contains commas, it's split into multiple fields.

        Args:
            field: The name of the field(s) to be added to input.
            value: The default value for the field.
        """
        if "," in field:
            field = field.split(",")
        if not isinstance(field, list):
            field = [field]

        for i in field:
            i = i.strip()
            if i not in self.all_fields:
                self.add_field(i, value=value)

            if i not in self.requested_fields:
                self.request_fields.append(i)
                self.validation_kwargs[i] = getattr(
                    self.all_fields[i], "validation_kwargs", {}
                )

    @singledispatchmethod
    def fill(self, input_: Any, *, strict=False, update=False, **kwargs):
        raise LionTypeError(f"Cannot fill form with type {type(input_)}")

    @fill.register(dict)
    def _(self, input_: dict, *, strict=False, update=False, **kwargs):
        if strict and (
            self.is_filled or any(i not in self.work_fields for i in input_.keys())
        ):
            raise LionValueError("Form is filled, cannot be worked on again")

        fields = {**input_, **kwargs}
        if update:
            for k, v in fields:
                if k in self.work_fields and v is not None:
                    setattr(self, k, v)
        else:
            for k, v in fields:
                if (
                    k in self.work_fields
                    and v is not None
                    and getattr(self, k, None) is None
                ):
                    setattr(self, k, v)

    @fill.register(MutableRecord)
    def _(self, input_: MutableRecord, *, strict=False, update=False, **kwargs):
        fields: dict = {**input_.work_fields, **kwargs}
        return self.fill(fields, strict=strict, update=update)

    @fill.register(str)
    def _(
        self,
        input_: str,
        *,
        strict=False,
        update=False,
        str_type="json",
        parser=None,
        **kwargs,
    ):
        try:
            fields = {**to_dict(input_, str_type=str_type, parser=parser), **kwargs}
            return self.fill(fields, strict=strict, update=update)
        except ValueError as e:
            if len(str(e)) > 50:
                e = str(e)[:50] + "..."
            raise LionValueError(f"Unable to fill form with string input: {e}")

    @fill.register(deque)
    @fill.register(set)
    @fill.register(tuple)
    @fill.register(Pile)
    @fill.register(list)
    def _(self, input_, *, strict=False, update=True, **kwargs):
        input_ = list(input_) if not isinstance(input_, list) else input_
        for i in input_:
            self.fill(i, strict=strict, update=update, **kwargs)

    @property
    def instruction_dict(self) -> dict:
        return {
            "context": self.instruction_context,
            "instruction": self.instruction_prompt,
            "requested_fields": self.instruction_requested_fields,
        }

    @property
    def instruction_context(self) -> str:
        """
        Generate a description of the form's input fields.

        Args:
            form: Form to generate context for.

        Returns:
            String with descriptions of input fields.
        """
        return "".join(
            f"""
        ## input: {i}:
        - description: {getattr(self.all_fields[i], "description", "N/A")}
        - value: {str(self.__getattribute__(self.request_fields[idx]))}
        """
            for idx, i in enumerate(self.request_fields)
        )

    @property
    def instruction_prompt(self) -> str:
        """
        Generate a task instruction prompt for a form.

        Args:
            form: Form to generate prompt for.

        Returns:
            Formatted instruction prompt string.
        """
        return f"""
        ## Task Instructions
        Please follow prompts to complete the task:
        1. Your task is: {self.task}
        2. The provided input fields are: {', '.join(self.request_fields)}
        3. The requested output fields are: {', '.join(self.requested_fields)}
        4. Provide your response in the specified JSON format.
        """

    @property
    def instruction_requested_fields(self) -> dict[str, str]:
        """
        Get descriptions of a form's requested fields.

        Args:
            form: Form to get requested fields from.

        Returns:
            Dictionary mapping field names to descriptions.
        """
        return {
            field: self.all_fields[field].description or "N/A"
            for field in self.requested_fields
        }

    @property
    def is_workable(self):
        try:
            self.check_is_workable()
            return True
        except LionValueError:
            return False

    def check_is_workable(self, strict=True):
        if strict and self.is_filled:
            raise LionValueError("Form is already filled, cannot be worked on again")
        for field in self.request_fields:
            if getattr(self, field, LN_UNDEFINED) is LN_UNDEFINED:
                raise LionValueError(f"Required field {field} is not provided")
        return True

    @property
    def is_filled(self):
        return all(
            getattr(self, field, LN_UNDEFINED) not in [None, LN_UNDEFINED]
            for field in self.work_fields
        )

    @singledispatchmethod
    def _get_field_annotation(self, field: Any) -> dict[str, Any]:
        return {}

    # use list comprehension
    @_get_field_annotation.register(str)
    def _(self, field: str) -> dict[str, Any]:
        dict_ = {field: self.all_fields[field].annotation}
        for k, v in dict_.items():
            if "|" in str(v):
                v = str(v)
                v = v.split("|")
                dict_[k] = [str(i).lower().strip() for i in v]
            else:
                dict_[k] = [v.__name__] if v else None
        return dict_

    @_get_field_annotation.register(deque)
    @_get_field_annotation.register(set)
    @_get_field_annotation.register(list)
    @_get_field_annotation.register(tuple)
    def _(self, field: list | tuple) -> dict[str, Any]:
        dict_ = {}
        for f in field:
            dict_.update(self._get_field_annotation(f))
        return dict_


# File: lion_core/form/form.py
