import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any, Literal

import pandas as pd
from lion_service import iModel
from lionabc import Traversal
from lionfuncs import (
    alcall,
    break_down_pydantic_annotation,
    copy,
    is_same_dtype,
    to_dict,
    validate_mapping,
)
from pydantic import BaseModel, Field, model_validator

from lion_core.action import FunctionCalling, Tool, ToolManager
from lion_core.communication import (
    ActionRequest,
    ActionResponse,
    AssistantResponse,
    Instruction,
    Mail,
    Package,
    RoledMessage,
    System,
)

# from lion_core.converter import ConverterRegistry
from lion_core.generic import Exchange, Pile, Progression, progression
from lion_core.generic.base import RealElement
from lion_core.operative.action_model import (
    ActionRequestModel,
    ActionResponseModel,
)
from lion_core.operative.step_model import StepModel
from lion_core.session.base import BaseSession
from lion_core.session.msg_handlers import (
    create_action_request_model,
    create_message,
    validate_message,
)
from lion_core.session.utils import RETRY_PROMPT, _chat
from lion_core.setting import TimedFuncCallConfig

# class BranchConverterRegistry(ConverterRegistry):
#     """Registry for Branch converters."""

#     pass

MESSAGE_FIELDS = [
    "timestamp",
    "lion_class",
    "role",
    "content",
    "ln_id",
    "sender",
    "recipient",
    "metadata",
]


