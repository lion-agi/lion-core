# lion_core/abc/tao.py

"""
LionAGI: Abstract Space Classes

This module defines abstract classes representing fundamental concepts in space
theory for the LionAGI project. The class hierarchy is inspired by Taoist
philosophy, following the principle of '道生一，一生二，二生三，三生万物' (Dao
generates One, One generates Two, Two generates Three, Three generates myriad
things).
"""

from abc import ABC


class Tao(ABC):
    """道 (Dao): The fundamental principle underlying existence and
    non-existence."""


# 一 (One)
class AbstractSpace(Tao):
    """A Borel Space, the existence of a set and a σ-field."""


# 二 (Two)
class AbstractObservation(Tao):
    """Represents a static snapshot state of a space or an outcome."""


class AbstractObserver(Tao):
    """An entity capable of observing a space."""


# 三 (Three)
class AbstractElement(Tao):
    """A distinct entity within a space."""


class AbstractCharacteristic(Tao):
    """A property of an element."""


class AbstractEvent(Tao):
    """Represents a change in a space."""
