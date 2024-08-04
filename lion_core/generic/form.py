from functools import singledispatchmethod
from collections import deque

from typing import Any, deque

from lion_core.abc import BaseRecord, MutableRecord
from lion_core.generic.component import Component


class Form(Component, MutableRecord):

    template_name: str = "default_form"

    @singledispatchmethod
    def _get_field_annotation(self, field: Any) -> dict[str, Any]:
        return {}

    # use list comprehension
    @_get_field_annotation.register(str)
    def _(self, field: str) -> dict[str, Any]:
        dict_ = {field: self.all_fields[field].annotation}
        for k, v in dict_.items():
            if "|" in str(v):
                v = str(v)
                v = v.split("|")
                dict_[k] = [str(i).lower().strip() for i in v]
            else:
                dict_[k] = [v.__name__] if v else None
        return dict_

    @_get_field_annotation.register(deque)
    @_get_field_annotation.register(set)
    @_get_field_annotation.register(list)
    @_get_field_annotation.register(tuple)
    def _(self, field: list | tuple) -> dict[str, Any]:
        dict_ = {}
        for f in field:
            dict_.update(self._get_field_annotation(f))
        return dict_

    ...


__all__ = ["Form"]
