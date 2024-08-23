from lion_core.converter import ConverterRegistry, DictConverter, JsonConverter


class ComponentConverterRegistry(ConverterRegistry):
    pass


ComponentConverterRegistry.register("dict", DictConverter())
ComponentConverterRegistry.register("json", JsonConverter())

__all__ = ["ComponentConverterRegistry", "DictConverter", "JsonConverter"]
