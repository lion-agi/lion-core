"""Manages operations on Form and Report instances in the Lion framework.

This module provides the ReportManager class, which centralizes operations
for Form and Report instances. It handles tasks such as checking workability,
filling forms and reports, and generating instructions.
"""

from typing import Any, List
from lion_core.sys_util import LN_UNDEFINED
from lion_core.exceptions import LionValueError
from lion_core.generic.pile import Pile, pile
from lion_core.generic.util import to_list_type
from .form import Form


class FormManager:
    """Manages operations on Form and Report instances."""

    @staticmethod
    def get_all_work_fields(
        obj: Form, form: List[Form] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Gather all work fields from forms and additional sources.

        Args:
            obj: Main form or report.
            form: List of additional forms.
            **kwargs: Additional fields to include.

        Returns:
            Dictionary of all gathered work fields with valid values.
        """
        form_list: list[Form] = to_list_type(form) if form else []
        all_fields = obj.work_fields.copy()
        all_form_fields = (
            {}
            if not form_list
            else {
                k: v
                for f in form_list
                for k, v in f.work_fields.items()
                if v not in [None, LN_UNDEFINED]
            }
        )
        all_fields.update({**all_form_fields, **kwargs})
        return all_fields

    @staticmethod
    def is_form_workable(form: Form) -> bool:
        """Check if a form is ready for processing.

        Args:
            form: The form to check.

        Returns:
            True if the form is workable.

        Raises:
            LionValueError: If form is filled or missing required fields.
        """
        if form.filled:
            raise LionValueError("Form is already filled.")

        for field in form.input_fields:
            if not getattr(form, field, LN_UNDEFINED):
                raise LionValueError(f"Required field '{field}' is missing.")

        return True

    @staticmethod
    def is_report_workable(report: Form) -> bool:
        """Check if a report is ready for processing.

        Args:
            report: The report to check.

        Returns:
            True if the report is workable.

        Raises:
            LionValueError: If report is improperly configured.
        """
        if report.filled:
            raise LionValueError("Report is already filled.")

        for field in report.input_fields:
            if not getattr(report, field, LN_UNDEFINED):
                raise LionValueError(f"Required field '{field}' is missing.")

        fields = set(report.input_fields + report.requested_fields)
        if not fields.issubset(report.work_fields.keys()):
            raise LionValueError("Some required fields are not in the forms.")

        output_fields = [f for form in report.forms for f in form.requested_fields]
        if len(output_fields) != len(set(output_fields)):
            raise LionValueError("Output fields are not unique across forms.")

        return True

    @staticmethod
    def next_forms(report: Form) -> Pile:
        """Get workable forms from a report.

        Args:
            report: The report to check.

        Returns:
            Pile of workable forms or None if no forms are workable.
        """
        a = [i for i in report.forms if i.workable]
        return pile(a) if len(a) > 0 else None

    @staticmethod
    def fill_form(
        obj: Form, other_form: list[Form] = None, strict: bool = True, **kwargs
    ) -> None:
        """Fill a form with data from other forms or kwargs.

        Args:
            obj: Form to fill.
            other_form: List of forms to get data from.
            strict: Raise error if form is already filled.
            **kwargs: Additional fields to fill.

        Raises:
            ValueError: If form is filled and strict is True.
        """
        if obj.filled:
            if strict:
                raise ValueError("Form is filled, cannot be worked on again")

        all_fields = FormManager.get_all_work_fields(other_form, **kwargs)

        for k, v in all_fields.items():
            if k in obj.work_fields and v is not None and getattr(obj, k, None) is None:
                setattr(obj, k, v)

    @staticmethod
    def fill_report(
        report: Form, form: Form = None, strict: bool = True, **kwargs
    ) -> None:
        """
        Fill a report and its forms with provided data.

        Args:
            report: Report to fill.
            form: Optional form to get data from.
            strict: Raise error if report is already filled.
            **kwargs: Additional fields to fill.

        Raises:
            ValueError: If report is filled and strict is True.
        """
        if report.filled:
            if strict:
                raise ValueError("Form is filled, cannot be worked on again")

        # gather all unique valid fields from input form,
        # kwargs and self workfields data
        all_work_fields = FormManager.get_all_work_fields(report, form, **kwargs)

        # if there are information in the forms that are not in the report,
        # add them to the report
        for k, v in all_work_fields.items():
            if (
                k in report.work_fields
                and getattr(report, k, LN_UNDEFINED) is LN_UNDEFINED
            ):
                setattr(report, k, v)

        # if there are information in the report that are not in the forms,
        # add them to the forms
        for _form in report.forms:
            for k, v in _form.work_fields.items():
                _kwargs = {}
                if (
                    v in [None, LN_UNDEFINED]
                    and (a := getattr(report, k, LN_UNDEFINED)) is not LN_UNDEFINED
                ):
                    _kwargs[k] = a

                FormManager.fill_form(_form, _kwargs, strict=strict)

    @staticmethod
    def get_instruction_context(form: Form) -> str:
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
        - description: {getattr(form.all_fields[i], "description", "N/A")}
        - value: {str(form.__getattribute__(form.input_fields[idx]))}
        """
            for idx, i in enumerate(form.input_fields)
        )

    @staticmethod
    def get_instruction_prompt(form: Form) -> str:
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
        1. Your task is: {form.task}
        2. The provided input fields are: {', '.join(form.input_fields)}
        3. The requested output fields are: {', '.join(form.requested_fields)}
        4. Provide your response in the specified JSON format.
        """

    @staticmethod
    def get_instruction_requested_fields(form: Form) -> dict[str, str]:
        """
        Get descriptions of a form's requested fields.

        Args:
            form: Form to get requested fields from.

        Returns:
            Dictionary mapping field names to descriptions.
        """
        return {
            field: form.model_fields[field].description or "N/A"
            for field in form.requested_fields
        }

    @staticmethod
    def form_instruction_dict(form: Form) -> dict[str, str]:
        """
        Generate a dictionary of form instructions.

        Args:
            form: Form to generate instructions for.

        Returns:
            Dictionary of form instructions.
        """
        return {
            "context": FormManager.get_instruction_context(form),
            "instruction": FormManager.get_instruction_prompt(form),
            "requested_fields": FormManager.get_instruction_requested_fields(form),
        }

    @staticmethod
    def check_workable_report(report: Form) -> bool:
        """
        Check if a report is ready for processing.

        Args:
            report: Report to check.

        Returns:
            True if report is workable.

        Raises:
            ValueError: If report is not properly configured.
        """
        if report.filled:
            raise ValueError("Form is already filled, cannot be worked on again")

        for i in report.input_fields:
            if not getattr(report, i, None):
                raise ValueError(f"Required field {i} is not provided")

        # this is the required fields from report's own assignment
        fields = report.input_fields
        fields.extend(report.requested_fields)

        # if the report's own assignment is not in the forms, return False
        for f in fields:
            if f not in report.work_fields:
                raise ValueError(f"Field {f} is not in the forms")

        # get all the output fields from all the forms
        outs = []
        for form in report.forms:
            outs.extend(form.requested_fields)

        # all output fields should be unique, not a single output field should be
        # calculated by more than one form
        if len(outs) != len(set(outs)):
            raise ValueError("Output fields are not unique")

        return True


# File: lion_core/form/report_manager.py
