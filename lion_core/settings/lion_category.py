"""
class_category.py

This module provides a comprehensive system for categorizing and analyzing classes
in a software project. It includes decorators for adding metadata to classes,
a registry for tracking categorized classes, and utilities for system-wide analysis.

Usage:
    from class_category import class_category, analyze_system, generate_class_diagram

    @class_category(abstraction_level="abstract", core_concept="structure")
    class MyClass:
        pass

    analyze_system()
    generate_class_diagram()
"""

import inspect
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class AbstractionLevel(str, Enum):
    """Enumeration of possible abstraction levels for a class."""

    ABSTRACT = "abstract"
    CONCRETE = "concrete"
    PROTOCOL = "protocol"
    PYDANTIC_MODEL = "pydantic_model"


class Functionality(str, Enum):
    """Enumeration of functionality types a class can have."""

    BASE = "base"
    UTILITY = "utility"
    EXTENSION = "extension"
    INTERFACE = "interface"


class CoreConcept(str, Enum):
    """Enumeration of core concepts a class can represent."""

    TAO = "tao"
    ELEMENT = "element"
    CHARACTERISTIC = "characteristic"
    OBSERVATION = "observation"
    EVENT = "event"
    SPACE = "space"
    OBSERVER = "observer"


class DomainSpecificity(str, Enum):
    """Enumeration of domain specificity levels for a class."""

    CORE = "core"
    DOMAIN_SPECIFIC = "domain_specific"


class VisibilityScope(str, Enum):
    """Enumeration of visibility scopes for a class."""

    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
    INTERNAL = "internal"


class OptimizationLevel(str, Enum):
    """Enumeration of optimization levels for a class."""

    UNOPTIMIZED = "unoptimized"
    OPTIMIZED = "optimized"
    HIGHLY_OPTIMIZED = "highly_optimized"


class TestingCategory(str, Enum):
    """Enumeration of testing categories for a class."""

    NOT_TESTED = "not_tested"
    UNIT_TESTED = "unit_tested"
    INTEGRATION_TESTED = "integration_tested"
    SYSTEM_TESTED = "system_tested"
    PERFORMANCE_TESTED = "performance_tested"


class DocumentationStatus(str, Enum):
    """Enumeration of documentation statuses for a class."""

    UNDOCUMENTED = "undocumented"
    PARTIALLY_DOCUMENTED = "partially_documented"
    FULLY_DOCUMENTED = "fully_documented"
    VERIFIED_DOCUMENTATION = "verified_documentation"


class VersionControl(str, Enum):
    """Enumeration of version control statuses for a class."""

    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"
    LEGACY = "legacy"


class LionCategory(BaseModel):
    """
    A model representing various categories and attributes of a class.

    This model provides a comprehensive way to describe and categorize
    a class based on its characteristics, lifecycle, functionality, and more.
    """

    abstraction_level: str = Field(...)
    functionality: str = Field(...)
    core_concept: str = Field(...)
    domain_specificity: str = Field(...)
    visibility_scope: str = Field(...)
    optimization_level: str = Field(...)
    testing_category: str = Field(...)
    documentation_status: str = Field(...)
    version_control: str = Field(...)
    author: str = Field(default="ocean")
    filepath: list[str] = Field(default_factory=list)
    parent_class: list[str] = Field(default_factory=list)
    created_at: datetime | str = Field(default_factory=datetime.now)
    last_modified: datetime | str = Field(default_factory=datetime.now)

    @field_validator("*", mode="before")
    def validate_enum_fields(cls, v, field):
        """Validate and convert string inputs to appropriate enum values."""
        if field.name in cls.__annotations__:
            enum_class = globals()[field.name.title().replace("_", "")]
            if isinstance(v, str):
                try:
                    return enum_class[v.upper()].value
                except KeyError:
                    raise ValueError(f"Invalid value for {field.name}: {v}")
            elif isinstance(v, enum_class):
                return v.value
        return v


class ClassCategoryRegistry:
    """A registry to keep track of all categorized classes."""

    _registry: Dict[str, LionCategory] = {}

    @classmethod
    def register(cls, class_name: str, category: LionCategory) -> None:
        """Register a class with its category information."""
        cls._registry[class_name] = category

    @classmethod
    def get(cls, class_name: str) -> Optional[LionCategory]:
        """Retrieve the category information for a given class."""
        return cls._registry.get(class_name)

    @classmethod
    def all(cls) -> Dict[str, LionCategory]:
        """Retrieve all registered classes and their categories."""
        return cls._registry


def lion_category(**kwargs: Any) -> Any:
    """
    A decorator to annotate classes with ClassCategory information.

    Usage:
    @class_category(abstraction_level="abstract", core_concept="structure")
    class MyClass:
        pass

    :param kwargs: Keyword arguments corresponding to ClassCategory fields
    :return: Decorator function
    """

    def decorator(cls: Any) -> Any:
        # Create ClassCategory instance
        category = LionCategory(**kwargs)

        # Add dependency information
        category.dependencies.imports = [
            imp for imp in cls.__module__.__dict__ if not imp.startswith("_")
        ]
        category.dependencies.parent_classes = [
            base.__name__ for base in cls.__bases__ if base != object
        ]

        # Add complexity metric
        category.complexity = len(inspect.getsource(cls).split("\n"))

        # Register the class
        ClassCategoryRegistry.register(cls.__name__, category)

        setattr(cls, "_class_category", category)

        @classmethod
        def get_class_category(cls) -> LionCategory:
            return cls._class_category

        cls.get_class_category = get_class_category
        return cls

    return decorator
