import re

from lionfuncs import copy, md_to_json, to_dict


def parse_action_request(content: str) -> list[dict]:

    json_blocks = md_to_json(
        str_to_parse=content,
        as_jsonl=True,
        suppress=True,
    )

    if not json_blocks:
        pattern2 = r"```python\s*(.*?)\s*```"
        _d = re.findall(pattern2, content, re.DOTALL)
        json_blocks = [
            to_dict(match, fuzzy_parse=True, suppress=True) for match in _d
        ]
        json_blocks = [i for i in json_blocks if i]

    out = []

    for i in json_blocks:
        j = {}
        for k, v in i.items():
            k = (
                k.replace("action_", "")
                .replace("recipient_", "")
                .replace("s", "")
            )
            if k in ["name", "function", "recipient"]:
                j["function"] = v
            elif k in ["parameter", "argument", "arg"]:
                j["arguments"] = to_dict(
                    v, str_type="json", fuzzy_parse=True, suppress=True
                )
        if (
            j
            and all(key in j for key in ["function", "arguments"])
            and j["arguments"]
        ):
            out.append(j)

    return out


def prepare_fields(
    exclude_fields: list | dict | None = None,
    include_fields: list | dict | None = None,
    **kwargs,
):
    kwargs = copy(kwargs)

    if exclude_fields:
        exclude_fields = (
            list(exclude_fields.keys())
            if isinstance(exclude_fields, dict)
            else exclude_fields
        )

    if include_fields:
        include_fields = (
            list(include_fields.keys())
            if isinstance(include_fields, dict)
            else include_fields
        )

    if exclude_fields and include_fields:
        for i in include_fields:
            if i in exclude_fields:
                raise ValueError(
                    f"Field {i} is repeated. Operation include "
                    "fields and exclude fields cannot have common elements."
                )

    if exclude_fields:
        for i in exclude_fields:
            kwargs.pop(i, None)

    if include_fields:
        for i in list(kwargs.keys()):
            if i not in include_fields:
                kwargs.pop(i, None)

    return {k: (v.annotation, v) for k, v in kwargs.items()}
