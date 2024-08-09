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

from abc import abstractmethod
from lion_core.abc._concept import AbstractSpace, AbstractElement
from lion_core.abc._characteristic import Traversal


class Container(AbstractSpace, AbstractElement):
    """
    Abstract container or storage space. Subclasses should implement
    __contains__ to define membership criteria.
    """

    @abstractmethod
    def __contains__(self, item) -> bool:
        """
        Check if an item is in the container.

        Args:
            item: The item to check.

        Returns:
            bool: True if the item is in the container, False otherwise.
        """


class Ordering(Container):
    """Container with a defined order. Subclass must have order attribute."""


class Collective(Container):
    """Container representing a collection of items."""

    @abstractmethod
    def items(self):
        """
        Get the items in the collective.

        Returns:
            Iterable: The items in the collective.
        """


class Structure(Container, Traversal):
    """
    Container with traversable structure, combining Container and Traversal
    characteristics.
    """
