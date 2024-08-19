from lion_core.abc import BaseiModel
from lion_core.generic.element import Element


class iModel(Element, BaseiModel):
    async def update_config(self, *args, **kwargs):
        raise NotImplementedError

    async def update_status(self, *args, **kwargs):
        raise NotImplementedError

    async def chat(self, messages, **kwargs):
        raise NotImplementedError

    async def structure(self, *args, **kwargs):
        """raise error, or return structured output"""
        raise NotImplementedError


__all__ = ["iModel"]
