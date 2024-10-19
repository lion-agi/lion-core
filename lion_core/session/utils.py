import logging
from typing import Literal

from lion_service import iModel
from lionfuncs import alcall, md_to_json
from pydantic import BaseModel

from lion_core.action.function_calling import FunctionCalling
from lion_core.communication.assistant_response import AssistantResponse
from lion_core.communication.instruction import Instruction
from lion_core.communication.message import RoledMessage
from lion_core.operative.operative import (
    ActionResponseModel,
    OperativeModel,
    StepModel,
)


async def _operate(
    branch=None,
    instruction=None,
    guidance=None,
    context=None,
    sender=None,
    recipient=None,
    operative_model: type[OperativeModel] = None,
    imodel: iModel = None,
    reason: bool = True,
    actions: bool = True,
    invoke_action: bool = True,
    messages: list[RoledMessage] = [],
    tool_schemas=None,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] = None,
    **kwargs,
):
    """
    additional payload to be passed into imodel api call
    """

    request_model: type[BaseModel] = StepModel.as_request_model(
        reason=reason, actions=actions, operative_model=operative_model
    )

    ins = Instruction(
        instruction=instruction,
        guidance=guidance,
        context=context,
        sender=sender,
        recipient=recipient,
        request_model=request_model,
        image_detail=image_detail,
        images=images,
    )
    if tool_schemas:
        ins.update_context(tool_schemas=tool_schemas)

    messages.append(ins)
    kwargs["messages"] = [m.chat_msg for m in messages]

    api_request = imodel.parse_to_data_model(**kwargs)
    api_response = await imodel.invoke(**api_request)
    res = AssistantResponse(
        assistant_response=api_response,
        sender=branch,
        recipient=None,
    )
    print(res.response)
    res.content["assistant_response"] = md_to_json(res.response)
    dict_ = res.content["assistant_response"]
    dict1 = {k: v for k, v in dict_.items() if k in request_model.model_fields}

    try:
        request_model = operative_model.model_validate(dict1)
    except Exception:
        request_model = request_model()

    if (
        actions
        and invoke_action
        and hasattr(request_model, "action_requests")
        and request_model.action_requests
    ):

        async def _invoke_action(i):
            tool = branch.tool_manager.registry.get(i.function, None)
            if tool:
                func_call = FunctionCalling(tool=tool, arguments=i.arguments)
                result = await func_call.invoke()
                return ActionResponseModel(
                    function=i.function, arguments=i.arguments, output=result
                )
            return None

        action_responses = alcall(
            request_model.action_requests, _invoke_action, dropna=True
        )
        dict_["action_responses"] = action_responses

    try:
        reponses_model = StepModel.parse_request_to_response(
            request=request_model, operative_model=operative_model, **dict_
        )
        return reponses_model, ins, res
    except Exception as e:
        logging.error(
            f"Failed to parse model response into operative model: {e}"
        )
        return dict_, ins, res


async def _chat(
    branch=None,
    instruction=None,
    guidance=None,
    context=None,
    sender=None,
    recipient=None,
    request_model: type[OperativeModel] = None,
    request_fields: dict = None,
    imodel: iModel = None,
    messages: list[RoledMessage] = [],
    tool_schemas=None,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] = None,
    **kwargs,
):
    if request_model and request_fields:
        raise ValueError("Cannot have both request_model and request_fields")

    ins = Instruction(
        instruction=instruction,
        guidance=guidance,
        context=context,
        sender=sender,
        recipient=recipient,
        request_model=request_model,
        image_detail=image_detail,
        images=images,
        request_fields=request_fields,
    )
    if tool_schemas:
        ins.update_context(tool_schemas=tool_schemas)

    messages.append(ins)
    kwargs["messages"] = [m.chat_msg for m in messages]

    api_request = imodel.parse_to_data_model(**kwargs)
    api_response = await imodel.invoke(**api_request)
    res = AssistantResponse(
        assistant_response=api_response,
        sender=branch,
        recipient=None,
    )
    if request_fields or request_model:
        try:
            res.content["assistant_response"] = md_to_json(res.response)
        except Exception:
            pass

    if request_model:
        try:
            reponses_model = request_model.model_validate(res.response)
            return reponses_model, ins, res
        except Exception as e:
            logging.error(
                f"Failed to parse model response into operative model: {e}"
            )
            return res.response, ins, res
    return res.response, ins, res
