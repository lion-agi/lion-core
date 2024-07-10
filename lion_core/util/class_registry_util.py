"""
Utility module for class registration and retrieval in the Lion framework.

This module provides a global class registry and utility functions for
managing and retrieving classes dynamically. It's designed to support
the extensible nature of the Lion framework by allowing runtime class
lookups and registrations.

The main components are:
- LION_CLASS_REGISTRY: A global dictionary storing class references.
- get_class: A function to retrieve classes by name, using the registry
             or dynamic import mechanisms.

Usage:
    from lion_core.util.class_registry_util import get_class, LION_CLASS_REGISTRY

    # Retrieve a class
    MyClass = get_class("MyClassName", BaseClass)

    # Register a class manually (if needed)
    LION_CLASS_REGISTRY["MyClassName"] = MyClass
"""

from typing import Dict, Type, TypeVar
from lion_core.util.sys_util import SysUtil

T = TypeVar("T")
LION_CLASS_REGISTRY: Dict[str, Type[T]] = {}


def get_class(class_name: str, base_class: type[T]) -> type[T]:
    """
    Retrieve a class by name from the registry or dynamically import it.

    This function first checks the LION_CLASS_REGISTRY for the requested class.
    If not found, it uses SysUtil.mor to dynamically import the class. The
    function ensures that the retrieved class is a subclass of the specified
    base_class.

    Args:
        class_name: The name of the class to retrieve.
        base_class: The expected base class of the retrieved class.

    Returns:
        The requested class, which is a subclass of base_class.

    Raises:
        ValueError: If the class is not found or not a subclass of base_class.

    Usage:
        MyClass = get_class("MyClassName", BaseClass)
        instance = MyClass()

    Note:
        This function automatically registers newly found classes in the
        LION_CLASS_REGISTRY for future quick access.
    """
    if class_name in LION_CLASS_REGISTRY:
        return LION_CLASS_REGISTRY[class_name]

    try:
        found_class = SysUtil.mor(class_name)
        if issubclass(found_class, base_class):
            LION_CLASS_REGISTRY[class_name] = found_class
            return found_class
        else:
            raise ValueError(f"{class_name} is not a subclass of {base_class.__name__}")
    except ValueError as e:
        raise ValueError(f"Unable to find class {class_name}: {e}")


# File: lion_core/util/class_registry_util.py
