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

from typing import Any, Callable

from lion_core.abc import BaseExecutor, Temporal, Observable
from lion_core.sys_utils import SysUtil
from lion_core.exceptions import LionTypeError, LionValueError

from lion_core.form.base import BaseForm
from lion_core.form.form import Form
from lion_core.imodel.imodel import iModel
from lion_core.rule.base import Rule
from lion_core.rule.rulebook import RuleBook


class RuleProcessor(BaseExecutor, Temporal, Observable):

    def __init__(
        self,
        *,
        strict: bool = True,
        rulebook: RuleBook = None,
        structure_imodel: iModel = None,
    ):
        self.ln_id = SysUtil.id()
        self.timestamp = SysUtil.time()
        self.strict = strict
        self.rulebook = rulebook or RuleBook()
        self.structure_imodel = structure_imodel

    def init_rule(
        self,
        rule_order: list = None,
        progress: str = None,  # an existing progress in rulebook
    ):
        if not rule_order:
            rule_order = self.rulebook.default_rule_order

        progress = self.rulebook.rule_flow._find_prog(progress)
        for i in rule_order:
            self.rulebook.init_rule(i, progress=progress)

    async def process_field(
        self,
        field: str,
        value: Any,
        /,
        *,
        annotation=None,
        form: BaseForm = None,
        progress=None,
        check_func: Callable = None,
        **kwargs,
    ):

        if annotation is None:
            if isinstance(form, BaseForm) and field in form.all_fields:
                annotation = form.field_getattr(field, "annotation")

        for i in self.rulebook.rule_flow[progress]:
            rule: Rule = self.rulebook.active_rules[i]
            if await rule.apply(
                field,
                value,
                annotation=annotation,
                check_func=check_func,
                **kwargs,
            ):
                try:
                    return await rule.validate(value)
                except Exception as e:
                    raise LionValueError(f"Failed to validate field: {field}") from e

        if self.strict:
            error_message = (
                f"Failed to validate {field} because no rule applied. To return the "
                "original value directly when no rule applies, set strict=False."
            )
            raise LionValueError(error_message)

        return value

    async def process_form(
        self,
        form: Form,
        response: dict | str,
        progress=None,
        structure_str: bool = False,
        structure_imodel: iModel | None = None,
    ):
        if isinstance(response, str):
            if len(form.request_fields) == 1:
                response = {form.request_fields[0]: response}
            else:
                if structure_str:
                    structure_imodel: iModel | None = (
                        structure_imodel or self.structure_imodel
                    )
                    if not structure_imodel:
                        raise ValueError(
                            "Response is a string, you asked to structure the string"
                            "but no structure imodel was provided"
                        )
                    try:
                        response = await structure_imodel.structure(response)
                    except Exception as e:
                        raise ValueError(
                            "Failed to structure the response string"
                            "Response is a string, but form has multiple"
                            " fields to be filled"
                        ) from e

            if not isinstance(response, dict):
                raise LionTypeError(
                    expected_type=dict,
                    received_type=type(response),
                )

        dict_ = {}
        for k, v in response.items():
            if k in form.request_fields:

                kwargs = form.validation_kwargs.get(k, {})
                _annotation = form.field_getattr(k, "annotation")

                kwargs["annotation"] = _annotation
                if (keys := form.field_getattr(k, "keys", None)) is not None:
                    kwargs["keys"] = keys

                v = await self.process_field(k, v, progress=progress, **kwargs)

            dict_[k] = v

        form.fill_request_fields(**dict_)
        return form
