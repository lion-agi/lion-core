from lion_core.converter import ConverterRegistry, DictConverter, JsonConverter


class ComponentConverterRegistry(ConverterRegistry): ...


ComponentConverterRegistry.register("dict", DictConverter())
ComponentConverterRegistry.register("json", JsonConverter())
