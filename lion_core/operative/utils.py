import re

from lionfuncs import md_to_json, to_dict
from pydantic import BaseModel


def parse_action_request(content: str | dict) -> list[dict]:

    json_blocks = []

    if isinstance(content, BaseModel):
        json_blocks = [content.model_dump()]

    elif content and isinstance(content, dict):
        json_blocks = [content]

    elif isinstance(content, str):
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
        if isinstance(i, dict):
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
