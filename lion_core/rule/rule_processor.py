from typing import Any, Callable

from lion_core.abc import BaseExecutor, Temporal, Observable
from lion_core.sys_utils import SysUtil
from lion_core.exceptions import LionTypeError, LionValueError
from lion_core.libs import ucall

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
        fallback_structure: Callable = None,
    ):
        self.ln_id = SysUtil.id()
        self.timestamp = SysUtil.time()
        self.strict = strict
        self.rulebook = rulebook or RuleBook()
        self.fallback_structure = fallback_structure

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

    async def process(
        self,
        form: Form,
        response: dict | str,
        progress=None,
        structure_str: bool = False,
        fallback_structure: Callable | None = None,
        **kwargs,  # additional kwargs for fallback_structure
    ):
        return await self.process_form(
            form,
            response,
            progress=progress,
            structure_str=structure_str,
            fallback_structure=fallback_structure,
            **kwargs,
        )

    async def process_form(
        self,
        form: Form,
        response: dict | str,
        progress=None,
        structure_str: bool = False,
        fallback_structure: Callable | None = None,
        **kwargs,  # additional kwargs for fallback_structure
    ):
        if isinstance(response, str):
            if len(form.request_fields) == 1:
                response = {form.request_fields[0]: response}
            else:
                if structure_str:
                    fallback_structure = fallback_structure or self.fallback_structure

                    if fallback_structure is None:
                        raise ValueError(
                            "Response is a string, you asked to structure the string"
                            "but no structure imodel was provided"
                        )
                    try:
                        response = await ucall(fallback_structure, response, **kwargs)
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
