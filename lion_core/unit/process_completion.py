import re
from typing import Any

from lion_core.libs import (
    to_dict,
    validate_mapping,
    fuzzy_parse_json,
    md_to_json,
    extract_json_block,
)

from lion_core.session.branch import Branch
from lion_core.imodel.imodel import iModel


async def parse_chatcompletion(
    branch: Branch,
    imodel: iModel,
    payload: dict,
    completion: dict,
    sender: str,
    costs: tuple[float, float] | None = None,
) -> Any:
    msg_ = None
    imodel = imodel or branch.imodel

    if "choices" in completion:
        payload.pop("messages", None)
        branch.update_last_instruction_meta(payload)
        _choices = completion.pop("choices", None)

        def process_completion_choice(choice, price=None):
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
            m = completion.get("model", None)
            if m:
                ttl = (a * price[0] + b * price[1]) / 1_000_000
                branch.messages[-1].metadata.insert(["extra", "usage", "expense"], ttl)
            return msg

        if _choices and not isinstance(_choices, list):
            _choices = [_choices]

        if _choices and isinstance(_choices, list):
            for _choice in _choices:
                msg_ = process_completion_choice(_choice, price=costs)

        # the imodel.endpoints still needs doing
        await imodel.update_status("chat/completions", "succeeded")
    else:
        await imodel.update_status("chat/completions", "failed")

    return msg_


# parse the response directly from the AI model into dictionary format if possible
def parse_model_response(
    content_: dict | str,
    request_fields: dict,
    fill_value: Any = None,
    fill_mapping: dict[str, Any] | None = None,
    strict: bool = False,
) -> dict | str:

    out_ = content_.get("content", "")

    if isinstance(out_, str):

        # we will start with three different json parsers
        a_ = to_dict(out_, str_type="json", parser=md_to_json, surpress=True)
        if a_ is None:
            a_ = to_dict(out_, str_type="json", parser=fuzzy_parse_json, surpress=True)
        if a_ is None:
            a_ = to_dict(
                out_, str_type="json", parser=extract_json_block, surpress=True
            )

        # if still failed, we try with xml parser
        if a_ is None:
            try:
                a_ = to_dict(out_, str_type="xml")
            except ValueError:
                a_ = None

        # if still failed, we try with using regex to extract json block
        if a_ is None:
            match = re.search(r"```json\n({.*?})\n```", out_, re.DOTALL)
            if match:
                a_ = match.group(1)
                a_ = fuzzy_parse_json(a_, surpress=True)

        # if still failed, we try with using regex to extract xml block
        if a_ is None:
            match = re.search(r"```xml\n({.*?})\n```", out_, re.DOTALL)
            if match:
                a_ = match.group(1)
                try:
                    a_ = to_dict(out_, str_type="xml")
                except ValueError:
                    a_ = None

        # we try replacing single quotes with double quotes
        if a_ is None:
            a_ = fuzzy_parse_json(out_.replace("'", '"'), surpress=True)

        # we give up here if still not succesfully parsed into a dictionary
        if a_:
            out_ = a_

    # we will forcefully correct the format of the dictionary
    # with all missing fields filled with fill_value or fill_mapping
    if isinstance(out_, dict) and request_fields:
        return validate_mapping(
            a_,
            request_fields,
            score_func=None,
            fuzzy_match=True,
            handle_unmatched="force",
            fill_value=fill_value,
            fill_mapping=fill_mapping,
            strict=strict,
        )

    return out_
