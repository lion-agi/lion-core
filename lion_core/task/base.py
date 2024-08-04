from typing import Any, override
from pydantic import Field

from lion_core.setting import LN_UNDEFINED
from lion_core.abc import MutableRecord
from lion_core.generic.component import Component


class BaseTask(Component, MutableRecord):
    template_name: str = "default_task"

    assignment: str | None = Field(
        None,
        description="The objective of the form.",
        examples=["input1, input2 -> output"],
    )

    input_fields: list[str] = Field(
        default_factory=list,
        description="Fields required to obtain the requested fields for the form's objective",
    )

    request_fields: list[str] = Field(
        default_factory=list, description="Fields requested to be filled."
    )

    task: Any = Field(
        default_factory=str,
        description="The work to be done by the form, including custom instructions.",
    )
    
    task_description: str = Field(
        str,
        description="Description of the task",
    )

    init_input_kwargs: dict = Field(default_factory=dict, exclude=True)

    none_as_valid_value: bool = Field(
        default=False, description="Indicate whether to treat None as a valid value."
    )

    has_processed: bool = Field(
        False,
        description="Indicate whether the task has been processed.",
        exclude=True,
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
        for i in self.input_fields + self.request_fields:
            result[i] = getattr(self, i)
        return result

    @property
    def is_completed(self) -> bool:
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
    def is_workable(self) -> bool:
        for i in self.input_fields:
            if self.none_as_valid_value:
                if getattr(self, i) is LN_UNDEFINED:
                    return False
            else:
                if getattr(self, i) is LN_UNDEFINED or getattr(self, i) is None:
                    return False
        if self.is_completed:
            return False
        return True

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
            3. The requested output fields are: {', '.join(self.request_fields)}
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
            for field in self.request_fields
        }
