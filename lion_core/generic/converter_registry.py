from __future__ import annotations
from typing import Any
from lion_core.converter import ConverterRegistry
from .element import Element
from lion_core.libs import fuzzy_parse_json, to_str


class DictConverter:

    @staticmethod
    def from_obj(obj: dict[str, Any]) -> dict[str, Any]:
        return obj

    @staticmethod
    def to_obj(self: Element) -> dict[str, Any]:
        return self.serialize()


class JsonConverter:

    @staticmethod
    def from_obj(obj: str) -> dict[str, Any]:
        return fuzzy_parse_json(obj)

    @staticmethod
    def to_obj(self: Element) -> str:
        return to_str(self.serialize())


# Register converters
ConverterRegistry.register("dict", DictConverter(), for_types=dict)
ConverterRegistry.register("json", JsonConverter(), for_types=str)


# File: lion_core/generic/converter_registry.py
