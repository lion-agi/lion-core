"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
