"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
    fallback_structure_imodel: Any = None,
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
        fallback_structure_imodel=fallback_structure_imodel,
    )
    if template_name:
        form.template_name = template_name

    return form
