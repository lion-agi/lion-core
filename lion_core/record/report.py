"""Extends BaseForm to handle a collection of Form instances.

This module defines the Report class, which manages multiple Form instances
based on specific assignments, ensuring proper configuration and
synchronization of fields across forms.
"""

from typing import Any, Type
from pydantic import Field

from lion_core.generic.pile import Pile, pile
from lion_core.setting import LN_UNDEFINED
from lion_core.generic import Component
from lion_core.abc import MutableRecord

from .util import get_input_output_fields
from .form import Form


class Report(Component, MutableRecord):
    """Extends BaseForm to handle a collection of Form instances.

    This class manages a pile of forms based on specific assignments,
    ensuring synchronization and proper configuration across all forms.

    Attributes:
        forms: A pile of forms related to the report.
        form_assignments: List of assignments for the report's forms.
        form_template: The template class for the forms in the report.
    """

    forms: Pile[Form] = Field(
        None,
        description="A pile of forms related to the report.",
    )

    form_assignments: list = Field(
        [],
        description="assignment for the report",
        examples=[["a, b -> c", "a -> e", "b -> f", "c -> g", "e, f, g -> h"]],
    )

    form_template: Type[Form] = Field(
        Form, description="The template for the forms in the report."
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the Report with forms based on provided assignments.

        Creates forms dynamically from provided assignments and synchronizes
        fields between the report and its forms.

        Args:
            **kwargs: Arbitrary keyword arguments for the parent class.
        """
        super().__init__(**kwargs)
        self.input_fields, self.requested_fields = get_input_output_fields(
            self.assignment
        )

        # if assignments is not provided, set it to report assignment
        if self.form_assignments == []:
            self.form_assignments.append(self.assignment)

        # create forms
        self.forms = pile(
            [self.form_template(assignment=i) for i in self.form_assignments],
            MutableRecord,
        )

        # Add undeclared fields to report with None values
        for v in self.forms:
            for _field in list(v.work_fields.keys()):
                if _field not in self.all_fields:
                    field_obj = v.all_fields[_field]
                    self.add_field(_field, value=LN_UNDEFINED, field_obj=field_obj)

        # Synchronize fields between report and forms
        for k, v in self.all_fields.items():
            if getattr(self, k, LN_UNDEFINED) not in [LN_UNDEFINED, None]:
                for _form in self.forms:
                    if k in _form.work_fields:
                        _form.fill(**{k: getattr(self, k)})

    @property
    def work_fields(self) -> dict[str, Any]:
        all_fields = {}
        for form in self.forms:
            for k, v in form.work_fields.items():
                if k not in all_fields:
                    all_fields[k] = v
        return all_fields


# File lion_core/form/report.py
