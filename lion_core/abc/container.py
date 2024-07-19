from .concept import AbstractSpace, AbstractElement


class Container(AbstractSpace, AbstractElement):
    """
    Abstract representation of a container or storage space.

    This class defines the concept of a container that can hold items.
    Subclasses should implement the __contains__ method to define
    membership criteria for the container.
    """

    def __contains__(self, item) -> bool:
        """
        Check if an item is in the container.

        Args:
            item: The item to check.

        Returns:
            bool: True if the item is in the container, False otherwise.
        """
        raise NotImplementedError


class Ordering(Container): ...

    # subclass must have order attribute 

class Collective(Container): ...


class Structure(Container): ...
