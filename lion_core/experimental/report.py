"""Extends BaseForm to handle a collection of Form instances.

This module defines the Report class, which manages multiple Form instances
based on specific assignments, ensuring proper configuration and
synchronization of fields across forms.
"""

from functools import singledispatchmethod
from typing import Any, Type
from pydantic import Field
from collections import deque

from lion_core.setting import LN_UNDEFINED
from lion_core.abc import ImmutableRecord, MutableRecord
from lion_core.libs import to_dict
from lion_core.generic.pile import Pile, pile
from lion_core.generic.component import Component
from lion_core.exceptions import LionTypeError, LionValueError


from ..record.utils import get_input_output_fields
from ..record.form import Form


class Report(Component, ImmutableRecord):

    forms: Pile[Form] = Field(
        LN_UNDEFINED,
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
            for _field in v.work_fields.keys():
                if _field not in self.all_fields:
                    field_obj = v.all_fields[_field]
                    self.add_field(_field, value=LN_UNDEFINED, field_obj=field_obj)

        # Synchronize fields between report and forms
        for k, v in self.all_fields.items():
            if getattr(self, k, LN_UNDEFINED) not in [LN_UNDEFINED, None]:
                for _form in self.forms:
                    if k in _form.work_fields:
                        _form.fill({k: getattr(self, k)}, strict=False, update=True)

    @property
    def work_fields(self) -> dict[str, Any]:
        all_fields = {}
        for form in self.forms:
            for k, v in form.work_fields.items():
                if k not in all_fields:
                    all_fields[k] = v
        return all_fields

    @singledispatchmethod
    def fill(self, input_: Any, strict=False, str_type="json", parser=None, **kwargs):
        raise LionTypeError("Fill method not implemented for the provided type.")

    @fill.register(dict)
    def _(self, input_: dict, strict=False, **kwargs):
        if strict and (
            self.is_filled or any(i not in self.work_fields for i in input_.keys())
        ):
            raise LionValueError("Form is already filled, cannot be worked on again")

        fields = {**input_, **kwargs}

        for k, v in fields.items():
            if k in self.work_fields and getattr(self, k, LN_UNDEFINED) is LN_UNDEFINED:
                setattr(self, k, v)

        for form in self.forms:
            for k, v in form.work_fields.items():
                _kwargs = {}
                if (
                    v in [None, LN_UNDEFINED]
                    and (a := getattr(self, k, LN_UNDEFINED)) is not LN_UNDEFINED
                ):
                    _kwargs[k] = a
                form.fill(_kwargs, strict=strict, update=False)

    @fill.register(MutableRecord)
    def _(self, input_: MutableRecord, strict=False, **kwargs):
        return self.fill(input_.work_fields, strict=strict, **kwargs)

    @fill.register(str)
    def _(self, input_: str, strict=False, str_type="json", parser=None, **kwargs):
        return self.fill(
            to_dict(input_, str_type=str_type, parser=parser), strict=strict, **kwargs
        )

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
    def is_workable(self):
        try:
            self.check_is_workable()
            return True
        except LionValueError:
            return False

    def check_is_workable(self):
        if self.is_filled:
            raise LionValueError("Form is already filled, cannot be worked on again")

        for i in self.input_fields:
            if getattr(self, i, LN_UNDEFINED) is LN_UNDEFINED:
                raise LionValueError(f"Required field {i} is not provided")

        # this is the required fields from report's own assignment
        fields = self.input_fields + self.requested_fields

        # if the report's own assignment is not in the forms, return False
        for f in fields:
            if f not in self.work_fields:
                raise LionValueError(f"Field {f} is not in the forms")

        # get all the output fields from all the forms
        outs = []
        for form in self.forms:
            outs.extend(form.requested_fields)

        # all output fields should be unique, not a single output field should be
        # calculated by more than one form
        if len(outs) != len(set(outs)):
            raise LionValueError("Output fields are not unique")

        return True

    def next_forms(self) -> Pile:
        """Get workable forms from a report.

        Args:
            report: The report to check.

        Returns:
            Pile of workable forms or None if no forms are workable.
        """
        a = [i for i in self.forms if i.is_workable]
        return pile(a) if len(a) > 0 else pile()

    @property
    def is_filled(self):
        return all(
            getattr(self, field, LN_UNDEFINED) not in [None, LN_UNDEFINED]
            for field in self.work_fields
        )


# File lion_core/form/report.py
