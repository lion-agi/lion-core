"""EdgeCondition module for the Lion framework.

This module defines the EdgeCondition class, which represents a condition
associated with an edge in the Lion framework. It combines AbstractCondition
with Pydantic's BaseModel for robust data validation.

Classes:
    EdgeCondition: Represents a condition associated with an edge.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Path: lion_core/abc/edge_condition.py
