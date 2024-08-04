# single step form
# rely on assignment

# 1. input/requested = get_input_output_fields(assignment)
# 2. does not allow explicit input/requested list define in init
# 3. input/requested list and assignment can not be changed after init

from typing import Any, override
import inspect
from pydantic import model_validator
from pydantic.fields import FieldInfo

from lion_core.setting import LN_UNDEFINED
from lion_core.exceptions import LionValueError
from lion_core.task.base import BaseTask
from lion_core.task.utils import get_input_output_fields


class StaticTask(BaseTask):

    @model_validator(mode="before")
    @classmethod
    def check_input_output_list_omitted(cls, data: dict):
        if not isinstance(data, dict):
            raise ValueError("Input should be a valid dictionary for init.")
        if not data.get("assignment"):
            raise AttributeError(
                "Please provide an assignment for this form. "
                "Example assignment: 'input1, input2 -> output'."
            )
        if "input_fields" in data or "requested_fields" in data:
            raise AttributeError(
                "Explicitly defining input_fields and requested_fields list is not supported. "
                "Please use assignment to indicate them."
            )

        input_fields, requested_fields = get_input_output_fields(data.get("assignment"))
        if not input_fields or input_fields == [""]:
            raise LionValueError(
                "Inputs are missing in the assignment. "
                "Example assignment: 'input1, input2 -> output'."
            )
        elif not requested_fields or requested_fields == [""]:
            raise LionValueError(
                "Outputs are missing in the assignment. "
                "Example assignment: 'input1, input2 -> output'."
            )
        data["input_fields"] = input_fields
        data["requested_fields"] = requested_fields

        data["input_kwargs"] = {}
        for item in data["input_fields"]:
            if item not in cls.model_fields:
                data["input_kwargs"][item] = data.pop(item, LN_UNDEFINED)
            else:
                data["input_kwargs"][item] = data.get(item, LN_UNDEFINED)

        return data

    @model_validator(mode="after")
    def check_input_output_fields(self):
        for i in self.input_fields:
            if i in self.model_fields:
                self.init_input_kwargs[i] = getattr(self, i)
            else:
                self.add_field(i, value=self.init_input_kwargs.get(i, LN_UNDEFINED))

        for i in self.request_fields:
            if i not in self.all_fields:
                self.add_field(i)
        return self

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"input_fields", "requested_fields", "assignment", "input_kwargs"}:
            raise AttributeError(f"{name} should not be modified after init")

        super().__setattr__(name, value)
        if name in self.input_fields:
            self.init_input_kwargs[name] = value

    @override
    def update_field(
        self,
        name: str,
        value: Any = LN_UNDEFINED,
        annotation: Any = LN_UNDEFINED,
        field_obj: FieldInfo | Any = LN_UNDEFINED,
        **kwargs,
    ) -> None:
        super().update_field(
            name=name, value=value, annotation=annotation, field_obj=field_obj, **kwargs
        )
        if name in self.input_fields:
            self.init_input_kwargs[name] = getattr(self, name)

    @classmethod
    def from_form(
        cls,
        assignment: str,
        form: BaseTask,
        task: Any = None,
        fill_inputs: bool = True,
        none_as_valid_value: bool = False,
    ):
        if inspect.isclass(form):
            if not issubclass(form, BaseTask):
                raise LionValueError(
                    "Invalid form class. The form must be a subclass of BaseForm."
                )
            template_name = form.model_fields["template_name"].default
            form_fields = form.model_fields
        else:
            if not isinstance(form, BaseTask):
                raise LionValueError(
                    "Invalid form instance. The form must be an instance of a subclass of BaseForm."
                )
            template_name = form.template_name
            form_fields = form.all_fields
        obj = cls(
            assignment=assignment,
            template_name=template_name,
            task=task,
            none_as_valid_value=none_as_valid_value,
        )
        for i in obj.work_fields.keys():
            obj.update_field(i, field_obj=form_fields[i])
            if not none_as_valid_value and getattr(obj, i) is None:
                setattr(obj, i, LN_UNDEFINED)
        if fill_inputs:
            if inspect.isclass(form):
                raise LionValueError(
                    "fill_inputs does not support passing a form class. "
                    "Please pass an instance of a form instead or set fill_inputs to False."
                )
            obj.fill_input_fields(form=form)
        return obj
