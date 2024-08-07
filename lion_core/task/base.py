from typing import Any, override, Literal
from pydantic import Field

from lion_core.setting import LN_UNDEFINED
from lion_core.abc import MutableRecord
from lion_core.generic.component import Component


class BaseTask(Component, MutableRecord):

    assignment: str | None = Field(
        None,
        description="The objective of the task.",
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

    task_description: str | None = Field(
        default_factory=str,
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
        if name in {"input_fields", "request_fields"}:
            raise AttributeError(
                "Cannot directly assign to input/request fields. "
                "Please use append_to_input and/or append_to_request if append is supported."
            )

        super().__setattr__(name, value)

    @property
    def completed(self) -> bool:
        try:
            self.check_is_completed(handle_how="raise")
            return True
        except Exception:
            return False

    @property
    def workable(self) -> bool:
        try:
            self.check_is_workable(handle_how="raise")
            return True
        except Exception:
            return False

    @property
    def work_fields(self) -> dict[str, Any]:
        result = {}
        for i in self.input_fields + self.request_fields:
            result[i] = getattr(self, i)
        return result

    # check whether the request fields are completed
    def check_is_completed(
        self, handle_how: Literal["raise", "return_missing"] = "raise"
    ):
        if self.has_processed:
            return

        non_complete_request = []
        if self.none_as_valid_value:
            for i in self.request_fields:
                if getattr(self, i) is LN_UNDEFINED:
                    non_complete_request.append(i)
        else:
            for i in self.request_fields:
                if getattr(self, i) in [LN_UNDEFINED, None]:
                    non_complete_request.append(i)
        if non_complete_request:
            if handle_how == "raise":
                raise ValueError(
                    f"Request fields {non_complete_request} are not completed."
                )
            elif handle_how == "return_missing":
                return non_complete_request
        else:
            self.has_processed = True

    # check whether the request fields are completed
    def check_is_workable(
        self, handle_how: Literal["raise", "return_missing"] = "raise"
    ):
        if self.has_processed:
            raise ValueError(
                "The task has been processed, and cannot be worked on again."
            )

        missing_inputs = []
        if self.none_as_valid_value:
            for i in self.input_fields:
                if getattr(self, i) is LN_UNDEFINED:
                    missing_inputs.append(i)
        else:
            for i in self.input_fields:
                if getattr(self, i) in [LN_UNDEFINED, None]:
                    missing_inputs.append(i)
        if missing_inputs:
            if handle_how == "raise":
                raise ValueError(f"Input fields {missing_inputs} are not provided.")
            elif handle_how == "return_missing":
                return missing_inputs

    @property
    def instruction_dict(self) -> dict:
        return {
            "context": self.instruction_context,
            "instruction": self.instruction_prompt,
            "request_fields": self.instruction_request_fields,
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
            - value: {str(getattr(self, self.request_fields[idx]))}
            """
            for idx, i in enumerate(self.request_fields)
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
            2. The provided input fields are: {', '.join(self.request_fields)}
            3. The requested output fields are: {', '.join(self.request_fields)}
            4. Provide your response in the specified JSON format.
            """

    @property
    def instruction_request_fields(self) -> dict[str, str]:
        """
        Get descriptions of a form's requested fields.

        Returns:
            Dictionary mapping field names to descriptions.
        """
        return {
            field: self.all_fields[field].description or "N/A"
            for field in self.request_fields
        }


__all__ = ["BaseTask"]
