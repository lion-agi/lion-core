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

from abc import ABC


class Tao(ABC):
    """
    Foundational abstraction embodying interconnectedness and existence.
    Root for all classes, reflecting Taoist unity and Category Theory relations.
    """


class AbstractSpace(Tao):
    """
    Abstract space or context, aligning with Category Theory's categories.
    Defines domain for elements and interactions, supporting system emergence.
    Subclasses implement __contains__ for membership criteria.
    """


class AbstractElement(Tao):
    """
    Observable entity within a space, reflecting Taoist individuality in unity.
    Embodies Category Theory objects and Complex Systems components.
    Capable of emergent behaviors through interactions.
    """

    @classmethod
    def class_name(cls) -> str:
        """Get class name, supporting reflection and metaprogramming."""
        return cls.__name__


class AbstractObserver(Tao):
    """
    Entity capable of observations, inspired by quantum mechanics and cognition.
    Prepresents intentionality and observer effect in complex systems.
    Subclasses implement specific observation mechanisms.
    """


class AbstractObservation(Tao):
    """
    Act of observing, integrating phenomenology and information theory.
    Captures information exchange and meaning construction in complex systems.
    """


# File: lion_core/abc/concept.py
