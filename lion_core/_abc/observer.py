"""
Abstract observer classes for the Lion framework.

This module defines observer-based structures that extend the concept of
AbstractObserver, incorporating principles from complex systems theory,
quantum observation, and distributed computing to model entities capable
of monitoring, processing, and acting upon the state of a system within
the LION framework.
"""

from abc import abstractmethod
from lion_core._abc.concept import AbstractObserver


class BaseManager(AbstractObserver):
    """
    Abstract base class for managers in the Lion framework.

    Managers in LION represent high-level observers that coordinate and
    oversee the activities of other observers and system components. They
    embody the concept of emergent control in complex systems, where global
    behaviors arise from local interactions and observations.
    """

    pass


class BaseExecutor(AbstractObserver):
    """
    Abstract base class for executors in the Lion framework.

    Executors in LION represent active observers that can perform tasks
    based on their observations. They draw inspiration from the concept
    of measurement-induced state changes in quantum mechanics, where the
    act of observation can directly influence the system's state.
    """

    @abstractmethod
    async def forward(self, *args, **kwargs):
        """
        Execute the observer's task asynchronously.

        This method represents the primary action of the executor, potentially
        altering the system's state based on observations. The asynchronous
        nature allows for modeling of concurrent operations and parallel
        processing in complex, distributed systems.
        """
        pass


class BaseProcessor(AbstractObserver):
    """
    Abstract base class for processors in the Lion framework.

    Processors in LION represent specialized observers focused on
    information transformation and analysis. They embody the concept of
    information processing in complex systems, drawing parallels to
    quantum information theory and cognitive processing models.
    """

    @abstractmethod
    async def process(self, *args, **kwargs):
        """
        Process information asynchronously based on observations.

        This method encapsulates the core functionality of information
        processing, potentially involving complex transformations,
        filtering, or aggregation of observed data. The asynchronous
        design supports modeling of continuous, real-time processing
        in dynamic systems.
        """
        pass


# File: lion_core/_abc/observer.py
