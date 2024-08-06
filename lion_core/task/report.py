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
from lion_core.generic.form import Form
from lion_core.generic.pile import Pile
from lion_core.task.base import BaseTask
from lion_core.task.static_task import StaticTask


class Report(Form):
    template_name: str = "default_report"

    final_output_fields: list[str] = Field(
        default_factory=list,
        description="A list for objective fields"
    )

    completed_tasks: Pile[BaseTask] = Field(
        default_factory=lambda: Pile(item_type={BaseTask}),
        description="A pile of tasks completed",
    )

    completed_task_assignments: dict[str, str] = Field(
        default_factory=dict,
        description="assignments completed for the report"
    )

    @property
    def final_output(self):
        result = {}
        for i in self.final_output_fields:
            if i not in self.all_fields:
                raise ValueError(f"Failed to find objective output field {i}")
            result[i] = getattr(self, i, LN_UNDEFINED)
        return result

    @property
    def work_fields(self):
        base_report_fields = Report.model_fields.keys()
        return {k: getattr(self, k) for k in self.all_fields if k not in base_report_fields}

    def get_incomplete_fields(self, none_as_valid_value=False):
        base_report_fields = Report.model_fields.keys()

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

    def parse_assignment(self, input_fields: list[str], request_fields: list[str]):
        if not isinstance(input_fields, list) or not isinstance(request_fields, list):
            raise ValueError("Invalid input_fields or request_fields type. Should be a list of str")
        for i in input_fields + request_fields:
            if i not in self.all_fields:
                raise ValueError(f"Invalid field {i}. Failed to find it in all_fields")

        input_assignment = ", ".join(input_fields)
        output_assignment = ", ".join(request_fields)
        return " -> ".join([input_assignment, output_assignment])

    def create_task(self,
                    assignment: str = None,
                    input_fields: list[str] = None,
                    request_fields: list[str] = None,
                    task_description: str = None,
                    fill_inputs: bool = True,
                    none_as_valid_value: bool = False):
        if all(i is None for i in [assignment, input_fields, request_fields]):
            raise ValueError("Please provide an assignment or input/request fields to create a task.")
        if assignment is not None and (input_fields is not None or request_fields is not None):
            raise ValueError("Please provide an assignment only or input/request fields only, not both.")
        if assignment is None and (input_fields is None or request_fields is None):
            raise ValueError("Please provide input_fields list and request_fields list together.")

        if not assignment:
            assignment = self.parse_assignment(input_fields, request_fields)
        task = StaticTask.from_form(assignment=assignment,
                                    form=self,
                                    task_description=task_description,
                                    fill_inputs=fill_inputs,
                                    none_as_valid_value=none_as_valid_value)
        return task

    def save_completed_task(self, task: StaticTask, update_results=False):
        try:
            task.check_is_completed(handle_how="raise")
        except Exception as e:
            raise ValueError(f"Failed to add completed task. Error: {e}")

        report_fields = self.all_fields.keys()
        for i in task.work_fields.keys():
            if i not in report_fields:
                raise LionValueError(f"Tha task does not match the report. "
                                     f"Field {i} in the task assignment is not found in the report.")

        self.completed_tasks.include(task)
        self.completed_task_assignments[task.ln_id] = task.assignment

        if update_results:
            for i in task.request_fields:
                field_result = getattr(task, i)
                setattr(self, i, field_result)

    @classmethod
    def from_form_template(cls, template_class: Type[Form], **input_kwargs):
        if not issubclass(template_class, Form):
            raise LionValueError(
                "Invalid form template. The template class must be a subclass of Form."
            )
        report_template_name = "report_for_" + template_class.model_fields["template_name"].default
        report_obj = cls(template_name=report_template_name)

        base_report_fields = Report.model_fields.keys()

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
    def from_form(cls, form: Form, fill_inputs: bool = True):
        if not isinstance(form, Form):
            raise LionValueError(
                "Invalid form instance. The form must be an instance of a subclass of Form."
            )
        report_template_name = "report_for_" + form.template_name
        report_obj = cls(template_name=report_template_name)

        base_report_fields = Report.model_fields.keys()

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
