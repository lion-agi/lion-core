from abc import abstractmethod
from .concept import AbstractSpace, AbstractElement
from .characteristic import Traversal


class Container(AbstractSpace, AbstractElement):
    """
    Abstract representation of a container or storage space.

    This class defines the concept of a container that can hold items.
    Subclasses should implement the __contains__ method to define
    membership criteria for the container.
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


# subclass must have order attribute
class Ordering(Container): ...


class Collective(Container):

    @abstractmethod
    def items(self):
        """
        Get the items in the collective.

        Returns:
            Iterable: The items in the collective.
        """


class Structure(Container, Traversal): ...
