from lion_core.libs import strip_lower
from lion_core.exceptions import LionValueError, LionOperationError


RESTRICTED_FIELDS = {
    "input_fields",
    "request_fields",
    "assignment",
    "init_input_kwargs",
    "output_fields",
}


ERR_MAP = {
    "not_dict": ValueError("Input should be a valid dictionary for init."),
    "no_assignment": AttributeError(
        "Please provide an assignment for this form. "
        "Example assignment: 'input1, input2 -> output'."
    ),
    "explicit_input_request": LionValueError(
        "Explicitly defining input_fields and request_fields list is not supported. "
        "Please use assignment to indicate them."
    ),
    "explicit_task": LionValueError(
        "Explicitly defining task is not supported. Please use task_description."
    ),
    "invalid_input": LionValueError(
        "Inputs are missing in the assignment. "
        "Example assignment: 'input1, input2 -> output'."
    ),
    "missing_output": LionValueError(
        "Outputs are missing in the assignment. "
        "Example assignment: 'input1, input2 -> output'."
    ),
    "task_already_processed": LionValueError(
        "The task has been processed, and cannot be worked on again."
    ),
    "incomplete_request": lambda x: ValueError(
        f"Request fields {x} are not completed."
    ),
    "incomplete_input": lambda x: ValueError(f"Input fields {x} are not completed."),
    "strict_assignment": lambda x: LionOperationError(
        f"The form is set to strict_assignment. {x} should not be modified after init."
    ),
    "not_form_instance": LionValueError(
        "Invalid form for fill. Should be a instance of Form."
    ),
    "not_form_class": LionValueError(
        "Invalid form class. The form must be a subclass of Form."
    ),
    "invalid_assignment": lambda x: LionValueError(
        f"Invalid_assignment. Field {x} is not found in the form"
    ),
    "missing_field": lambda x: LionValueError(f"Field {x} is missing in the form."),
}


def get_input_output_fields(str_: str) -> tuple[list[str], list[str]]:
    if str_ is None:
        return [], []

    if "->" not in str_:
        raise ValueError("Invalid assignment format. Expected 'inputs -> outputs'.")

    inputs, outputs = str_.split("->")

    input_fields = [strip_lower(i) for i in inputs.split(",")]
    request_fields = [strip_lower(o) for o in outputs.split(",")]

    return input_fields, request_fields
