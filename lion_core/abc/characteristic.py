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

from lion_core.abc.concept import Tao


class Characteristic(Tao):
    """
    Base class for Lion framework characteristics. Represents fundamental
    properties of Nodes, inspired by property dualism. Forms building blocks
    for modeling complex systems and emergent behaviors.
    """

    pass


class Observable(Characteristic):
    """
    Defines observable entities in quantum-inspired computation and
    cognitive modeling. Rooted in quantum measurement theory, represents
    elements perceivable by AbstractObserver.
    """

    # must have ln_id
    pass


class Temporal(Characteristic):
    """
    Represents time-evolving properties or behaviors. Inspired by
    dynamical systems theory, essential for modeling time-dependent
    processes and state changes in complex systems.
    """

    # must have timestamp
    pass


class Quantum(Characteristic):
    """
    Embodies quantum concepts like superposition and entanglement.
    Enables modeling of non-classical behaviors in cognitive and
    computational processes, key to quantum-inspired approaches.
    """

    pass


class Probabilistic(Characteristic):
    """
    Represents entities with inherent uncertainty. Grounded in
    probability theory and stochastic processes, crucial for modeling
    decision-making and multi-outcome systems.
    """

    pass


class Stochastic(Probabilistic, Temporal):
    """
    Combines probabilistic and time-dependent aspects. Integrates
    stochastic processes and time series analysis for modeling systems
    with evolving randomness, like financial markets or biological processes.
    """

    pass


class Relational(Observable):
    """
    Represents inherently connected or related entities. Fundamental
    for modeling networked systems, social interactions, and complex
    relationships across various domains.
    """

    pass


class Traversal(Observable):
    """
    Represents traversable or explorable entities. Inspired by graph
    theory and network science, essential for modeling paths, connections,
    and information flow in complex networked systems.
    """

    pass


# File: lion_core/abc/characteristic.py
