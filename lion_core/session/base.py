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

from typing import Any
from pydantic import Field
from lion_core.abc import AbstractSpace
from lion_core.communication import System
from lion_core.graph.node import Node
from lion_core.imodel.imodel import iModel


class BaseSession(Node, AbstractSpace):

    system: System | None = Field(None, description="The system message node.")
    user: str | None = Field(None, description="The user name or id of this space")
    imodel: iModel | None = Field(None)

    def __init__(
        self,
        system: Any = None,
    ): ...
