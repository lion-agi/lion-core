from typing import Any, Callable, Literal
from lion_core.sys_utils import SysUtil
from lion_core.generic import Note
from lion_core.libs import fuzzy_parse_json, to_str, to_dict
from lion_core.exceptions import LionIDError, LionValueError

DEFAULT_SYSTEM = "You are a helpful AI assistant. Let's think step by step."


def prepare_action_request(func: str | Callable, arguments: dict) -> Note:

    def _prepare_arguments(_arg: Any) -> dict[str, Any]:
        """Prepare and validate the arguments for an action request."""
        if not isinstance(_arg, dict):
            try:
                _arg = to_dict(to_str(_arg), str_type="json", parser=fuzzy_parse_json)
            except ValueError:
                _arg = to_dict(to_str(_arg), str_type="xml")
            except Exception as e:
                raise ValueError(f"Invalid arguments: {e}") from e

        if isinstance(arguments, dict):
            return arguments
        raise ValueError(f"Invalid arguments: {arguments}")

    arguments = _prepare_arguments(arguments)
    return Note(**{"action_request": {"function": func, "arguments": arguments}})


def validate_sender_recipient(value: Any) -> str:
    """Validate the sender and recipient fields."""
    if value in ["system", "user", "N/A", "assistant"]:
        return value

    if value is None:
        return "N/A"

    try:
        return SysUtil.get_id(value)
    except LionIDError as e:
        raise LionValueError(f"Invalid sender or recipient") from e


def format_requested_fields(requested_fields: dict) -> dict:
    format_ = f"""
    MUST RETURN JSON-PARSEABLE RESPONSE ENCLOSED BY JSON CODE BLOCKS. ---
    ```json
    {requested_fields}
    ```---
    """
    return {"response_format": format_.strip()}


def prepare_instruction_content(
    instruction: str | None = None,
    context: str | dict | list | None = None,
    images: str | list | None = None,
    requested_fields: dict | None = None,
    image_detail: str | None = None,
):
    if image_detail:
        if image_detail not in ["low", "high", "auto"]:
            image_detail = "auto"

    content_dict = {
        "instruction": instruction or "N/A",
        "context": context,
        "images": (
            (images if isinstance(images, list) else [images]) if images else None
        ),
        "image_detail": (image_detail or "low") if images else None,
        "requested_fields": (
            format_requested_fields(requested_fields) if requested_fields else None
        ),
    }

    content = Note()
    for k, v in content_dict.items():
        if v is not None:
            content.set(k, v)
    return content


def format_image_content(
    text_content: str, images: list, image_detail: Literal["low", "high", "auto"]
):

    content = [{"type": "text", "text": text_content}]

    for i in images:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{i}",
                    "detail": image_detail,
                },
            }
        )
    return content


def format_system_content(with_datetime: bool | str | None, _str) -> Note:
    _str = _str or DEFAULT_SYSTEM
    if not with_datetime:
        return Note(**{"system_info": str(_str)})
    if isinstance(with_datetime, str):
        return Note(**{"system_info": f"{_str}. System Date: {with_datetime}"})
    if with_datetime:
        return Note(
            **{
                "system_info": f"{_str}. System Date: {SysUtil.time(type_='iso', timespec='minutes')}"
            }
        )
