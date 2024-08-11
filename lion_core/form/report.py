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

from typing import Type
from pydantic import Field

from lion_core.exceptions import LionValueError
from lion_core.setting import LN_UNDEFINED
from lion_core.generic.pile import Pile
from lion_core.form.base import BaseForm
from lion_core.form.form import Form


class Report(BaseForm):

    default_form_template: Type[Form] = Form
    strict_form: bool = Field(
        default=False,
        description="Indicate whether the form is strict. If True, the form cannot be modified after init.",
    )

    completed_tasks: Pile[Form] = Field(
        default_factory=lambda: Pile(item_type={Form}),
        description="A pile of tasks completed",
    )

    completed_task_assignments: dict[str, str] = Field(
        default_factory=dict, description="assignments completed for the report"
    )

    @property
    def work_fields(self) -> list[str]:
        base_report_fields = self.__class__.model_fields.keys()
        return [i for i in self.all_fields.keys() if i not in base_report_fields]

    def get_incomplete_fields(
        self,
        none_as_valid_value: bool = False,
    ):
        base_report_fields = self.__class__.model_fields.keys()

        result = []
        for i in self.all_fields:
            if i in base_report_fields:
                continue
            if none_as_valid_value:
                if getattr(self, i) is LN_UNDEFINED:
                    result.append(i)
            else:
                if getattr(self, i) in [None, LN_UNDEFINED]:
                    result.append(i)
        return result

    def parse_assignment(
        self,
        input_fields: list[str],
        request_fields: list[str],
    ):
        if not isinstance(input_fields, list) or not isinstance(request_fields, list):
            raise ValueError(
                "Invalid input_fields or request_fields type. Should be a list of str"
            )
        for i in input_fields + request_fields:
            if i not in self.all_fields:
                raise ValueError(f"Invalid field {i}. Failed to find it in all_fields")

        input_assignment = ", ".join(input_fields)
        output_assignment = ", ".join(request_fields)
        return " -> ".join([input_assignment, output_assignment])

    def create_form(
        self,
        assignment: str,
        *,
        input_fields: list[str] | None = None,
        request_fields: list[str] | None = None,
        task_description: str | None = None,
        fill_inputs: bool | None = True,
        none_as_valid_value: bool | None = False,
        strict=None,
    ):
        if assignment is not None:
            if input_fields is not None or request_fields is not None:
                raise ValueError(
                    "You cannot provide input/request fields when assignment is provided."
                )
        else:
            if input_fields is None or request_fields is None:
                raise ValueError(
                    "Please provide input_fields list and request_fields list together."
                )

        if not assignment:
            assignment = self.parse_assignment(
                input_fields=input_fields,
                request_fields=request_fields,
            )

        f_ = self.default_form_template.from_form(
            assignment=assignment,
            form=self,
            task_description=task_description,
            fill_inputs=fill_inputs,
            none_as_valid_value=none_as_valid_value,
            strict=strict if isinstance(strict, bool) else self.strict_form,
        )
        return f_

    def save_completed_task(
        self,
        form: Form,
        update_results=False,
    ):
        try:
            form.check_is_completed(handle_how="raise")
        except Exception as e:
            raise ValueError(f"Failed to add completed task. Error: {e}")

        report_fields = self.all_fields.keys()
        for i in form.work_dict.keys():
            if i not in report_fields:
                raise LionValueError(
                    f"Tha task does not match the report. "
                    f"Field {i} in the task assignment is not found in the report."
                )

        self.completed_tasks.include(form)
        self.completed_task_assignments[form.ln_id] = form.assignment

        if update_results:
            for i in form.request_fields:
                field_result = getattr(form, i)
                setattr(self, i, field_result)

    @classmethod
    def from_form_template(
        cls,
        template_class: Type[BaseForm],
        **input_kwargs,
    ):
        if not issubclass(template_class, BaseForm):
            raise LionValueError(
                "Invalid form template. The template class must be a subclass of Form."
            )
        template_class = template_class or cls.default_form_template
        report_template_name = (
            "report_for_" + template_class.model_fields["template_name"].default
        )
        report_obj = cls(template_name=report_template_name)

        base_report_fields = cls.model_fields.keys()

        for field, field_info in template_class.model_fields.items():
            if field in base_report_fields:
                continue
            if field not in report_obj.all_fields:
                report_obj.add_field(field, field_obj=field_info)
            if field in input_kwargs:
                value = input_kwargs.get(field)
                setattr(report_obj, field, value)

        return report_obj

    @classmethod
    def from_form(
        cls,
        form: BaseForm,
        fill_inputs: bool = True,
    ):
        if not isinstance(form, BaseForm):
            raise LionValueError(
                "Invalid form instance. The form must be an instance of a subclass of Form."
            )
        report_template_name = "report_for_" + form.template_name
        report_obj = cls(template_name=report_template_name)

        base_report_fields = cls.model_fields.keys()

        for field, field_info in form.all_fields.items():
            if field in base_report_fields:
                continue
            if field not in report_obj.all_fields:
                report_obj.add_field(field, field_obj=field_info)
            if fill_inputs:
                value = getattr(form, field)
                setattr(report_obj, field, value)

        return report_obj


# File lion_core/form/report.py
