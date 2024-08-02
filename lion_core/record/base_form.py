from typing import Any, override
from pydantic import Field

from lion_core.setting import LN_UNDEFINED
from lion_core.abc import MutableRecord
from lion_core.sys_utils import SysUtil
from lion_core.exceptions import LionValueError
from lion_core.generic.component import Component, T


class BaseForm(Component, MutableRecord):
    template_name: str = "default_base_form"

    assignment: str | None = Field(
        None,
        description="The objective of the form.",
        examples=["input1, input2 -> output"],
    )

    input_fields: list[str] = Field(
        default_factory=list,
        description="Fields required to obtain the requested fields for the form's objective",
    )

    requested_fields: list[str] = Field(
        default_factory=list, description="Fields requested to be filled."
    )

    task: Any = Field(
        default_factory=str,
        description="The work to be done by the form, including custom instructions.",
    )

    input_kwargs: dict = Field(default_factory=dict, exclude=True)

    none_as_valid_value: bool = Field(
        default=False, description="Indicate whether to treat None as a valid value."
    )

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"input_fields", "requested_fields"}:
            raise AttributeError(
                "Cannot directly assign to input/requested fields. "
                "Please use append_to_input and/or append_to_request if append is supported."
            )

        super().__setattr__(name, value)

    @property
    def work_fields(self) -> dict[str, Any]:
        result = {}
        for i in self.input_fields + self.requested_fields:
            result[i] = getattr(self, i)
        return result

    @property
    def filled(self) -> bool:
        if self.none_as_valid_value:
            if LN_UNDEFINED in self.work_fields.values():
                return False
            else:
                return True
        else:
            if (
                LN_UNDEFINED in self.work_fields.values()
                or None in self.work_fields.values()
            ):
                return False
            else:
                return True

    @property
    def workable(self) -> bool:
        for i in self.input_fields:
            if self.none_as_valid_value:
                if getattr(self, i) is LN_UNDEFINED:
                    return False
            else:
                if getattr(self, i) is LN_UNDEFINED or getattr(self, i) is None:
                    return False
        if self.filled:
            return False
        return True

    def fill(self, form: "BaseForm" = None, **kwargs):
        self.fill_input_fields(form=form, **kwargs)
        self.fill_requested_fields(form=form, **kwargs)

    def fill_input_fields(self, form: "BaseForm" = None, **kwargs):
        if form is not None and not isinstance(form, BaseForm):
            raise LionValueError(
                "Invalid form for fill. Should be a instance of BaseForm."
            )
        for i in self.input_fields:
            if self.none_as_valid_value:
                if getattr(self, i) is not LN_UNDEFINED:
                    continue
                value = kwargs.get(i, LN_UNDEFINED)
                if value is LN_UNDEFINED:
                    value = SysUtil.copy(getattr(form, i, LN_UNDEFINED))
                if value is not LN_UNDEFINED:
                    setattr(self, i, value)
            else:
                if getattr(self, i) is None or getattr(self, i) is LN_UNDEFINED:
                    value = kwargs.get(i)
                    if value is LN_UNDEFINED or value is None:
                        value = SysUtil.copy(getattr(form, i, LN_UNDEFINED))
                    if value is not LN_UNDEFINED and value is not None:
                        setattr(self, i, value)

    def fill_requested_fields(self, form: "BaseForm" = None, **kwargs):
        if form is not None and not isinstance(form, BaseForm):
            raise LionValueError(
                "Invalid form for fill. Should be a instance of BaseForm."
            )
        for i in self.requested_fields:
            if self.none_as_valid_value:
                if getattr(self, i) is not LN_UNDEFINED:
                    continue
                value = kwargs.get(i, LN_UNDEFINED)
                if value is LN_UNDEFINED:
                    value = SysUtil.copy(getattr(form, i, LN_UNDEFINED))
                if value is not LN_UNDEFINED:
                    setattr(self, i, value)
            else:
                if getattr(self, i) is None or getattr(self, i) is LN_UNDEFINED:
                    value = kwargs.get(i)
                    if value is LN_UNDEFINED or value is None:
                        value = SysUtil.copy(getattr(form, i, LN_UNDEFINED))
                    if value is not LN_UNDEFINED and value is not None:
                        setattr(self, i, value)

    @property
    def instruction_dict(self) -> dict:
        return {
            "context": self.instruction_context,
            "instruction": self.instruction_prompt,
            "requested_fields": self.instruction_requested_fields,
        }

    @property
    def instruction_context(self) -> str:
        """
        Generate a description of the form's input fields.

        Returns:
            String with descriptions of input fields.
        """
        return "".join(
            f"""
            ## input: {i}:
            - description: {getattr(self.all_fields[i], "description", "N/A")}
            - value: {str(getattr(self, self.input_fields[idx]))}
            """
            for idx, i in enumerate(self.input_fields)
        )

    @property
    def instruction_prompt(self) -> str:
        """
        Generate a task instruction prompt for a form.

        Returns:
            Formatted instruction prompt string.
        """
        return f"""
            ## Task Instructions
            Please follow prompts to complete the task:
            1. Your task is: {self.task}
            2. The provided input fields are: {', '.join(self.input_fields)}
            3. The requested output fields are: {', '.join(self.requested_fields)}
            4. Provide your response in the specified JSON format.
            """

    @property
    def instruction_requested_fields(self) -> dict[str, str]:
        """
        Get descriptions of a form's requested fields.

        Returns:
            Dictionary mapping field names to descriptions.
        """
        return {
            field: self.all_fields[field].description or "N/A"
            for field in self.requested_fields
        }
