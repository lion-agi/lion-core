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

"""Form class extending BaseTaskForm with additional functionality."""

import inspect

import re
from typing import Any, Literal, Type, override

from pydantic import Field, model_validator, ConfigDict
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from lion_core.setting import LN_UNDEFINED
from lion_core.sys_utils import SysUtil
from lion_core.exceptions import LionValueError
from lion_core.generic.note import Note
from lion_core.form.base import BaseForm
from lion_core.form.utils import get_input_output_fields, ERR_MAP, RESTRICTED_FIELDS


class Form(BaseForm):
    """
    Base task form class extending BaseForm with task-specific functionality.

    Introduces concepts of input fields, request fields, and task-related
    attributes for a comprehensive task-based form framework.

    Key concepts:
    - input_fields: Fields needed to obtain the request fields.
    - request_fields: Fields to be filled by an intelligent process.
    - output_fields: Fields for presentation, may include all, some, or no
      request fields. Can be conditionally modified if not strict.
    """

    strict: bool = Field(
        default=False,
        description="If True, form fields and assignment are immutable.",
        frozen=True,
    )
    guidance: str | dict[str, Any] | None = Field(
        default=None,
        description="High-level task guidance, optimizable by AI.",
    )
    input_fields: list[str] = Field(
        default_factory=list,
        description="Fields required to obtain the requested fields.",
    )
    request_fields: list[str] = Field(
        default_factory=list,
        description="Fields to be filled by an intelligent process.",
    )
    task: Any = Field(
        default_factory=str,
        description="Work to be done, including custom instructions.",
    )
    task_description: str | None = Field(
        default_factory=str,
        description="Detailed description of the task",
    )
    init_input_kwargs: dict[str, Any] = Field(default_factory=dict, exclude=True)
    has_processed: bool = Field(
        default=False,
        description="Indicates if the task has been processed.",
        exclude=True,
    )
    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        populate_by_name=True,
    )

    def to_dict(self, *, valid_only=False):
        _dict = super().to_dict()
        if not valid_only:
            return _dict

        disallow_values = [LN_UNDEFINED, PydanticUndefined, None]
        return {k: v for k, v in _dict.items() if v not in disallow_values}

    @override
    @property
    def work_fields(self) -> list[str]:
        """Return a list of all fields involved in the task."""
        return self.input_fields + self.request_fields

    @override
    @property
    def required_fields(self) -> list[str]:
        """Return a list of all unique required fields."""
        return list(set(self.input_fields + self.request_fields + self.output_fields))

    @property
    def validation_kwargs(self):
        return {
            i: self.field_getattr(i, "validation_kwargs", {}) for i in self.work_fields
        }

    @property
    def instruction_dict(self) -> dict[str, Any]:
        """Return a dictionary with task instruction information."""
        return {
            "context": self.instruction_context,
            "instruction": self.instruction_prompt,
            "request_fields": self.instruction_request_fields,
        }

    @property
    def instruction_context(self) -> str:
        """Generate a description of the form's input fields."""
        return "".join(
            f"""
## input: {i}:
- description: {getattr(self.all_fields[i], "description", "N/A")}
- value: {str(getattr(self, self.request_fields[idx]))}
- examples: {getattr(self.all_fields[i], "examples", "N/A")}
"""
            for idx, i in enumerate(self.request_fields)
        )

    @property
    def instruction_prompt(self) -> str:
        """Generate a task instruction prompt for the form."""
        return f"""
## Task Instructions
Please follow prompts to complete the task:
1. Your task is: {self.task}
2. The provided input fields are: {', '.join(self.request_fields)}
3. The requested output fields are: {', '.join(self.request_fields)}
4. Provide your response in the specified JSON format.
"""

    @property
    def instruction_request_fields(self) -> dict[str, str]:
        """Get descriptions of the form's requested fields."""
        return {
            field: self.all_fields[field].description or "N/A"
            for field in self.request_fields
        }

    @override
    def update_field(
        self,
        field_name: str,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo | Any = LN_UNDEFINED,
        **kwargs: Any,
    ) -> None:
        """
        Update a field in the form.

        Extends the base update_field method to also update
        the init_input_kwargs dictionary.
        """
        super().update_field(
            field_name=field_name,
            value=value,
            annotation=annotation,
            field_obj=field_obj,
            **kwargs,
        )
        self._fill_init_input_kwargs(field_name)

    @override
    def __setattr__(self, field_name: str, value: Any) -> None:
        """
        Set an attribute of the form.

        Extends the base __setattr__ method to enforce strictness
        and update the init_input_kwargs dictionary.
        """
        if self.strict and field_name in RESTRICTED_FIELDS:
            raise AttributeError(f"{field_name} should not be modified after init")

        super().__setattr__(field_name, value)
        self._fill_init_input_kwargs(field_name)

    def _fill_init_input_kwargs(self, field_name):
        if field_name in self.input_fields:
            self.init_input_kwargs[field_name] = getattr(self, field_name)

    def check_is_completed(
        self, handle_how: Literal["raise", "return_missing"] = "raise"
    ) -> list[str] | None:
        """
        Check if all required fields are completed.

        Args:
            handle_how: How to handle incomplete fields.

        Returns:
            List of incomplete fields if handle_how is "return_missing",
            None otherwise.

        Raises:
            ValueError: If required fields are incomplete and handle_how
                is "raise".
        """
        if self.strict and self.has_processed:
            return

        non_complete_request = []
        invalid_values = [LN_UNDEFINED, PydanticUndefined]
        if not self.none_as_valid_value:
            invalid_values.append(None)

        for i in self.required_fields:
            if getattr(self, i) in invalid_values:
                non_complete_request.append(i)

        if non_complete_request:
            if handle_how == "raise":
                raise ERR_MAP["incomplete_request"](non_complete_request)
            elif handle_how == "return_missing":
                return non_complete_request
        else:
            self.has_processed = True

    def check_is_workable(
        self, handle_how: Literal["raise", "return_missing"] = "raise"
    ) -> list[str] | None:
        """
        Check if all input fields are filled and the form is workable.

        Args:
            handle_how: How to handle missing inputs.

        Returns:
            List of missing inputs if handle_how is "return_missing",
            None otherwise.

        Raises:
            ValueError: If input fields are missing and handle_how is "raise".
        """
        if self.has_processed:
            raise ERR_MAP["task_already_processed"]

        missing_inputs = []
        invalid_values = [LN_UNDEFINED, PydanticUndefined]
        if not self.none_as_valid_value:
            invalid_values.append(None)

        for i in self.input_fields:
            if getattr(self, i) in invalid_values:
                missing_inputs.append(i)

        if missing_inputs:
            if handle_how == "raise":
                raise ERR_MAP["incomplete_input"](missing_inputs)
            elif handle_how == "return_missing":
                return missing_inputs

    @classmethod
    def from_dict(cls, data: dict):
        for i in ["input_fields", "request_fields", "task"]:
            if i in data:
                data.pop(i)
        return cls(**data)

    @model_validator(mode="before")
    @classmethod
    def check_input_output_list_omitted(cls, data: Any) -> dict[str, Any]:
        """
        Validate the input data before model creation.

        Args:
            data: Input data for model creation.

        Returns:
            Validated and processed input data.

        Raises:
            ValueError: If input data is invalid.
        """

        if isinstance(data, Note):
            data = data.to_dict()

        if not isinstance(data, dict):
            raise ERR_MAP["not_dict"]

        if not data.get("assignment", None):
            raise ERR_MAP["no_assignment"]

        if "input_fields" in data or "request_fields" in data:
            raise ERR_MAP["explicit_input_request"]

        if "task" in data:
            raise ERR_MAP["explicit_task"]

        input_fields, request_fields = get_input_output_fields(data.get("assignment"))

        if not input_fields or input_fields == [""]:
            raise ERR_MAP["invalid_input"]
        elif not request_fields or request_fields == [""]:
            raise ERR_MAP["missing_output"]

        data["input_fields"] = input_fields
        data["request_fields"] = request_fields
        data["output_fields"] = data.get("output_fields", request_fields)
        data["init_input_kwargs"] = {}
        data["strict_assignment"] = data.get("strict_assignment", False)

        for in_ in data["input_fields"]:
            data["init_input_kwargs"][in_] = (
                data.pop(in_, LN_UNDEFINED)
                if in_ not in cls.model_fields
                else data.get(in_, None)
            )
        return data

    @model_validator(mode="after")
    def check_input_output_fields(self) -> "Form":
        """
        Validate and process input and output fields after model creation.

        Returns:
            The validated Form instance.
        """
        for i in self.input_fields:
            if i in self.model_fields:
                self.init_input_kwargs[i] = getattr(self, i)
            else:
                self.add_field(
                    field_name=i, value=self.init_input_kwargs.get(i, LN_UNDEFINED)
                )

        for i in self.request_fields:
            if i not in self.all_fields:
                self.add_field(field_name=i)

        return self

    def is_completed(self) -> bool:
        try:
            self.check_is_completed(handle_how="raise")
            return True
        except Exception:
            return False

    def is_workable(self) -> bool:
        try:
            self.check_is_workable(handle_how="raise")
            return True
        except Exception:
            return False

    def fill_input_fields(self, form: BaseForm | Any = None, **value_kwargs):
        if form is not None and not isinstance(form, BaseForm):
            raise LionValueError("Invalid form for fill. Should be a instance of Form.")
        for i in self.input_fields:
            if self.none_as_valid_value:
                if getattr(self, i) is not LN_UNDEFINED:
                    continue
                value = value_kwargs.get(i, LN_UNDEFINED)
                if value is LN_UNDEFINED:
                    value = SysUtil.copy(getattr(form, i, LN_UNDEFINED))
                if value is not LN_UNDEFINED:
                    setattr(self, i, value)
            else:
                if getattr(self, i) in [LN_UNDEFINED, None]:
                    value = value_kwargs.get(i)
                    if value in [LN_UNDEFINED, None]:
                        value = SysUtil.copy(getattr(form, i, LN_UNDEFINED))
                    if value not in [LN_UNDEFINED, None]:
                        setattr(self, i, value)

    def fill_request_fields(self, form: BaseForm = None, **value_kwargs):
        if form is not None and not isinstance(form, BaseForm):
            raise ERR_MAP["not_form_instance"]

        for i in self.request_fields:
            if self.none_as_valid_value:
                if getattr(self, i) is not LN_UNDEFINED:
                    continue
                value = value_kwargs.get(i, LN_UNDEFINED)
                if value is LN_UNDEFINED:
                    value = SysUtil.copy(getattr(form, i, LN_UNDEFINED))
                if value is not LN_UNDEFINED:
                    setattr(self, i, value)
            else:
                if getattr(self, i) in [LN_UNDEFINED, None]:
                    value = value_kwargs.get(i)
                    if value in [LN_UNDEFINED, None]:
                        value = SysUtil.copy(getattr(form, i, LN_UNDEFINED))
                    if value not in [LN_UNDEFINED, None]:
                        setattr(self, i, value)

    @classmethod
    def from_form(
        cls,
        form: BaseForm | Type[BaseForm],
        guidance: str | dict[str, Any] | None = None,
        assignment: str | None = None,
        strict: bool = None,
        task_description: str | None = None,
        fill_inputs: bool | None = True,
        none_as_valid_value: bool | None = False,
        **input_value_kwargs,
    ):

        if inspect.isclass(form):
            if not issubclass(form, BaseForm):
                raise ERR_MAP["not_form_class"]
            form_fields = form.model_fields
        else:
            if not isinstance(form, BaseForm):
                raise ERR_MAP["not_form_instance"]
            form_fields = form.all_fields

        obj = cls(
            guidance=guidance or getattr(form, "guidance", None),
            assignment=assignment or form.assignment,
            task_description=task_description,
            none_as_valid_value=none_as_valid_value,
            strict=(
                strict if isinstance(strict, bool) else getattr(form, "strict", False)
            ),
            output_fields=form.output_fields,
        )

        for i in obj.work_dict.keys():
            if i not in form_fields:
                raise ERR_MAP["invalid_assignment"](i)
            obj.update_field(i, field_obj=form_fields[i])
            if not none_as_valid_value and getattr(obj, i) is None:
                setattr(obj, i, LN_UNDEFINED)

        if fill_inputs:
            if inspect.isclass(form):
                obj.fill_input_fields(**input_value_kwargs)
            else:
                obj.fill_input_fields(form=form, **input_value_kwargs)

        return obj

    def remove_request_from_output(self):
        for i in self.request_fields:
            if i in self.output_fields:
                self.output_fields.remove(i)

    def _append_to_one(
        self,
        field_name: Any,
        field_type: Literal["input", "output", "request"],
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo | Any = LN_UNDEFINED,
        **kwargs,
    ):
        _f = lambda x: [i.strip() for i in x.split(",") if i]
        if not (a := _f(field_name)) or len(a) > 1:
            raise LionValueError(
                "Cannot append more than one field at a time, a field's name cannot contain commas."
            )

        config = {
            "field_name": field_name,
            "value": value,
            "annotation": annotation,
            "field_obj": field_obj,
            **kwargs,
        }

        if self.strict:
            raise LionValueError("Cannot modify a strict form.")

        match field_type:
            case "input":
                if field_name not in self.input_fields:
                    self.input_fields.append(field_name)
                if field_name not in self.assignment:
                    self.assignment = f"{field_name}, " + self.assignment

            case "request":
                if field_name not in self.request_fields:
                    self.request_fields.append(field_name)
                    config.pop("value")
                if field_name not in self.assignment:
                    self.assignment += f", {field_name}"

            case "output":
                if field_name not in self.output_fields:
                    self.output_fields.append(field_name)

            case _:
                raise LionValueError(f"Invalid field type {field_type}")

        self.update_field(**config)

    def append_to_input(
        self,
        field_name: str,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo | Any = LN_UNDEFINED,
        **kwargs,
    ) -> None:
        try:
            self._append_to_one(
                field_name=field_name,
                field_type="input",
                value=value,
                annotation=annotation,
                field_obj=field_obj,
                **kwargs,
            )
        except Exception as e:
            raise LionValueError(
                f"Failed to append {field_name} to input fields."
            ) from e

    def append_to_output(
        self,
        field_name: str,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo | Any = LN_UNDEFINED,
        **kwargs,
    ) -> None:

        try:
            self._append_to_one(
                field_name=field_name,
                field_type="output",
                value=value,
                annotation=annotation,
                field_obj=field_obj,
                **kwargs,
            )
        except Exception as e:
            raise LionValueError(
                f"Failed to append {field_name} to output fields."
            ) from e

    def append_to_request(
        self,
        field_name: str,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo | Any = LN_UNDEFINED,
        **kwargs,
    ) -> None:
        if "value" in kwargs:
            raise LionValueError("Cannot provide value to request fields.")
        try:
            self._append_to_one(
                field_name=field_name,
                field_type="request",
                annotation=annotation,
                field_obj=field_obj,
                **kwargs,
            )
        except Exception as e:
            raise LionValueError(
                f"Failed to append {field_name} to request fields."
            ) from e


__all__ = ["Form"]
