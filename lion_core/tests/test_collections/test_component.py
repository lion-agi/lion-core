import unittest
from datetime import datetime
import json
import pandas as pd
from pydantic import BaseModel, Field

from lion_core.generic.component import Component
from lion_core.abc import LionValueError, LionTypeError
from lion_core.libs import SysUtil

class TestComponent(unittest.TestCase):

    def setUp(self):
        """Set up a basic Component instance for testing."""
        self.component = Component(content="test content")

    def test_initialization(self):
        """Test basic initialization and attributes."""
        self.assertIsInstance(self.component.ln_id, str)
        self.assertIsInstance(self.component.timestamp, float)
        self.assertIsInstance(self.component.metadata, dict)
        self.assertEqual(self.component.content, "test content")
        self.assertIsInstance(self.component.extra_fields, dict)

    def test_all_fields(self):
        """Test the all_fields method."""
        all_fields = self.component.all_fields()
        self.assertIn("ln_id", all_fields)
        self.assertIn("timestamp", all_fields)
        self.assertIn("content", all_fields)

    def test_from_obj(self):
        """Test the from_obj class method."""
        obj = {"content": "new content", "extra_data": "extra"}
        new_component = Component.from_obj(obj, "dict")
        self.assertEqual(new_component.content, "new content")
        self.assertEqual(new_component.metadata["extra_data"], "extra")

    def test_from_dict(self):
        """Test the from_dict class method."""
        dict_data = {"content": "dict content", "ln_id": "test_id"}
        new_component = Component.from_dict(dict_data)
        self.assertEqual(new_component.content, "dict content")
        self.assertEqual(new_component.ln_id, "test_id")

    def test_to_dict(self):
        """Test the to_dict method."""
        self.component.extra_fields["extra_key"] = Field(default="extra_value")
        dict_data = self.component.to_dict()
        self.assertEqual(dict_data["content"], "test content")
        self.assertEqual(dict_data["extra_key"], "extra_value")
        self.assertEqual(dict_data["lion_class"], "Component")

    def test_add_field(self):
        """Test adding a new field."""
        self.component.add_field("new_field", Field(default="new_value"))
        self.assertIn("new_field", self.component.extra_fields)
        self.assertEqual(getattr(self.component, "new_field"), "new_value")

    def test_update_field(self):
        """Test updating an existing field."""
        self.component.add_field("update_field", Field(default="old_value"))
        self.component.update_field("update_field", Field(default="new_value"))
        self.assertEqual(getattr(self.component, "update_field"), "new_value")

    def test_metadata_operations(self):
        """Test metadata operations."""
        self.component._meta_set(["test_key"], "test_value")
        self.assertEqual(self.component._meta_get(["test_key"]), "test_value")
        self.component._meta_pop(["test_key"])
        self.assertNotIn("test_key", self.component.metadata)

    def test_str_repr(self):
        """Test string and representation methods."""
        str_output = str(self.component)
        repr_output = repr(self.component)
        self.assertIn("Component", str_output)
        self.assertIn("Component", repr_output)
        self.assertIn("test content", str_output)
        self.assertIn("test content", repr_output)

    def test_invalid_metadata_assignment(self):
        """Test invalid direct assignment to metadata."""
        with self.assertRaises(AttributeError):
            self.component.metadata = {}

    def test_subclass_registration(self):
        """Test subclass registration."""
        class TestSubclass(Component):
            pass
        self.assertIn("TestSubclass", Component._INIT_CLASS)

    def test_converter_registry(self):
        """Test converter registry functionality."""
        class DummyConverter:
            @staticmethod
            def convert_from(obj, key):
                return {"content": str(obj)}
            
            @staticmethod
            def convert_to(obj, key):
                return obj.content

        ConverterRegistry = type("ConverterRegistry", (), {
            "convert_from": DummyConverter.convert_from,
            "convert_to": DummyConverter.convert_to
        })

        obj = 12345
        new_component = Component.from_obj(obj, "int")
        self.assertEqual(new_component.content, "12345")

        converted_obj = new_component.to_obj(ConverterRegistry, "str")
        self.assertEqual(converted_obj, "12345")

    def test_validation_error(self):
        """Test validation error handling."""
        with self.assertRaises(ValueError):
            Component.from_dict({"ln_id": 12345})  # Invalid ln_id type

if __name__ == "__main__":
    unittest.main()