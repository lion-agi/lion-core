from collections.abc import Mapping
from typing import Type
import os
import ast
import datetime
import importlib.util
from hashlib import sha256
import random


def unique_hash(n: int = 32) -> str:
    """unique random hash"""
    current_time = datetime.now().isoformat().encode("utf-8")
    random_bytes = os.urandom(42)
    return sha256(current_time + random_bytes).hexdigest()[:n]


def is_same_dtype(
    input_: list | dict, dtype: Type | None = None, return_dtype: bool = False
) -> bool | tuple[bool, Type]:
    """Check if all elements in input have the same data type."""
    if not input_:
        return True if not return_dtype else (True, None)

    iterable = input_.values() if isinstance(input_, Mapping) else input_
    first_element_type = type(next(iter(iterable), None))

    dtype = dtype or first_element_type
    result = all(isinstance(element, dtype) for element in iterable)
    return (result, dtype) if return_dtype else result


def insert_random_hyphens(
    s: str,
    num_hyphens: int = 1,
    start_index: int | None = None,
    end_index: int | None = None,
) -> str:
    """Insert random hyphens into a string."""
    if len(s) < 2:
        return s

    prefix = s[:start_index] if start_index else ""
    postfix = s[end_index:] if end_index else ""
    modifiable_part = s[start_index:end_index] if start_index else s

    positions = random.sample(range(len(modifiable_part)), num_hyphens)
    positions.sort()

    for pos in reversed(positions):
        modifiable_part = modifiable_part[:pos] + "-" + modifiable_part[pos:]

    return prefix + modifiable_part + postfix


def get_file_classes(file_path):
    with open(file_path, "r") as file:
        file_content = file.read()

    tree = ast.parse(file_content)

    class_file_dict = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_file_dict[node.name] = file_path

    return class_file_dict


def get_class_file_registry(folder_path, pattern_list):
    class_file_registry = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                if any(pattern in root for pattern in pattern_list):
                    class_file_dict = get_file_classes(os.path.join(root, file))
                    class_file_registry.update(class_file_dict)
    return class_file_registry


def get_class_objects(file_path):
    class_objects = {}
    spec = importlib.util.spec_from_file_location("module.name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for class_name in dir(module):
        obj = getattr(module, class_name)
        if isinstance(obj, type):
            class_objects[class_name] = obj

    return class_objects


__all__ = ["unique_hash", "is_same_dtype", "insert_random_hyphens"]
