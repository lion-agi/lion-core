# dynamic process form
# assignment as guide, input/requested fields change along the process

# 1. does not get fields from assignment, input/requested fields are added separately
# 2. intermediate step assignment property reflects current input/requested fields list
# 3. allow input/requested fields deletion
# 4. mainly when fields are already defined in all_fields, add_field tends not to be called in append_to

from pydantic import model_validator

from lion_core.setting import LN_UNDEFINED
from lion_core.record.base_form import BaseForm


class DynamicForm(BaseForm):

    @model_validator(mode="before")
    @classmethod
    def check_input_output_list(cls, data: dict):
        if not isinstance(data, dict):
            raise ValueError("Input should be a valid dictionary for init.")

        data["input_fields"] = data.get("input_fields", [])
        data["requested_fields"] = data.get("requested_fields", [])

        if "input_fields" in data or "requested_fields" in data:
            raise AttributeError(
                "Explicitly defining input_fields and requested_fields list is not supported. "
                "Please use append_to methods after init."
            )

        return data

    @property
    def current_step_assignment(self):
        input_str = ", ".join(self.input_fields)
        requested_str = ", ".join(self.requested_fields)
        output = " -> ".join([input_str, requested_str])
        return output

    def append_to_input(self, field: str, value=LN_UNDEFINED):
        if field not in self.all_fields:
            self.add_field(field)
        if field not in self.input_fields:
            self.input_fields.append(field)
        if value is not LN_UNDEFINED:
            setattr(self, field, value)

        self.input_kwargs[field] = getattr(self, field)

    def append_to_request(self, field: str, value=LN_UNDEFINED):
        if field not in self.all_fields:
            self.add_field(field)
        if field not in self.requested_fields:
            self.requested_fields.append(field)
        if value is not LN_UNDEFINED:
            setattr(self, field, value)

    def remove_from_input(self, field: str):
        if "," in field:
            field = field.split(",")
        if not isinstance(field, list):
            field = [field]

        for i in field:
            i = i.strip()
            if i in self.input_fields:
                self.input_fields.remove(i)
                self.input_kwargs.pop(i)

    def remove_from_request(self, field: str):
        if "," in field:
            field = field.split(",")
        if not isinstance(field, list):
            field = [field]

        for i in field:
            i = i.strip()
            if i in self.requested_fields:
                self.requested_fields.remove(i)
