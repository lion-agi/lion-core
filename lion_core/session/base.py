from typing import Type
from pydantic import Field, model_validator, PrivateAttr

from lion_core.sys_utils import SysUtil
from lion_core.abc import AbstractSpace
from lion_core.communication.system import System
from lion_core.generic.node import Node
from lion_core.generic.pile import Pile
from lion_core.imodel.imodel import iModel
from lion_core.session.msg_handlers import validate_system


class BaseSession(Node, AbstractSpace):

    system: System | None = Field(None)
    user: str | None = Field(None)
    imodel: iModel | None = Field(None)
    name: str | None = Field(None)
    pile_type: Type[Pile] = PrivateAttr(Pile)

    @model_validator(mode="before")
    def validate_system(cls, data: dict):
        system = data.pop("system", None)
        sender = data.pop("system_sender", None)
        system_datetime = data.pop("system_datetime", None)

        system = validate_system(
            system=system,
            sender=sender,
            system_datetime=system_datetime,
        )
        data["system"] = system
        return data

    @model_validator(mode="after")
    def check_system_recipient(self):
        if not SysUtil.is_id(self.system.recipient):
            self.system.recipient = self.ln_id
        return self


# File: lion_core/session/base.py
