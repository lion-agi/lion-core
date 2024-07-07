# lion_core/abc/tao.py

"""
LionAGI: Abstract Space Classes

This module defines abstract classes representing fundamental concepts in space
theory for the LionAGI project. The class hierarchy is inspired by Taoist
philosophy, following the principle of '道生一，一生二，二生三，三生万物' (Dao
generates One, One generates Two, Two generates Three, Three generates myriad
things).
"""

from abc import ABC, abstractmethod
from functools import partial
from lion_core.settings import lion_category


tao_category = partial(
    lion_category,
    abstraction_level="abstract",
    functionality="base",
    domain_specificity="core",
    visibility_scope="internal",
    optimization_level="unoptimized",
    testing_category="not_tested",
    documentation_status="undocumented",
    version_control="experimental",
    filepaths=["lion_core", "abc", "tao.py"],
    author="ocean",
    created_at="2024-07-01",
)


@tao_category(core_concept="tao")
class Tao(ABC):
    """道 (Dao): The fundamental principle underlying existence and
    non-existence."""


# 一 (One)
@tao_category(core_concept="space", parent_class=["Tao"])
class AbstractSpace(Tao):
    """A Borel Space, the existence of a set and a σ-field."""


# 二 (Two)
@tao_category(core_concept="observation", parent_class=["Tao"])
class AbstractObservation(Tao):
    """Represents a static snapshot state of a space or an outcome."""


@tao_category(core_concept="observer", parent_class=["Tao"])
class AbstractObserver(Tao):
    """An entity capable of observing a space."""


# 三 (Three)
@tao_category(core_concept="element", parent_class=["Tao"])
class AbstractElement(Tao):
    """A distinct entity within a space."""

    @abstractmethod
    def to_dict(self, *args, **kwargs): ...


@tao_category(core_concept="characteristic", parent_class=["Tao"])
class AbstractCharacteristic(Tao):
    """A property of an element."""


@tao_category(core_concept="event", parent_class=["Tao"])
class AbstractEvent(Tao):
    """Represents a change in a space."""
