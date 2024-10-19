from lionabc import AbstractSpace, BaseiModel
from pydantic import model_validator

from lion_core.communication import System
from lion_core.generic.node import Node
from lion_core.session.msg_handlers import create_system
from lion_core.sys_utils import SysUtil


class BaseSession(Node, AbstractSpace):
    system: System | None = None
    user: str = "user"
    imodel: BaseiModel | None = None
    name: str | None = None

    @model_validator(mode="before")
    def validate_system(cls, data: dict):
        system = data.pop("system", None)
        if system is None:
            return data

        sender = data.pop("system_sender", None)
        system_datetime = data.pop("system_datetime", None)

        system = create_system(
            system=system,
            sender=sender,
            system_datetime=system_datetime,
        )
        data["system"] = system
        return data

    @model_validator(mode="after")
    def check_system_recipient(self):
        if self.system is None:
            return self
        if not SysUtil.is_id(self.system.recipient):
            self.system.recipient = self.ln_id
        return self


__all__ = ["BaseSession"]
# File: lion_core/session/base.py
