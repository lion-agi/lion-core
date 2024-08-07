"""
Module for parsing chat completions and model responses in Lion framework.

Provides functionality to parse and process chat completions and model
responses, including handling of various JSON and XML formats.
"""

import re
from typing import Any, TYPE_CHECKING

from lion_core.libs import (
    to_dict,
    validate_mapping,
    fuzzy_parse_json,
    md_to_json,
    extract_json_block,
)
from lion_core.imodel.imodel import iModel

if TYPE_CHECKING:
    from lion_core.session.branch import Branch


async def parse_chatcompletion(
    branch: "Branch",
    imodel: iModel | None,
    payload: dict,
    completion: dict,
    sender: str,
    costs: tuple[float, float] | None = None,
) -> Any:
    """
    Parse chat completion and update the branch with the response.

    Args:
        branch: The Branch object to update.
        imodel: The iModel object to use for status updates.
        payload: The payload dictionary.
        completion: The completion dictionary from the AI model.
        sender: The sender of the message.
        costs: A tuple of prompt and completion token costs.

    Returns:
        The processed message or None.
    """
    msg_ = None
    imodel = imodel or branch.imodel

    if "choices" in completion:
        payload.pop("messages", None)
        branch.update_last_instruction_meta(payload)
        _choices = completion.pop("choices", None)

        def process_completion_choice(
            choice: dict, price: tuple[float, float] | None
        ) -> Any:
            if isinstance(choice, dict):
                msg = choice.pop("message", None)
                _completion = completion.copy()
                _completion.update(choice)
                branch.add_message(
                    assistant_response=msg,
                    metadata=_completion,
                    sender=sender,
                )
            a = branch.messages[-1].metadata.get(["extra", "usage", "prompt_tokens"], 0)
            b = branch.messages[-1].metadata.get(
                ["extra", "usage", "completion_tokens"], 0
            )
            m = completion.get("model")
            if m and price:
                ttl = (a * price[0] + b * price[1]) / 1_000_000
                branch.messages[-1].metadata.insert(["extra", "usage", "expense"], ttl)
            return msg

        if _choices and not isinstance(_choices, list):
            _choices = [_choices]

        if _choices and isinstance(_choices, list):
            for _choice in _choices:
                msg_ = process_completion_choice(_choice, price=costs)

        await imodel.update_status("chat/completions", "succeeded")
    else:
        await imodel.update_status("chat/completions", "failed")

    return msg_


def parse_model_response(
    content_: dict | str,
    request_fields: dict,
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    strict: bool = False,
) -> dict | str:
    """
    Parse the response from the AI model into dictionary format if possible.

    Args:
        content_: The content to parse, either a dictionary or a string.
        request_fields: The fields requested in the response.
        fill_value: The value to use for missing fields.
        fill_mapping: A mapping of field names to fill values.
        strict: Whether to use strict parsing.

    Returns:
        The parsed content as a dictionary or the original string if parsing
        fails.
    """
    out_ = content_.get("content", "") if isinstance(content_, dict) else content_

    if isinstance(out_, str):
        parsing_methods = [
            lambda x: to_dict(x, str_type="json", parser=md_to_json, surpress=True),
            lambda x: to_dict(
                x, str_type="json", parser=fuzzy_parse_json, surpress=True
            ),
            lambda x: to_dict(
                x, str_type="json", parser=extract_json_block, surpress=True
            ),
            lambda x: to_dict(x, str_type="xml"),
            lambda x: (
                fuzzy_parse_json(
                    re.search(r"```json\n({.*?})\n```", x, re.DOTALL).group(1),
                    surpress=True,
                )
                if re.search(r"```json\n({.*?})\n```", x, re.DOTALL)
                else None
            ),
            lambda x: (
                to_dict(
                    re.search(r"```xml\n({.*?})\n```", x, re.DOTALL).group(1),
                    str_type="xml",
                )
                if re.search(r"```xml\n({.*?})\n```", x, re.DOTALL)
                else None
            ),
            lambda x: fuzzy_parse_json(x.replace("'", '"'), surpress=True),
        ]

        for method in parsing_methods:
            try:
                a_ = method(out_)
                if a_ is not None:
                    out_ = a_
                    break
            except Exception:
                continue

    if isinstance(out_, dict) and request_fields:
        return validate_mapping(
            out_,
            request_fields,
            score_func=None,
            fuzzy_match=True,
            handle_unmatched="force",
            fill_value=fill_value,
            fill_mapping=fill_mapping,
            strict=strict,
        )

    return out_


__all__ = ["parse_chatcompletion", "parse_model_response"]

# File: lion_core/chat/parsing.py
