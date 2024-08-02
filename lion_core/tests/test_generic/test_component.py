import unittest
from datetime import datetime, timezone
from typing import Any, Dict
import time

from pydantic_core._pydantic_core import ValidationError
from lion_core.generic.component import Component
from lion_core.generic.note import Note
from lion_core.generic.component_converter import ComponentConverterRegistry
from lion_core.sys_utils import SysUtil
from lion_core.exceptions import LionIDError, LionValueError, LionTypeError

class TestComponent(unittest.TestCase):
    """Comprehensive test suite for the Component class."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_id = SysUtil.id()
        self.timestamp = datetime.now(timezone.utc).timestamp()

    def test_basic_initialization(self):
        """Test basic initialization of Component."""
        component = Component(ln_id=self.valid_id, timestamp=self.timestamp)
        self.assertEqual(component.ln_id, self.valid_id)
        self.assertEqual(component.timestamp, self.timestamp)
        self.assertIsInstance(component.metadata, Note)
        self.assertIsNone(component.content)
        self.assertEqual(component.embedding, [])
        self.assertEqual(component.extra_fields, {})

    def test_full_initialization(self):
        """Test initialization with all attributes."""
        metadata = Note()
        metadata.update({"key": "value"})
        content = "Test content"
        embedding = [0.1, 0.2, 0.3]
        extra_fields = {"extra_key": "extra_value"}

        component = Component(
            ln_id=self.valid_id,
            timestamp=self.timestamp,
            metadata=metadata,
            content=content,
            embedding=embedding,
            extra_fields=extra_fields
        )

        self.assertEqual(component.metadata.content, {"key": "value"})
        self.assertEqual(component.content, content)
        self.assertEqual(component.embedding, embedding)
        self.assertEqual(component.extra_fields, extra_fields)

    def test_metadata_serialization(self):
        """Test metadata serialization."""
        metadata = Note()
        metadata.update({"key": "value"})
        component = Component(metadata=metadata)
        serialized = component.model_dump()
        self.assertEqual(serialized["metadata"], {"key": "value"})

    def test_add_field(self):
        """Test adding a new field to the component."""
        component = Component()
        component.add_field("new_field", "new_value")
        self.assertEqual(component.new_field, "new_value")
        self.assertIn("new_field", component.extra_fields)

        # Test adding a field that already exists
        with self.assertRaises(LionValueError):
            component.add_field("new_field", "another_value")

    def test_update_field(self):
        """Test updating an existing field."""
        component = Component()
        component.add_field("test_field", "initial_value")
        component.update_field("test_field", "updated_value")
        self.assertEqual(component.test_field, "updated_value")

        # Test updating a non-existent field (should create it)
        component.update_field("new_field", "new_value")
        self.assertEqual(component.new_field, "new_value")

    def test_to_dict_consistency(self):
        """Test that to_dict() output is consistent with the Component's attributes."""
        component = Component(
            ln_id=self.valid_id,
            timestamp=self.timestamp,
            content="Test content",
            embedding=[0.1, 0.2, 0.3]
        )
        component.add_field("extra_field", "extra_value")

        dict_repr = component.to_dict()

        self.assertEqual(dict_repr["ln_id"], self.valid_id)
        self.assertEqual(dict_repr["timestamp"], self.timestamp)
        self.assertEqual(dict_repr["content"], "Test content")
        self.assertEqual(dict_repr["embedding"], [0.1, 0.2, 0.3])
        self.assertEqual(dict_repr["extra_field"], "extra_value")
        self.assertEqual(dict_repr["lion_class"], "Component")

    def test_from_dict(self):
        """Test creating a Component from a dictionary."""
        input_dict = {
            "ln_id": self.valid_id,
            "timestamp": self.timestamp,
            "content": "Test content",
            "embedding": [0.1, 0.2, 0.3],
            "extra_field": "extra_value",
            "lion_class": "Component"
        }

        component = Component.from_dict(input_dict)

        self.assertEqual(component.ln_id, self.valid_id)
        self.assertEqual(component.timestamp, self.timestamp)
        self.assertEqual(component.content, "Test content")
        self.assertEqual(component.embedding, [0.1, 0.2, 0.3])
        self.assertEqual(component.extra_field, "extra_value")

    def test_nested_structures(self):
        """Test handling of nested structures in content and metadata."""
        nested_content = {
            "level1": {
                "level2": [1, 2, {"level3": "deep"}]
            }
        }
        nested_metadata = Note()
        nested_metadata.update({"meta_level1": {"meta_level2": ["a", "b", "c"]}})

        component = Component(content=nested_content, metadata=nested_metadata)
        serialized = component.to_dict()

        self.assertEqual(serialized["content"], nested_content)
        self.assertEqual(serialized["metadata"], nested_metadata.content)

        deserialized = Component.from_dict(serialized)
        self.assertEqual(deserialized.content, nested_content)
        self.assertEqual(deserialized.metadata.content, nested_metadata.content)

    def test_large_component(self):
        """Test handling of a component with large amount of data."""
        large_content = "x" * 1000000  # 1MB of data
        large_embedding = [0.1] * 10000  # 10,000 float embeddings

        component = Component(content=large_content, embedding=large_embedding)
        serialized = component.to_dict()
        deserialized = Component.from_dict(serialized)

        self.assertEqual(len(deserialized.content), 1000000)
        self.assertEqual(len(deserialized.embedding), 10000)

    def test_component_equality(self):
        """Test equality comparison of Components."""
        comp1 = Component(ln_id=self.valid_id, content="Same content")
        time.sleep(0.01)  # Ensure different timestamps
        comp2 = Component(ln_id=self.valid_id, content="Same content")
        comp3 = Component(ln_id=SysUtil.id(), content="Different content")

        self.assertNotEqual(comp1, comp2)  # Different timestamps
        self.assertNotEqual(comp1, comp3)  # Different ln_id and content

    def test_component_immutability(self):
        """Test that core attributes of Component are immutable."""
        component = Component(ln_id=self.valid_id, timestamp=self.timestamp)

        with self.assertRaises(ValidationError):
            component.ln_id = SysUtil.id()

        with self.assertRaises(ValidationError):
            component.timestamp = datetime.now().timestamp()


    def test_component_with_note_content(self):
        """Test Component with Note as content."""
        note_content = Note()
        note_content.update({"key": "value"})
        component = Component(content=note_content)
        serialized = component.to_dict()

        self.assertEqual(serialized["content"], {"key": "value"})

        deserialized = Component.from_dict(serialized)
        self.assertIsInstance(deserialized.content, dict)
        self.assertEqual(deserialized.content, {"key": "value"})

    def test_component_string_representations(self):
        """Test string representations of Component."""
        component = Component(ln_id=self.valid_id, content="Test content")
        str_repr = str(component)
        repr_repr = repr(component)

        self.assertIn(self.valid_id[:8], str_repr)
        self.assertIn("Test content", str_repr)
        self.assertIn(self.valid_id, repr_repr)
        self.assertIn("Test content", repr_repr)
        
if __name__ == '__main__':
    unittest.main()

# File: tests/test_component.py