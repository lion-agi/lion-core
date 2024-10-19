import logging
from typing import Literal

from lion_service import iModel
from lionfuncs import alcall, copy, md_to_json, to_dict, validate_mapping
from pydantic import BaseModel

from lion_core.action.function_calling import FunctionCalling
from lion_core.communication.assistant_response import AssistantResponse
from lion_core.communication.instruction import Instruction
from lion_core.communication.message import RoledMessage
from lion_core.operative.operative import (
    ActionRequestModel,
    ActionResponseModel,
    OperativeModel,
    StepModel,
)


async def _invoke_action(i: ActionRequestModel, branch=None):
    tool = branch.tool_manager.registry.get(i.function, None)
    if tool:
        func_call = FunctionCalling(tool, arguments=i.arguments)
        result = await func_call.invoke()
        return ActionResponseModel(
            function=i.function, arguments=i.arguments, output=result
        )
    return None


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
    handle_unmatched: Literal[
        "ignore", "raise", "remove", "fill", "force"
    ] = "force",
    **kwargs,
):
    """
    additional payload to be passed into imodel api call
    """

    request_model: type[BaseModel] = StepModel.as_request_model(
        reason=reason, actions=actions, operative_model=operative_model
    )

    ins = None
    if isinstance(instruction, Instruction):
        ins = instruction
        if context:
            ins.update_context(context)
        if images:
            ins.update_images(images=images, image_detail=image_detail)
        if guidance:
            ins.update_guidance(guidance)
    else:
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
        recipient=branch.user,
    )
    res.content["assistant_response"] = validate_mapping(
        res.response,
        request_model.model_fields,
        handle_unmatched=handle_unmatched,
    )
    dict_ = copy(res.content["assistant_response"])

    try:
        request_model = request_model.model_validate(dict_)
    except Exception:
        request_model = request_model()

    if (
        actions
        and invoke_action
        and hasattr(request_model, "action_required")
        and request_model.action_required
        and hasattr(request_model, "action_requests")
        and request_model.action_requests
    ):

        action_responses = await alcall(
            request_model.action_requests, _invoke_action, branch=branch
        )
        action_responses = [to_dict(i) for i in action_responses if i]
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

    ins = None
    if isinstance(instruction, Instruction):
        if context:
            instruction.update_context(context)

        if request_model:
            schema = request_model.model_json_schema()
            request_fields = schema.pop("properties")
            instruction.update_context(respond_schema_info=schema)

        if request_fields:
            instruction.update_request_fields(request_fields=request_fields)
        if images:
            instruction.update_images(images=images, image_detail=image_detail)
        if guidance:
            instruction.update_guidance(guidance)
        ins = instruction

    else:
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
        guide = ins.guidance or ""
        guide += "\n\nwhen providing function arguments, please use "
        guide += "the following format:\n\n"
        guide += "{'function': ..., 'arguments': {...}}\n\n"
        ins.update_guidance(guide)

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
