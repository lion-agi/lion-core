from pydantic import Field
from lion_core.abc import AbstractSpace
from lion_core.communication import System
from lion_core.graph.node import Node
from lion_core.imodel.imodel import iModel


class BaseSession(Node, AbstractSpace):

    system: System | None = Field(None, description="The system message node.")
    user: str | None = Field(None, description="The user name or id of this space")
    imodel: iModel | None = Field(None)
