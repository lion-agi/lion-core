# from __future__ import annotations
#
# import json
# from .element import Element
# from lion_core.libs import fuzzy_parse_json
#
#
# class DefaultConverter:
#
#     @property
#     def dict_converter(self):
#         return DictConverter
#
#     @property
#     def str_converter(self):
#         return JsonConverter
#
#
# class DictConverter:
#
#     @staticmethod
#     def from_obj(target_class, obj: dict):
#         try:
#             return target_class(**obj)
#         except:
#             try:
#                 if "from_dict" in target_class.__dict__:
#                     return target_class.from_dict(**obj)
#                 else:
#                     raise ValueError(f"Converter to {target_class} is not supported.")
#             except Exception as e:
#                 raise ValueError(f"Failed to convert from dict. Error: {e}")
#
#     @staticmethod
#     def to_obj(self, **kwargs):
#         try:
#             if isinstance(self, Element):
#                 return self.model_dump(**kwargs)
#             elif "to_dict" in self.__dict__:
#                 return self.to_dict(**kwargs)
#             else:
#                 raise ValueError(f"Converter from {self.__class__.__name__} is not supported.")
#         except Exception as e:
#             raise ValueError(f"Failed to convert to dict. Error: {e}")
#
#
# class JsonConverter:
#
#     @staticmethod
#     def from_obj(target_class, obj: str):
#         obj_dict = fuzzy_parse_json(obj)
#         return DictConverter.from_obj(target_class, obj_dict)
#
#     @staticmethod
#     def to_obj(self, **kwargs) -> str:
#         try:
#             if isinstance(self, Element):
#                 return self.model_dump_json(**kwargs)
#             elif "to_json" in self.__dict__:
#                 return self.to_json(**kwargs)
#             else:
#                 result_dict = DictConverter.to_obj(self, **kwargs)
#                 return json.dumps(result_dict)
#         except Exception as e:
#             raise ValueError(f"Failed to convert to json. Error: {e}")
#
#
# Register converters
# ConverterRegistry.register("dict", DictConverter(), for_types=dict)
# ConverterRegistry.register("json", JsonConverter(), for_types=str)
#
#
# File: lion_core/generic/converter_registry.py
