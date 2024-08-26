from lion_core.converter import ConverterRegistry, JsonConverter


class ComponentConverterRegistry(ConverterRegistry):
    pass


ComponentConverterRegistry.register("json", JsonConverter())

__all__ = ["ComponentConverterRegistry"]
