import json
import re
import contextlib
from lion_core.communication.action_request import ActionRequest
from lion_core.generic.note import Note, note
from lion_core.libs import (
    to_dict,
    strip_lower,
    nget,
    fuzzy_parse_json,
    md_to_json,
    extract_json_block,
)


def extract_request_plain_function_calling(
    response: dict,
    suppress=False,
) -> list[dict]:
    """Handles the action request parsing from the response."""
    try:
        tool_count = 0
        func_list = []
        while tool_count < len(response["tool_calls"]):
            _path = ["tool_calls", tool_count, "type"]

            if nget(response, _path) == "function":
                _path1 = ["tool_calls", tool_count, "function", "name"]
                _path2 = ["tool_calls", tool_count, "function", "arguments"]

                func_content = {
                    "action": f"action_{nget(response, _path1)}",
                    "arguments": nget(response, _path2),
                }
                func_list.append(func_content)
            tool_count += 1
        return func_list
    except:
        if not suppress:
            raise ValueError(
                "Response message must be one of regular response or function calling"
            )


def extract_request_from_content_code_block(content_: list[dict]) -> list[dict]:
    out = {}

    def _inner(request_):
        if "recipient_name" in request_:
            out["action"] = request_["recipient_name"].split(".")[1]
        elif "function" in request_:
            out["action"] = request_["function"]

        if "parameters" in request_:
            out["arguments"] = request_["parameters"]
        elif "arguments" in request_:
            out["arguments"] = request_["arguments"]

        if isinstance((_arg := out.get("arguments")), str):
            if (
                a := to_dict(_arg, str_type="json", parser=fuzzy_parse_json)
            ) is not None:
                out["arguments"] = a
            elif (a := to_dict(_arg, str_type="xml")) is not None:
                out["arguments"] = a

        _f = lambda x: x.replace("action_", "").replace("recipient_", "")
        return {"func": _f(out["action"]), "arguments": out["arguments"]}

    return [_inner(i) for i in content_]


def extract_action_request(content_: list[dict]) -> list[ActionRequest]:
    outs = []
    for request_ in content_:
        if "recipient_name" in request_:
            request_["action"] = request_.pop("recipient_name").split(".")[1]
        elif "function" in request_:
            request_["action"] = request_.pop("function")

        if "parameters" in request_:
            request_["arguments"] = request_["parameters"]
        elif "arguments" in request_:
            request_["arguments"] = request_["arguments"]

        f = lambda x: x.replace("action_", "").replace("recipient_", "")

        msg = ActionRequest(
            func=f(request_["action"]),
            arguments=request_["arguments"],
        )
        outs.append(msg)

    return outs