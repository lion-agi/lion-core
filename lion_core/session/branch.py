import logging
from datetime import datetime
from typing import Any, Literal

import pandas as pd
from lion_service import iModel
from lionabc import Traversal
from lionfuncs import is_same_dtype
from pydantic import BaseModel, Field, model_validator

from lion_core.action import Tool, ToolManager
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
from lion_core.session.base import BaseSession
from lion_core.session.msg_handlers import create_message, validate_message
from lion_core.session.utils import _chat, _operate

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
    """

    messages: Pile = Field(default_factory=Pile)
    tool_manager: ToolManager = Field(default_factory=ToolManager)
    mailbox: Exchange = Field(default_factory=Exchange)
    progress: Progression = Field(default_factory=progression)
    system: System | None = Field(None)
    user: str = "user"
    imodel: iModel | None = Field(None)
    operative_model: type[BaseModel] | None = Field(None)

    # _converter_registry: ClassVar = BranchConverterRegistry

    @model_validator(mode="before")
    def _validate_input(cls, data: dict) -> dict:
        messages = data.pop("messages", None)
        data["messages"] = cls.messages.__class__(
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
            data["tool_manager"].register_tools(data.pop("tools"))
        return cls.validate_system(data)

    @model_validator(mode="after")
    def _check_system(self):
        if self.system not in self.messages:
            self.messages.include(self.system)
            self.progress.insert(0, self.system)
        return self

    def set_system(self, system: System) -> None:
        """
        Set or update the system message for the branch.

        Args:
            system: The new system message.
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
    ) -> bool:
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
        return _msg

    def clear_messages(self) -> None:
        """Clear all messages except the system message."""
        self.messages.clear()
        self.progress.clear()
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
        Send a mail to a recipient.

        Args:
            recipient: The recipient's ID.
            category: The category of the mail.
            package: The content of the mail.
            request_source: The source of the request.
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
            message (bool, optional): Whether to process message mails.
            tool (bool, optional): Whether to process tool mails.
            imodel (bool, optional): Whether to process imodel mails.

        Raises:
            ValueError: If the sender does not exist or the mail category
                is invalid.
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
        """
        Receives mail from all senders.
        """
        for key in list(self.mailbox.pending_ins.keys()):
            self.receive(key)

    @property
    def last_response(self) -> AssistantResponse | None:
        """
        Get the last assistant response.

        Returns:
            AssistantResponse | None: The last assistant response, if any.
        """
        for i in reversed(self.progress):
            if isinstance(self.messages[i], AssistantResponse):
                return self.messages[i]

    @property
    def assistant_responses(self) -> Pile:
        """
        Get all assistant responses as a Pile.

        Returns:
            Pile: A Pile containing all assistant responses.
        """
        return self.messages.__class__(
            [
                self.messages[i]
                for i in self.progress
                if isinstance(self.messages[i], AssistantResponse)
            ]
        )

    def update_last_instruction_meta(self, meta: dict) -> None:
        """
        Update metadata of the last instruction.

        Args:
            meta (dict): Metadata to update.
        """
        for i in reversed(self.progress):
            if isinstance(self.messages[i], Instruction):
                self.messages[i].metadata.update(meta, ["extra"])
                return

    def has_tools(self) -> bool:
        """
        Check if the branch has any registered tools.

        Returns:
            bool: True if tools are registered, False otherwise.
        """
        return self.tool_manager.registry != {}

    def register_tools(self, tools: Any) -> None:
        """
        Register new tools to the tool manager.

        Args:
            tools (Any): Tools to be registered.
        """
        self.tool_manager.register_tools(tools=tools)

    def delete_tools(
        self,
        tools: Any,
        verbose: bool = True,
    ) -> bool:
        """
        Delete specified tools from the tool manager.

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
        Convert messages to a list of chat message dictionaries.

        Returns:
            list[dict[str, Any]]: A list of chat message dictionaries.
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
        **kwargs,
    ):
        self = self or Branch()
        progress = progress or self.progress

        tool_schemas = None
        if tools:
            self.register_tools(tools)
            tool_schemas = self.tool_manager.get_tool_schema(tools)

        responses_model, ins, res = await _operate(
            branch=self,
            instruction=instruction,
            guidance=guidance,
            context=context,
            sender=sender,
            recipient=recipient,
            operative_model=operative_model or self.operative_model,
            imodel=imodel or self.imodel,
            reason=reason,
            actions=actions,
            invoke_action=invoke_action,
            messages=[self.messages[i] for i in progress],
            tool_schemas=tool_schemas,
            handle_unmatched=handle_unmatched,
            **kwargs,
        )
        if num_parse_retries > 10:
            logging.warning(
                f"Are you sure you want to retry {num_parse_retries} "
                "times? lowering retry attempts to 10. Suggestion is under 3"
            )
            num_parse_retries = 10

        if isinstance(responses_model, dict):
            while num_parse_retries > 0 and isinstance(responses_model, dict):
                responses_model, ins, res = await _operate(
                    instruction=instruction,
                    guidance=guidance,
                    context=context,
                    sender=sender,
                    recipient=recipient,
                    operative_model=operative_model or self.operative_model,
                    imodel=retry_imodel or imodel or self.imodel,
                    reason=reason,
                    actions=actions,
                    messages=[self.messages[i] for i in progress],
                    tool_schemas=tool_schemas,
                    handle_unmatched=handle_unmatched,
                    **responses_model,
                )
                num_parse_retries -= 1

        if not skip_validation and isinstance(responses_model, dict):
            logging.warning(
                "iModel response not parsed into operative "
                f"model: {responses_model}"
            )
            if handle_validation == "raise":
                raise ValueError(
                    "Operative model validation failed. iModel response"
                    f" not parsed into operative model: {responses_model}"
                )
            if handle_validation == "return_none":
                return None
            if handle_validation == "return_value":
                self.add_message(instruction=ins)
                self.add_message(assistant_response=res)
                return responses_model

        action_responses = None
        if isinstance(responses_model, dict):
            action_responses = responses_model.get("action_responses", None)
        elif isinstance(responses_model, BaseModel) and hasattr(
            responses_model, "action_responses"
        ):
            action_responses = responses_model.action_responses

        self.add_message(instruction=ins)
        self.add_message(assistant_response=res)

        if action_responses:
            for i in action_responses:
                act_req = ActionRequest(
                    function=i.function,
                    arguments=i.arguments,
                    sender=self,
                    recipient=self.tool_manager.registry[i.function].ln_id,
                )
                act_req = self.add_message(action_request=act_req)
                self.add_message(
                    action_request=act_req,
                    action_response_model=i,
                    sender=self.tool_manager.registry[i.function].ln_id,
                    recipient=self,
                )

        elif isinstance(responses_model, BaseModel) and hasattr(
            responses_model, "action_requests"
        ):
            for i in responses_model.action_requests:
                self.add_message(
                    action_request_model=i,
                    sender=self.ln_id,
                    recipient=self.tool_manager.registry[i.function].ln_id,
                )

        return responses_model

    async def chat(
        self,
        instruction=None,
        guidance=None,
        context=None,
        sender=None,
        recipient=None,
        progress=None,
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
        **kwargs,
    ):
        self = self or Branch()
        progress = progress or self.progress

        tool_schemas = None
        if tools:
            self.register_tools(tools)
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
                    **response,
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
                    **response,
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
        return response

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