class Branch(BaseSession, Traversal):
    """
    Represents a branch in the conversation tree with tools and messages.

    This class manages a conversation branch, including messages, tools,
    and communication within the branch.

    Attributes:
        messages (Pile): Collection of messages in the branch.
        tool_manager (ToolManager): Manages tools available in the branch.
        mailbox (Exchange): Handles mail communication for the branch.
        progress (Progression): Tracks the order of messages.
        system (System | None): System message for the branch.
        user (str): Identifier for the user in the conversation.
        imodel (iModel | None): AI model associated with the branch.
        operative_model (type[BaseModel] | None): Model for operation results.
    """

    messages: Pile | None = Field(default_factory=Pile)
    tool_manager: ToolManager | None = Field(default_factory=ToolManager)
    mailbox: Exchange | None = Field(default_factory=Exchange)
    progress: Progression | None = Field(default_factory=progression)
    system: System | None = None
    user: str | None = "user"
    imodel: iModel | None = None
    operative_model: type[BaseModel] | None = BaseModel

    # _converter_registry: ClassVar = BranchConverterRegistry

    @model_validator(mode="before")
    def _validate_input(cls, data: dict) -> dict:
        messages = data.pop("messages", None)

        data["messages"] = Pile(
            validate_message(messages),
            {RoledMessage},
            strict=False,
        )
        data["progress"] = progression(
            list(data.pop("messages", [])),
        )
        data["tool_manager"] = data.pop(
            "tool_manager",
            ToolManager(),
        )
        data["mailbox"] = data.pop(
            "mailbox",
            Exchange(),
        )
        if "tools" in data:
            tool_manager = data.get("tool_manager", None)
            tool_manager = tool_manager or ToolManager()
            tool_manager.register_tools(data.pop("tools"))
            data["tool_manager"] = tool_manager
        return cls.validate_system(data)

    @model_validator(mode="after")
    def _check_system(self):
        if self.system is None:
            return self
        if self.system not in self.messages:
            self.messages.include(self.system)
            self.progress.insert(0, self.system)
        return self

    def set_system(self, system: System) -> None:
        """
        Sets or updates the system message for the branch.

        Args:
            system (System): The new system message to set.
        """
        if len(self.progress) < 1:
            self.messages.include(system)
            self.system = system
            self.progress[0] = self.system
        else:
            self._change_system(system, delete_previous_system=True)
            self.progress[0] = self.system

    def add_message(
        self,
        *,
        sender=None,
        recipient=None,
        instruction=None,
        context=None,
        guidance=None,
        request_fields=None,
        system=None,
        system_sender=None,
        system_datetime=None,
        images=None,
        image_detail=None,
        assistant_response=None,
        action_request: ActionRequest = None,
        action_response: ActionResponse = None,
        action_request_model=None,
        action_response_model=None,
        delete_previous_system: bool = None,
        metadata=None,
    ):
        """
        Adds a new message to the branch.

        Supports various message types including instructions, system messages,
        assistant responses, and action requests/responses.

        Args:
            **kwargs: Keyword arguments for message creation.
        """

        _msg = create_message(
            sender=sender,
            recipient=recipient,
            instruction=instruction,
            context=context,
            guidance=guidance,
            request_fields=request_fields,
            system=system,
            system_sender=system_sender,
            system_datetime=system_datetime,
            images=images,
            image_detail=image_detail,
            assistant_response=assistant_response,
            action_request=action_request,
            action_response=action_response,
            action_request_model=action_request_model,
            action_response_model=action_response_model,
        )

        if isinstance(_msg, System):
            _msg.recipient = (
                self.ln_id
            )  # the branch itself, system is to the branch
            self._change_system(
                system=_msg,
                delete_previous_system=delete_previous_system,
            )

        if isinstance(_msg, Instruction):
            _msg.sender = sender or self.user
            _msg.recipient = recipient or self.ln_id

        if isinstance(_msg, AssistantResponse):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or self.user or "user"

        if isinstance(_msg, ActionRequest):
            _msg.sender = sender or self.ln_id
            _msg.recipient = recipient or "N/A"

        if isinstance(_msg, ActionResponse):
            _msg.sender = sender or "N/A"
            _msg.recipient = recipient or self.ln_id

        if metadata:
            _msg.metadata.update(metadata, ["extra"])

        self.messages.include(_msg)

    def clear_messages(self) -> None:
        """Clears all messages from the branch except the system message."""
        self.messages.clear()
        self.progress.clear()
        if self.system:
            self.messages.include(self.system)
            self.progress.insert(0, self.system)

    def _change_system(
        self,
        system: System,
        delete_previous_system: bool = False,
    ):
        """
        Change the system message.

        Args:
            system: The new system message.
            delete_previous_system: If True, delete the previous system
                message.
        """
        old_system = self.system
        self.system = system
        self.messages.insert(0, self.system)

        if delete_previous_system:
            self.messages.exclude(old_system)

    def send(
        self,
        recipient: str,
        category: str,
        package: Any,
        request_source: str,
    ) -> None:
        """
        Sends a mail to a recipient.

        Args:
            recipient (str): The recipient's ID.
            category (str): The category of the mail.
            package (Any): The content of the mail.
            request_source (str): The source of the request.
        """
        package = Package(
            category=category,
            package=package,
            request_source=request_source,
        )

        mail = Mail(
            sender=self.ln_id,
            recipient=recipient,
            package=package,
        )
        self.mailbox.include(mail, "out")

    def receive(
        self,
        sender: str,
        message: bool = False,
        tool: bool = False,
        imodel: bool = False,
    ) -> None:
        """
        Receives mail from a sender.

        Args:
            sender (str): The ID of the sender.
            message (bool): Whether to process message mails.
            tool (bool): Whether to process tool mails.
            imodel (bool): Whether to process imodel mails.

        Raises:
            ValueError: If the sender does not exist or the mail category is
            invalid.
        """
        skipped_requests = progression()
        if sender not in self.mailbox.pending_ins.keys():
            raise ValueError(f"No package from {sender}")
        while self.mailbox.pending_ins[sender].size() > 0:
            mail_id = self.mailbox.pending_ins[sender].popleft()
            mail: Mail = self.mailbox.pile_[mail_id]

            if mail.category == "message" and message:
                if not isinstance(mail.package.package, RoledMessage):
                    raise ValueError("Invalid message format")
                new_message = mail.package.package.clone()
                new_message.sender = mail.sender
                new_message.recipient = self.ln_id
                self.messages.include(new_message)
                self.mailbox.pile_.pop(mail_id)

            elif mail.category == "tool" and tool:
                if not isinstance(mail.package.package, Tool):
                    raise ValueError("Invalid tools format")
                self.tool_manager.register_tools(mail.package.package)
                self.mailbox.pile_.pop(mail_id)

            elif mail.category == "imodel" and imodel:
                if not isinstance(mail.package.package, iModel):
                    raise ValueError("Invalid iModel format")
                self.imodel = mail.package.package
                self.mailbox.pile_.pop(mail_id)

            else:
                skipped_requests.append(mail)

        self.mailbox.pending_ins[sender] = skipped_requests

        if self.mailbox.pending_ins[sender].size() == 0:
            self.mailbox.pending_ins.pop(sender)

    def receive_all(self) -> None:
        """Receives mail from all senders."""
        for key in list(self.mailbox.pending_ins.keys()):
            self.receive(key)

    @property
    def last_response(self) -> AssistantResponse | None:
        """
        Retrieves the last assistant response in the branch.

        Returns:
            AssistantResponse | None: The last assistant response, if any.
        """
        for i in reversed(self.progress):
            if isinstance(self.messages[i], AssistantResponse):
                return self.messages[i]

    @property
    def assistant_responses(self) -> Pile:
        """
        Retrieves all assistant responses in the branch.

        Returns:
            Pile: A Pile containing all assistant responses.
        """
        return Pile(
            [
                self.messages[i]
                for i in self.progress
                if isinstance(self.messages[i], AssistantResponse)
            ]
        )

    @property
    def action_requests(self) -> Pile:
        """
        Retrieves all action requests in the branch.

        Returns:
            Pile: A Pile containing all action requests.
        """
        return Pile(
            [
                self.messages[i]
                for i in self.progress
                if isinstance(self.messages[i], ActionRequest)
            ]
        )

    @property
    def action_responses(self) -> Pile:
        """
        Retrieves all action responses in the branch.

        Returns:
            Pile: A Pile containing all action responses.
        """
        return Pile(
            [
                self.messages[i]
                for i in self.progress
                if isinstance(self.messages[i], ActionResponse)
            ]
        )

    @property
    def instructions(self) -> Pile:
        """
        Retrieves all instructions in the branch.

        Returns:
            Pile: A Pile containing all instructions.
        """
        return Pile(
            [
                self.messages[i]
                for i in self.progress
                if isinstance(self.messages[i], Instruction)
            ]
        )

    def has_tools(self) -> bool:
        """
        Checks if the branch has any registered tools.

        Returns:
            bool: True if tools are registered, False otherwise.
        """
        return self.tool_manager.registry != {}

    def register_tools(self, tools: Any, update: bool = False) -> None:
        """
        Registers new tools to the tool manager.

        Args:
            tools (Any): Tools to be registered.
        """
        self.tool_manager.register_tools(tools=tools, update=update)

    def delete_tools(self, tools: Any, verbose: bool = True) -> bool:
        """
        Deletes specified tools from the tool manager.

        Args:
            tools (Any): Tools to be deleted.
            verbose (bool): If True, print status messages.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not isinstance(tools, list):
            tools = [tools]
        if is_same_dtype(input_=tools, dtype=str):
            for act_ in tools:
                if act_ in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_)
            if verbose:
                print("tools successfully deleted")
            return True
        elif is_same_dtype(input_=tools, dtype=Tool):
            for act_ in tools:
                if act_.function_name in self.tool_manager.registry:
                    self.tool_manager.registry.pop(act_.function_name)
            if verbose:
                print("tools successfully deleted")
            return True
        if verbose:
            print("tools deletion failed")
        return False

    def to_chat_messages(self, progress=None) -> list[dict[str, Any]]:
        """
        Converts messages to a list of chat message dictionaries.

        Args:
            progress (Progression, optional): Specific progression to convert.

        Returns:
            list[dict[str, Any]]: A list of chat message dictionaries.

        Raises:
            ValueError: If the provided progress is invalid.
        """
        if not all(i in self.messages for i in (progress or self.progress)):
            raise ValueError("Invalid progress")
        return [self.messages[i].chat_msg for i in (progress or self.progress)]

    async def operate(
        self,
        instruction=None,
        guidance=None,
        context=None,
        sender=None,
        recipient=None,
        progress: Progression = None,
        operative_model: type[BaseModel] = None,
        imodel: iModel = None,
        reason: bool = True,
        actions: bool = False,
        tools: Any = None,
        invoke_action: bool = True,
        num_parse_retries: int = 0,
        retry_imodel: iModel = None,
        handle_validation: Literal[
            "raise", "return_value", "return_none"
        ] = "return_value",
        skip_validation: bool = False,
        handle_unmatched: Literal[
            "ignore", "raise", "remove", "fill", "force"
        ] = "force",
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        clear_messages: bool = False,
        action_timed_config: dict | TimedFuncCallConfig | None = None,
        **kwargs,
    ) -> BaseModel:

        if clear_messages:
            self.clear_messages()

        tool_schemas = None
        if tools:
            tools = tools if isinstance(tools, list) else [tools]
            for i in tools:
                if (
                    isinstance(i, Tool | Callable)
                    and i not in self.tool_manager
                ):
                    self.tool_manager.register_tools(i)
            tool_schemas = self.tool_manager.get_tool_schema(tools)

        if num_parse_retries > 10:
            logging.warning(
                f"Are you sure you want to retry {num_parse_retries} "
                "times? lowering retry attempts to 10. Suggestion is under 3"
            )
            num_parse_retries = 10

        response_model = await self._operate(
            self=self,
            instruction=instruction,
            guidance=guidance,
            context=context,
            sender=sender,
            recipient=recipient,
            operative_model=operative_model or self.operative_model,
            progress=progress,
            imodel=imodel or self.imodel,
            reason=reason,
            actions=actions,
            tool_schemas=tool_schemas,
            images=images,
            image_detail=image_detail,
            handle_unmatched=handle_unmatched,
            num_parse_retries=num_parse_retries,
            retry_imodel=retry_imodel,
            **kwargs,
        )

        if skip_validation:
            return response_model

        if isinstance(response_model, dict | str):
            if handle_validation == "raise":
                request_model: type[BaseModel] = StepModel.as_request_model(
                    reason=reason,
                    actions=actions,
                    operative_model=operative_model,
                )
                raise ValueError(
                    "Operative model validation failed. iModel response"
                    " not parsed into operative model:"
                    f" {request_model.__name__}"
                )
            if handle_validation == "return_none":
                return None
            if handle_validation == "return_value":
                return response_model

        if (
            actions
            and invoke_action
            and hasattr(request_model, "action_required")
            and request_model.action_required
            and hasattr(request_model, "action_requests")
            and request_model.action_requests
        ):
            action_requests = request_model.action_requests
            action_response_models = await alcall(
                action_requests,
                self.invoke_action,
                suppress_errors=True,
                timed_config=action_timed_config,
            )
            dict_ = response_model.model_dump()
            action_response_models = [
                to_dict(i) for i in action_response_models if i
            ]
            dict_["action_responses"] = action_response_models

            try:
                response_model = StepModel.parse_request_to_response(
                    request=request_model,
                    operative_model=operative_model,
                    **dict_,
                )
            except Exception as e:
                logging.error(
                    f"Failed to parse model response into operative model: {e}"
                )

        elif (
            hasattr(request_model, "action_requests")
            and request_model.action_requests
        ):
            for i in request_model.action_requests:
                i = to_dict(i)
                act_req = ActionRequest(
                    function=i["function"],
                    arguments=i["arguments"],
                    sender=self,
                )
                self.add_message(
                    action_request=act_req,
                    sender=act_req.sender,
                    recipient=None,
                )

        return response_model

    async def invoke_action(
        self,
        action_request_model: ActionRequestModel = None,
        action_request: ActionRequest = None,
        timed_config: dict | TimedFuncCallConfig | None = None,
        suppress_errors: bool = False,
    ) -> ActionResponseModel:
        try:
            if action_request and action_request_model:
                raise ValueError(
                    "Cannot have both action_request and action_request_model"
                )
            if not action_request and not action_request_model:
                raise ValueError(
                    "Either action_request or action_request_model must "
                    "be provided"
                )

            if not action_request:
                action_request = action_request_model.to_message()

            if not action_request_model:
                action_request_model = ActionRequestModel.parse_to_model(
                    action_request_message=action_request,
                )

            tool: Tool = self.tool_manager.registry.get(
                action_request.function
            )
            if action_request not in self.messages:
                self.add_message(
                    action_request=action_request,
                    sender=self,
                    recipient=tool.ln_id,
                )
            func_call = FunctionCalling(
                func_tool=tool,
                arguments=action_request.arguments,
                timed_config=timed_config,
            )
            result = await func_call.invoke()
            action_response_model = ActionResponseModel.parse_to_model(
                action_request_message=action_request, output=result
            )
            action_response = action_response_model.to_message(
                action_request_message=action_request,
                func_call=func_call,
            )
            self.add_message(
                action_response=action_response,
                sender=tool.ln_id,
                recipient=self,
            )
            return action_response_model
        except Exception as e:
            if suppress_errors:
                logging.error(f"Failed to invoke action: {e}")
                return None
            raise e

    async def chat(
        self,
        instruction: Any = None,
        guidance: str | dict | list = None,
        context: str | dict | list = None,
        sender: RealElement | str | None = None,
        recipient: RealElement | str | None = None,
        progress: Progression | list | None = None,
        request_model: type[BaseModel] = None,
        request_fields: dict = None,
        imodel: iModel = None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        tools: Any = None,
        num_parse_retries: int = 0,
        retry_imodel: iModel = None,
        handle_validation: Literal[
            "raise", "return_value", "return_none"
        ] = "return_value",
        skip_validation: bool = False,
        clear_messages: bool = False,
        invoke_action: bool = False,
        **kwargs,
    ) -> str | dict | BaseModel:
        """
        Initiates a chat interaction in the branch using AI models and tools.

        This method processes a chat interaction, potentially invoking AI model
        and tools based on the conversation. It can handle various types of
        inputs and outputs, including structured data and images.

        Args:
            instruction (Any): The main instruction or query for the chat.
            guidance (Any): Additional guidance for the AI model.
            context (Any): Context information for the chat.
            sender (Any): The sender of the message.
            recipient (Any): The intended recipient of the message.
            progress (Progression): Specific conversation progress to use.
            request_model (type[BaseModel]): Pydantic model for structured
                output
            request_fields (dict): Fields to request in the output.
            imodel (iModel): The AI model to use for generation.
            images (list): List of images to include in the chat.
            image_detail (Literal["low", "high", "auto"], optional):
                Image detail level.
            tools (Any): Tools to make available for the chat.
            num_parse_retries (int): Number of retries for parsing the response
            retry_imodel (iModel): Alternative AI model for retries.
            handle_validation (Literal["raise", "return_value", "return_none"])
                : How to handle validation failures.
            skip_validation (bool): Whether to skip response validation.
            clear_messages (bool): Whether to clear previous messages.
            invoke_action (bool): Whether to invoke actions from the response.
            **kwargs: Additional keyword arguments for the chat process.

        Returns:
            str | dict | BaseModel: The response from the chat interaction.
                The type depends on the request_model and request_fields
                parameters.

        Raises:
            ValueError: If validation fails and handle_validation is
                set to "raise".

        Note:
            - This method adds the instruction and response to the
                branch's messages.
            - If tools are provided, they are registered with the tool manager.
            - Action requests in the response can be automatically invoked if
            invoke_action is True.
        """
        if clear_messages:
            self.clear_messages()
        progress = progress or self.progress

        tool_schemas = None
        if tools:
            tools = tools if isinstance(tools, list) else [tools]
            for i in tools:
                if (
                    isinstance(i, Tool | Callable)
                    and i not in self.tool_manager
                ):
                    self.tool_manager.register_tools(i)

            tool_schemas = self.tool_manager.get_tool_schema(tools)

        response, ins, res = await _chat(
            branch=self,
            instruction=instruction,
            guidance=guidance,
            context=context,
            sender=sender,
            recipient=recipient,
            request_model=request_model,
            request_fields=request_fields,
            imodel=imodel or self.imodel,
            messages=[self.messages[i] for i in progress],
            tool_schemas=tool_schemas,
            images=images,
            image_detail=image_detail,
            invoke_action=invoke_action,
            **kwargs,
        )

        if num_parse_retries > 10:
            logging.warning(
                f"Are you sure you want to retry {num_parse_retries} times"
                "? lowering retry attempts to 10. Suggestion is under 3"
            )
            num_parse_retries = 10

        if request_fields and not isinstance(response, dict):
            while num_parse_retries > 0 and not isinstance(response, dict):
                response, ins, res = await _chat(
                    branch=self,
                    instruction=instruction,
                    guidance=guidance,
                    context=context,
                    sender=sender,
                    recipient=recipient,
                    request_model=request_model,
                    request_fields=request_fields,
                    imodel=retry_imodel or imodel or self.imodel,
                    messages=[self.messages[i] for i in progress],
                    tool_schemas=tool_schemas,
                    images=images,
                    image_detail=image_detail,
                    invoke_action=invoke_action,
                    **kwargs,
                )
                num_parse_retries -= 1
        elif request_model and not isinstance(response, BaseModel):
            while num_parse_retries > 0 and not isinstance(
                response, BaseModel
            ):
                response, ins, res = await _chat(
                    branch=self,
                    instruction=instruction,
                    guidance=guidance,
                    context=context,
                    sender=sender,
                    recipient=recipient,
                    request_model=request_model,
                    request_fields=request_fields,
                    imodel=retry_imodel or imodel or self.imodel,
                    messages=[self.messages[i] for i in progress],
                    tool_schemas=tool_schemas,
                    images=images,
                    image_detail=image_detail,
                    **kwargs,
                )
                num_parse_retries -= 1
        if not skip_validation:
            if request_fields and not isinstance(response, dict):
                logging.warning(
                    "Operative model validation failed. iModel "
                    f"response not parsed into operative model: {response}"
                )
                if handle_validation == "raise":
                    raise ValueError(
                        "Operative model validation failed. iModel "
                        f"response not parsed into operative model: {response}"
                    )
                if handle_validation == "return_none":
                    return None
                if handle_validation == "return_value":
                    self.add_message(instruction=ins)
                    self.add_message(assistant_response=res)
                    return response
            elif request_model and not isinstance(response, BaseModel):
                logging.warning(
                    "Operative model validation failed. iModel response"
                    f" not parsed into operative model: {response}"
                )
                if handle_validation == "raise":
                    raise ValueError(
                        "Operative model validation failed. iModel response"
                        f" not parsed into operative model: {response}"
                    )
                if handle_validation == "return_none":
                    return None
                if handle_validation == "return_value":
                    self.add_message(instruction=ins)
                    self.add_message(assistant_response=res)
                    return response

        self.add_message(instruction=ins)
        self.add_message(assistant_response=res)

        action_request_models = create_action_request_model(response)
        if action_request_models:
            if invoke_action:
                try:
                    action_responses = await alcall(
                        action_request_models,
                        self.invoke_action,
                        suppress_errors=True,
                    )
                except Exception as e:
                    logging.error(f"Failed to invoke action: {e}")
                    action_responses = []

                if action_responses:
                    for i in action_responses:
                        i = to_dict(i)
                        if i.get("output", None):
                            act_req = ActionRequest(
                                function=i["function"],
                                arguments=i["arguments"],
                                sender=self,
                                recipient=self.tool_manager.registry[
                                    i["function"]
                                ].ln_id,
                            )
                            act_res = ActionResponse(
                                action_request=act_req,
                                sender=self.tool_manager.registry[
                                    i["function"]
                                ].ln_id,
                                func_output=i["output"],
                            )

                            self.add_message(
                                action_request=act_req,
                                sender=act_req.sender,
                                recipient=act_req.recipient,
                            )

                            self.add_message(
                                action_request=act_req,
                                action_response=act_res,
                                sender=act_res.sender,
                            )
            else:
                for i in action_request_models:
                    i = to_dict(i)
                    act_req = ActionRequest(
                        function=i["function"],
                        arguments=i["arguments"],
                        sender=self,
                    )
                    self.add_message(
                        action_request=act_req,
                        sender=act_req.sender,
                        recipient=None,
                    )
        return response

    async def _operate(
        self,
        instruction=None,
        guidance=None,
        context=None,
        sender=None,
        recipient=None,
        operative_model: type[BaseModel] = None,
        progress=None,
        imodel: iModel = None,
        reason: bool = True,
        actions: bool = True,
        tool_schemas=None,
        images: list = None,
        image_detail: Literal["low", "high", "auto"] = None,
        handle_unmatched: Literal[
            "ignore", "raise", "remove", "fill", "force"
        ] = "force",
        num_parse_retries: int = 0,
        retry_imodel: iModel = None,
        **kwargs,
    ) -> BaseModel | str | dict:
        request_model: type[BaseModel] = StepModel.as_request_model(
            reason=reason, actions=actions, operative_model=operative_model
        )

        ins = None
        if isinstance(instruction, Instruction):
            ins = instruction
            ins.update_request_model(request_model)
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

        messages = [self.messages[i] for i in (progress or self.progress)]
        messages.append(ins)
        kwargs["messages"] = [m.chat_msg for m in messages]

        imodel = imodel or self.imodel
        api_request = imodel.parse_to_data_model(**kwargs)
        api_response = await imodel.invoke(**api_request)
        res = AssistantResponse(
            assistant_response=api_response,
            sender=self,
            recipient=self.user,
        )
        self.add_message(instruction=ins)
        self.add_message(assistant_response=res)

        step_request_model = None
        dict_ = {}

        def _validate_pydantic(_s):
            d_ = validate_mapping(
                res.response,
                request_model.model_fields,
                handle_unmatched=handle_unmatched,
                fuzzy_match=True,
            )
            step_request_model = request_model.model_validate(d_)
            return d_, step_request_model

        try:
            dict_, step_request_model = _validate_pydantic(res.response)

        except Exception:

            while num_parse_retries > 0 and step_request_model is None:
                retry_imodel = retry_imodel or imodel
                content = RETRY_PROMPT.format(
                    response=res.response,
                    request_model=break_down_pydantic_annotation(
                        request_model
                    ),
                )
                msg = {"role": "user", "content": content}
                kwargs2 = copy(kwargs)
                kwargs2["messages"] = [msg]
                api_request = imodel.parse_to_data_model(**kwargs2)
                api_response = await imodel.invoke(**api_request)
                res = AssistantResponse(
                    assistant_response=api_response,
                    sender=self,
                    recipient=self.user,
                )
                try:
                    dict_, step_request_model = _validate_pydantic(
                        res.response
                    )
                    self.add_message(assistant_response=res)
                    break

                except Exception:
                    if num_parse_retries == 1:
                        try:
                            dict_ = validate_mapping(
                                res.response,
                                request_model.model_fields,
                                handle_unmatched=handle_unmatched,
                                fuzzy_match=True,
                            )
                            break
                        except Exception:
                            dict_ = res.response
                            logging.error(
                                f"Failed to parse response: {res.response}. "
                                "max retries reached, returning raw response"
                            )
                            break

                    logging.error(
                        f"Failed to parse response: {res.response}. "
                        f"Retrying with {retry_imodel.model} ..."
                    )
                    step_request_model = None
                    num_parse_retries -= 1

        return step_request_model if step_request_model else dict_

    def to_df(self) -> pd.DataFrame:
        dicts_ = []
        for i in self.messages:
            dict_: dict = i.to_dict()
            for k in list(dict_.keys()):
                if k not in MESSAGE_FIELDS:
                    dict_.pop(k)
            datetime_ = datetime.fromtimestamp(i.timestamp)
            dict_["timestamp"] = datetime_.isoformat(timespec="auto")
            dict_["role"] = i.role.value

            dicts_.append(dict_)
        return pd.DataFrame(dicts_, columns=MESSAGE_FIELDS)


__all__ = ["Branch"]
# File: lion_core/session/branch.py
