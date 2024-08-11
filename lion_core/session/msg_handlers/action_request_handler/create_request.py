from lion_core.generic.note import note
from lion_core.communication.action_request import ActionRequest
from lion_core.libs import to_dict, strip_lower, fuzzy_parse_json

from lion_core.session.msg_handlers.action_request_handler.extract_request import (
    extract_request_from_content_code_block,
    extract_request_plain_function_calling,
    extract_action_request,
)


def create_action_request(response: str | dict) -> list[ActionRequest] | None:
    msg = note(**to_dict(response))

    content_ = None
    if strip_lower(msg.get(["content"], "")) == "none":
        content_ = extract_request_plain_function_calling(msg, suppress=True)
    elif a := msg.get(["content", "tool_uses"], None):
        content_ = a
    else:
        content_ = extract_request_from_content_code_block(msg)

    if content_:
        content_ = [content_] if isinstance(content_, dict) else content_
        return extract_action_request(content_)

    _content = to_dict(msg["content"], parser=fuzzy_parse_json, surpress=True)

    if _content and isinstance(_content, dict):
        if "action_request" in _content:
            content_ = _content["action_request"]
        if isinstance(content_, str):
            content_ = to_dict(content_, parser=fuzzy_parse_json, surpress=True)
        if isinstance(content_, dict):
            content_ = [content_]
        if isinstance(content_, list):
            return extract_action_request(content_)

    return None