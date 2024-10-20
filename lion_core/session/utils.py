import logging
from typing import Literal

from lion_service import iModel
from lionfuncs import md_to_json
from pydantic import BaseModel

from lion_core.communication.assistant_response import AssistantResponse
from lion_core.communication.instruction import Instruction
from lion_core.communication.message import RoledMessage

RETRY_PROMPT = (
    "the following text is of invalid format. \n\n {response}"
    "please provide a valid JSON-PARSABLE response format according "
    "to the following model\n\n ```json\n{request_model}\n``` \n\n"
)


async def _chat(
    branch=None,
    instruction=None,
    guidance=None,
    context=None,
    sender=None,
    recipient=None,
    request_model: type[BaseModel] = None,
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


# async def _chat(
#     self,
#     instruction=None,
#     guidance=None,
#     context=None,
#     sender=None,
#     recipient=None,
#     request_model: type[BaseModel] = None,
#     request_fields: dict = None,
#     progress = None,
#     imodel: iModel = None,
#     messages: list[RoledMessage] = [],
#     tool_schemas=None,
#     images: list = None,
#     image_detail: Literal["low", "high", "auto"] = None,
#     **kwargs,
# ) -> BaseModel | str | dict:
#     if request_model and request_fields:
#         raise ValueError("Cannot have both request_model and request_fields")
#     ins = None
#     if isinstance(instruction, Instruction):
#         ins = instruction
#         ins.update_request_model(request_model)
#         if context:
#             ins.update_context(context)
#         if images:
#             ins.update_images(images=images, image_detail=image_detail)
#         if guidance:
#             ins.update_guidance(guidance)
#     else:
#         ins = Instruction(
#             instruction=instruction,
#             guidance=guidance,
#             context=context,
#             sender=sender,
#             recipient=recipient,
#             request_model=request_model,
#             image_detail=image_detail,
#             images=images,
#         )
#     if tool_schemas:
#         ins.update_context(tool_schemas=tool_schemas)
#         guide = ins.guidance or ""
#         guide += "\n\nwhen providing function arguments, please use "
#         guide += "the following format:\n\n"
#         guide += "{'function': ..., 'arguments': {...}}\n\n"
#         ins.update_guidance(guide)

#     messages = [self.messages[i] for i in (progress or self.progress)]
#     messages.append(ins)
#     kwargs["messages"] = [m.chat_msg for m in messages]

#     imodel = imodel or self.imodel
#     api_request = imodel.parse_to_data_model(**kwargs)
#     api_response = await imodel.invoke(**api_request)
#     res = AssistantResponse(
#         assistant_response=api_response,
#         sender=self,
#         recipient=self.user,
#     )
#     self.add_message(instruction=ins)
#     self.add_message(assistant_response=res)

#     if request_fields or request_model:
#         try:
#             dict_ = md_to_json(res.response)
#             res.content["assistant_response"] = copy(dict_)
#         except Exception:
#             pass

#     if request_model:
#         try:
#             res1 = res.content["assistant_response"]
#             return request_model.model_validate(res1)
#         except Exception as e:
#             logging.error(
#                 f"Failed to parse model response into operative model: {e}"
#             )

#     return res.content["assistant_response"]
