from lionabc.exceptions import LionValueError
from lionfuncs import nget, note, to_dict

from lion_core.communication.action_request import ActionRequest
from lion_core.operative.operative import ActionRequestModel


def _extract_request_plain_function_calling(
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
    except Exception as e:
        if not suppress:
            raise ValueError(
                "Response message must be one of regular response or "
                "function calling"
            ) from e


def _extract_request_from_content_code_block(
    content_: list[dict],
) -> list[dict]:
    out = {}

    def _f(x: str):
        return x.replace("action_", "").replace("recipient_", "")

    def _inner(request_):
        if "recipient_name" in request_:
            out["action"] = request_["recipient_name"].split(".")[1]
        elif "function" in request_:
            out["action"] = request_["function"]

        if "parameters" in request_:
            out["arguments"] = request_["parameters"]
        elif "arguments" in request_:
            out["arguments"] = request_["arguments"]

        if isinstance(_arg := out.get("arguments"), str):
            if (
                a := to_dict(_arg, str_type="json", fuzzy_parse=True)
            ) is not None:
                out["arguments"] = a
            elif (a := to_dict(_arg, str_type="xml")) is not None:
                out["arguments"] = a

        return {"func": _f(out["action"]), "arguments": out["arguments"]}

    return [_inner(i) for i in content_]


def _extract_action_request(content_: list[dict]) -> list[ActionRequestModel]:
    outs = []

    def _f(x: str):
        return x.replace("action_", "").replace("recipient_", "")

    for request_ in content_:
        if "recipient_name" in request_:
            request_["action"] = request_.pop("recipient_name").split(".")[1]
        elif "function" in request_:
            request_["action"] = request_.pop("function")

        if "parameters" in request_:
            request_["arguments"] = request_["parameters"]
        elif "arguments" in request_:
            request_["arguments"] = request_["arguments"]

        msg = ActionRequestModel(
            function=_f(request_["action"]),
            arguments=request_["arguments"],
        )
        outs.append(msg)

    return outs


def create_action_request_model(
    response: str | dict,
) -> list[ActionRequest] | None:
    msg = note(**to_dict(response))

    content_ = None
    if str(msg.get(["content"], "")).strip().lower() == "none":
        content_ = _extract_request_plain_function_calling(msg, suppress=True)
    elif a := msg.get(["content", "tool_uses"], None):
        content_ = a
    else:
        content_ = _extract_request_from_content_code_block(msg)

    if content_:
        content_ = [content_] if isinstance(content_, dict) else content_
        return _extract_action_request(content_)

    _content = to_dict(msg["content"], fuzzy_parse=True, suppress=True)

    if _content and isinstance(_content, dict):
        if "action_request" in _content:
            content_ = _content["action_request"]
        if isinstance(content_, str):
            content_ = to_dict(content_, fuzzy_parse=True, suppress=True)
        if isinstance(content_, dict):
            content_ = [content_]
        if isinstance(content_, list):
            return _extract_action_request(content_)

    return None


def create_action_request(
    *,
    action_request_model: ActionRequestModel,
    sender,
    recipient,
    action_request: ActionRequest = None,
):
    if action_request:
        if not isinstance(action_request, ActionRequest):
            raise LionValueError(
                "Error: action request must be an instance of ActionRequest."
            )
        return action_request

    return ActionRequest(
        function=action_request_model.function,
        arguments=action_request_model.arguments,
        sender=sender,
        recipient=recipient,
    )
