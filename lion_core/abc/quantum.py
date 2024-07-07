# lion_core/abc/quantum.py

"""
LionAGI: Quantum Abstractions

This module defines abstract classes representing quantum concepts
in the LionAGI framework. These classes extend the AbstractCharacteristic
base class.
"""

from .tao import AbstractCharacteristic
from functools import partial
from lion_core.settings import lion_category


quantum_category = partial(
    lion_category,
    abstraction_level="abstract",
    functionality="base",
    domain_specificity="core",
    visibility_scope="internal",
    optimization_level="unoptimized",
    testing_category="not_tested",
    documentation_status="undocumented",
    version_control="experimental",
    author="ocean",
    created_at="2024-07-01",
)


@quantum_category(
    core_concept="characteristic", parent_class=["AbstractCharacteristic"]
)
class Quantum(AbstractCharacteristic):
    """Entities with quantum properties."""


@quantum_category(core_concept="characteristic", parent_class=["Quantum"])
class Superposable(Quantum):
    """Quantum entities that can be in superposition."""


@quantum_category(core_concept="characteristic", parent_class=["Quantum"])
class Entangleable(Quantum):
    """Quantum entities that can be entangled."""
