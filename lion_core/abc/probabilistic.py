# lion_core/abc/probabilistic.py

"""
LionAGI: Probabilistic Abstractions

This module defines abstract classes representing probabilistic concepts
in the LionAGI framework. These classes extend the AbstractCharacteristic
base class.
"""

from .tao import AbstractCharacteristic
from functools import partial
from lion_core.settings import lion_category

char_category = partial(
    lion_category,
    abstraction_level="abstract",
    functionality="base",
    domain_specificity="core",
    visibility_scope="internal",
    optimization_level="unoptimized",
    testing_category="not_tested",
    documentation_status="undocumented",
    version_control="experimental",
    filepaths=["lion_core", "abc", "probabilistic.py"],
    author="ocean",
    created_at="2024-07-01",
)


@char_category(core_concept="characteristic", parent_class=["AbstractCharacteristic"])
class Probabilistic(AbstractCharacteristic):
    """Entities with probabilistic behavior."""


@char_category(core_concept="characteristic", parent_class=["Probabilistic"])
class Deterministic(Probabilistic):
    """Entities with deterministic behavior (certain outcomes)."""


@char_category(core_concept="characteristic", parent_class=["Probabilistic"])
class Stochastic(Probabilistic):
    """Entities with random, time-evolving behavior."""
