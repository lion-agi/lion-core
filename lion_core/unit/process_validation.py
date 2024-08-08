from typing import Any

from lion_core.form.task_form import BaseForm
from lion_core.rule.validator import Validator


async def process_validation(
    form: BaseForm,
    validator: Validator,
    response_: dict | str,
    rulebook: Any = None,
    strict: bool = False,
    use_annotation: bool = True,
    template_name: str | None = None,
) -> BaseForm:
    """
    Process form validation.

    Args:
        form: The form to validate.
        validator: The validator to use.
        response_: The response to validate.
        rulebook: Optional rulebook for validation.
        strict: Whether to use strict validation.
        use_annotation: Whether to use annotation for validation.
        template_name: Optional template name to set on the form.

    Returns:
        The validated form.
    """
    validator = Validator(rulebook=rulebook) if rulebook else validator
    form = await validator.validate_response(
        form=form,
        response=response_,
        strict=strict,
        use_annotation=use_annotation,
    )
    if template_name:
        form.template_name = template_name

    return form
