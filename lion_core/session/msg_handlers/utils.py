import re

from lionfuncs import to_json, to_list
from pydantic import BaseModel

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


def parse_action_request(content: str) -> list[dict]:
    """
    return [{"function": "function_name", "arguments": {...}}, ...]
    """
    json_blocks = _prepare_response(content)
    return _parse_action_request(json_blocks)


def _prepare_response(content: str | dict | BaseModel) -> list[dict | str]:

    if isinstance(content, BaseModel):
        return [content.model_dump()]

    elif content and isinstance(content, dict):
        return [content]

    try:
        return to_list(to_json(content, fuzzy_parse=True), flatten=True)
    except Exception:
        pass

    try:
        pattern2 = r"```python\s*(.*?)\s*```"
        json_blocks = re.findall(pattern2, content, re.DOTALL)
        return to_list(to_json(json_blocks, fuzzy_parse=True), flatten=True)
    except Exception:
        return []


def _parse_action_request(json_blocks: list[dict]) -> list[dict]:
    if not json_blocks:
        return []

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
                    j["arguments"] = v
            if list(j.keys()) == ["function", "arguments"]:
                out.append(j)

    return out
