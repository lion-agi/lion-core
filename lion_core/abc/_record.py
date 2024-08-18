"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from lion_core.abc._concept import AbstractElement
from lion_core.abc._characteristic import Observable, Temporal


class BaseRecord(AbstractElement, Observable, Temporal):
    """
    Base class for records. Combines AbstractElement with Observable and
    Temporal characteristics.
    """


class MutableRecord(BaseRecord):
    """
    Mutable record class. Inherits from BaseRecord and allows
    modifications.
    """


class ImmutableRecord(BaseRecord):
    """
    Immutable record class. Inherits from BaseRecord but prevents
    modifications. Once a field is filled with data, that field
    cannot change value.
    """


__all__ = [
    "BaseRecord",
    "MutableRecord",
    "ImmutableRecord",
]

# File: lion_core/abc/record.py
