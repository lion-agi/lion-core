from typing import Type
from lion_core.abc import BaseProcessor
from lion_core.generic.form import Form
from lion_core.unit.unit_form import UnitForm


class UnitProcessor(BaseProcessor):
    """Unit processor class."""

    default_form: Type[Form] = UnitForm


__all__ = ["UnitProcessor"]
