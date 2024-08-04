from lion_core.abc import MutableRecord
from lion_core.generic.component import Component


class Form(Component, MutableRecord):

    template_name: str = "default_form"


__all__ = ["Form"]
