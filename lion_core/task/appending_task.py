# original Form (For UnitForm)

# 1. in init, input/requested = get_input_output_fields(assignment)
# 2. only allow append_to (input/requested)
# 3. mainly when fields are already defined in all_fields, add_field tends not to be called in append_to

from typing import Any, Literal

from pydantic import model_validator

from lion_core.setting import LN_UNDEFINED
from lion_core.task.base import BaseTask
from lion_core.task.utils import get_input_output_fields


class Task(BaseTask):

    @model_validator(mode="before")
    @classmethod
    def check_input_output_list(cls, data: dict):
        if not isinstance(data, dict):
            raise ValueError("Input should be a valid dictionary for init.")

        data["input_fields"] = data.get("input_fields", [])
        data["requested_fields"] = data.get("requested_fields", [])
        input_fields, requested_fields = get_input_output_fields(data.get("assignment"))

        if not isinstance(data["input_fields"], list):
            raise TypeError("Invalid type for input_fields. Should be a list of str.")
        for i in input_fields:
            if i not in data["input_fields"]:
                data["input_fields"].append(i)

        if not isinstance(data["requested_fields"], list):
            raise TypeError(
                "Invalid type for requested_fields. Should be a list of str"
            )
        for i in requested_fields:
            if i not in data["requested_fields"]:
                data["requested_fields"].append(i)

        data["input_kwargs"] = {}

        for item in data["input_fields"]:
            if item not in cls.model_fields:
                data["input_kwargs"][item] = data.pop(item, LN_UNDEFINED)
            else:
                data["input_kwargs"][item] = data.get(item, LN_UNDEFINED)

        return data

    @model_validator(mode="after")
    def check_input_output_fields(self):
        for i in self.request_fields:
            if i in self.model_fields:
                self.init_input_kwargs[i] = getattr(self, i)
            else:
                self.add_field(i, value=self.init_input_kwargs.get(i, LN_UNDEFINED))

        for i in self.request_fields:
            if i not in self.all_fields:
                self.add_field(i)
        return self

    def append_to_input(self, field: str, value=LN_UNDEFINED):
        if field not in self.all_fields:
            self.add_field(field)
        if field not in self.request_fields:
            self.request_fields.append(field)
        if value is not LN_UNDEFINED:
            setattr(self, field, value)

        self.init_input_kwargs[field] = getattr(self, field)

    def append_to_request(self, field: str, value=LN_UNDEFINED):
        if field not in self.all_fields:
            self.add_field(field)
        if field not in self.request_fields:
            self.request_fields.append(field)
        if value is not LN_UNDEFINED:
            setattr(self, field, value)
