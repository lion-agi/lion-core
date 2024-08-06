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
from lion_core.sys_utils import SysUtil
from lion_core.generic.form import Form
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
        if "input_fields" in data or "request_fields" in data:
            raise AttributeError(
                "Explicitly defining input_fields and request_fields list is not supported. "
                "Please use assignment to indicate them."
            )
        if "task" in data:
            raise AttributeError(
                "Explicitly defining task is not supported. Please use task_description."
            )

        input_fields, request_fields = get_input_output_fields(data.get("assignment"))
        if not input_fields or input_fields == [""]:
            raise LionValueError(
                "Inputs are missing in the assignment. "
                "Example assignment: 'input1, input2 -> output'."
            )
        elif not request_fields or request_fields == [""]:
            raise LionValueError(
                "Outputs are missing in the assignment. "
                "Example assignment: 'input1, input2 -> output'."
            )
        data["input_fields"] = input_fields
        data["request_fields"] = request_fields

        data["init_input_kwargs"] = {}
        for item in data["input_fields"]:
            if item not in cls.model_fields:
                data["init_input_kwargs"][item] = data.pop(item, LN_UNDEFINED)
            else:
                data["init_input_kwargs"][item] = data.get(item, LN_UNDEFINED)

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
        if name in {"input_fields", "request_fields", "assignment", "init_input_kwargs"}:
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

    def fill_input_fields(self, form: Form = None, **value_kwargs):
        if form is not None and not isinstance(form, Form):
            raise LionValueError(
                "Invalid form for fill. Should be a instance of Form."
            )
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

    def fill_request_fields(self, form: Form = None, **value_kwargs):
        if form is not None and not isinstance(form, Form):
            raise LionValueError(
                "Invalid form for fill. Should be a instance of Form."
            )
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
    def from_form(cls,
                  assignment: str,
                  form: Form,
                  task_description: str = None,
                  fill_inputs: bool = True,
                  none_as_valid_value: bool = False,
                  **input_value_kwargs):
        if inspect.isclass(form):
            if not issubclass(form, Form):
                raise LionValueError(
                    "Invalid form class. The form must be a subclass of Form."
                )
            form_fields = form.model_fields
        else:
            if not isinstance(form, Form):
                raise LionValueError(
                    "Invalid form instance. The form must be an instance of a subclass of Form."
                )
            form_fields = form.all_fields

        obj = cls(
            assignment=assignment,
            task_description=task_description,
            none_as_valid_value=none_as_valid_value,
        )

        for i in obj.work_fields.keys():
            if i not in form_fields:
                raise LionValueError(f"Invalid_assignment. Field {i} is not found in the form {form}.")
            obj.update_field(i, field_obj=form_fields[i])
            if not none_as_valid_value and getattr(obj, i) is None:
                setattr(obj, i, LN_UNDEFINED)

        if fill_inputs:
            if inspect.isclass(form):
                obj.fill_input_fields(**input_value_kwargs)
            else:
                obj.fill_input_fields(form=form, **input_value_kwargs)

        return obj
