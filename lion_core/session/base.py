from pydantic import Field
from lion_core.abc import AbstractSpace, BaseiModel
from lion_core.generic.component import Component
from lion_core.communication import System


class BaseSession(Component, AbstractSpace):

    system: System | None = Field(None, description="The system message node.")
    imodel: BaseiModel | None = Field(None, description="An intelligent model")
    user: str | None = Field(None, description="The user name or id of this space")
