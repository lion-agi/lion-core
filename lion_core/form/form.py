"""
Specialized implementation of BaseForm for dynamic form management.

This module defines the Form class, which manages form fields dynamically
based on specified assignments. It supports initialization and management
of input and requested fields.
"""

from typing import Any

from lion_core.setting import BASE_LION_FIELDS
from lion_core.sys_util import LN_UNDEFINED
from .base import BaseForm
from .util import get_input_output_fields


class Form(BaseForm):
    """
    A specialized implementation of BaseForm for dynamic form management.

    This class manages form fields dynamically based on specified
    assignments. It supports initialization and management of input and
    requested fields.

    Attributes:
        input_fields: Fields required for the form's objective.
        requested_fields: Fields to be filled by the user.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize a new instance of the Form.

        Sets up input and requested fields based on the form's assignment.

        Args:
            **kwargs: Arbitrary keyword arguments for the parent class.
        """
        super().__init__(**kwargs)
        self.input_fields, self.requested_fields = get_input_output_fields(
            self.assignment
        )

        for i in self.input_fields:
            self.append_to_input(i)

        for i in self.input_fields + self.requested_fields:
            if i not in self.all_fields:
                self.add_field(i, value=LN_UNDEFINED)

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
                self.input_fields.append(i)
                self.validation_kwargs[i] = getattr(
                    self.all_fields[i], "validation_kwargs", {}
                )

    @property
    def work_fields(self) -> dict[str, Any]:
        """Retrieve fields relevant to the current task.

        Returns a dictionary of fields that are relevant to the current
        task, excluding BASE_LION_FIELD and including only input and
        requested fields.

        Returns:
            A dictionary of fields relevant to the current task.
        """
        dict_ = self.model_dump()
        return {
            k: v
            for k, v in dict_.items()
            if (k not in BASE_LION_FIELDS)
            and (k in self.input_fields + self.requested_fields)
        }

    @property
    def instruction_dict(self) -> str:
        from .form_manager import ReportManager

        return ReportManager.form_instruction_dict(self)


# File: lion_core/form/form.py
