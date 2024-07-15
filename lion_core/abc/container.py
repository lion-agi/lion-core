from .concept import AbstractSpace


class Container(AbstractSpace):
    """
    Abstract representation of a container or storage space.

    This class defines the concept of a container that can hold items.
    Subclasses should implement the __contains__ method to define
    membership criteria for the container.
    """

    def __contains__(self, item: T) -> bool:
        """
        Check if an item is in the container.

        Args:
            item: The item to check.

        Returns:
            bool: True if the item is in the container, False otherwise.
        """
        raise NotImplementedError


class Ordering(Container): ...


class Collective(Container): ...
