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

"""Base form class for the lion-core library."""

from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_core import PydanticUndefined

from lion_core.abc import MutableRecord
from lion_core.exceptions import LionValueError
from lion_core.generic.component import Component
from lion_core.setting import LN_UNDEFINED
from lion_core.form.utils import ERR_MAP


class BaseForm(Component, MutableRecord):
    """
    Base form class providing core functionality for form handling.

    Serves as a foundation for creating custom forms in the lion-core library.
    Includes methods for managing output fields, handling results, and
    field annotations.

    This class focuses on output fields, which are fields that are outputted
    and presented. Output fields can include all, part, or none of the
    request fields and can be conditionally modified by the process if not strict.
    """

    assignment: str | None = Field(
        default=None,
        description="The objective of the task.",
        examples=["input1, input2 -> output"],
    )

    template_name: str = Field(
        default="default_form", description="Name of the form template"
    )
    output_fields: list[str] = Field(
        default_factory=list,
        description=(
            "Fields that are outputted and presented by the form. "
            "These can include all, part, or none of the request fields."
        ),
    )
    none_as_valid_value: bool = Field(
        default=False, description="Indicate whether to treat None as a valid value."
    )

    has_processed: bool = Field(
        default=False,
        description="Indicates if the task has been processed.",
        exclude=True,
    )

    def check_is_completed(
        self,
        handle_how: Literal["raise", "return_missing"] = "raise",
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

        non_complete_request = []
        invalid_values = [LN_UNDEFINED, PydanticUndefined]
        if not self.none_as_valid_value:
            invalid_values.append(None)

        for i in self.required_fields:
            if getattr(self, i) in invalid_values:
                non_complete_request.append(i)

        if non_complete_request:
            if handle_how == "raise":
                raise ERR_MAP["assignment", "incomplete_request"](non_complete_request)
            elif handle_how == "return_missing":
                return non_complete_request
        else:
            self.has_processed = True

    def is_completed(self) -> bool:
        try:
            self.check_is_completed(handle_how="raise")
            return True
        except Exception:
            return False

    @field_validator("output_fields", mode="before")
    @classmethod
    def _validate_output(cls, value):
        if isinstance(value, str):
            return [value]
        if isinstance(value, list) and all(
            [i for i in value if isinstance(i, str)],
        ):
            return value
        if not value:
            return []
        raise LionValueError("Invalid output fields.")

    @property
    def work_fields(self) -> list[str]:
        return self.output_fields

    @property
    def work_dict(self) -> dict[str, Any]:
        """Return a dictionary of all work fields and their values."""
        return {i: getattr(self, i, LN_UNDEFINED) for i in self.work_fields}

    @property
    def required_fields(self) -> list[str]:
        """Return the list of required fields for the form."""
        return self.output_fields

    @property
    def required_dict(self) -> dict[str, Any]:
        """Return a dictionary of all work fields and their values."""
        return {i: getattr(self, i, LN_UNDEFINED) for i in self.required_fields}

    def get_results(
        self,
        suppress: bool = False,
        valid_only: bool = False,
    ) -> dict[str, Any]:
        """
        Retrieve the results of the form.

        Args:
            suppress: If True, suppress errors for missing fields.
            valid_only: If True, return only valid (non-empty) results.

        Returns:
            A dictionary of field names and their values.

        Raises:
            ValueError: If a required field is missing and suppress is False.
        """
        result = {}
        out_fields = self.output_fields or getattr(self, "request_fields", [])

        for i in out_fields:
            if i not in self.all_fields:
                if not suppress:
                    raise ERR_MAP["field", "missing"](i)
            else:
                result[i] = getattr(self, i, LN_UNDEFINED)

        # add a validator for output fields

        if valid_only:
            invalid_values = [
                LN_UNDEFINED,
                PydanticUndefined,
            ]
            if not self.none_as_valid_value:
                invalid_values.append(None)
            result = {k: v for k, v in result.items() if v not in invalid_values}
        return result

    @property
    def display_dict(self) -> dict[str, Any]:
        return self.required_dict


__all__ = ["BaseForm"]
