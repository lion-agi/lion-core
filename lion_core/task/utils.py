from lion_core.libs import strip_lower


def get_input_output_fields(str_: str) -> tuple[list[str], list[str]]:
    if str_ is None:
        return [], []

    if "->" not in str_:
        raise ValueError("Invalid assignment format. Expected 'inputs -> outputs'.")

    inputs, outputs = str_.split("->")

    input_fields = [strip_lower(i) for i in inputs.split(",")]
    request_fields = [strip_lower(o) for o in outputs.split(",")]

    return input_fields, request_fields
