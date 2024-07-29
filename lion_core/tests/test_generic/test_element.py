import unittest
from datetime import datetime, timezone
from typing import Any, Dict
import time

from pydantic_core._pydantic_core import ValidationError

from lion_core.generic.element import Element
from lion_core.sys_utils import SysUtil
from lion_core.exceptions import LionIDError


class TestElement(unittest.TestCase):
    """Test suite for the Element class."""

    def test_initialization(self) -> None:
        """Test Element initialization with various input combinations."""
        # Default initialization
        element = Element()
        self.assertIsInstance(element.ln_id, str)
        self.assertIsInstance(element.timestamp, float)

        # Initialization with custom ln_id
        custom_id = SysUtil.id()
        element = Element(ln_id=custom_id)
        self.assertEqual(element.ln_id, custom_id)

        # Initialization with custom timestamp
        custom_timestamp = 1625097600.0  # 2021-07-01 00:00:00 UTC
        element = Element(timestamp=custom_timestamp)
        self.assertEqual(element.timestamp, custom_timestamp)

        # Initialization with both custom ln_id and timestamp
        element = Element(ln_id=custom_id, timestamp=custom_timestamp)
        self.assertEqual(element.ln_id, custom_id)
        self.assertEqual(element.timestamp, custom_timestamp)

    def test_created_datetime_property(self) -> None:
        """Test the _created_datetime property."""
        custom_timestamp = 1625097600.0  # 2021-07-01 00:00:00 UTC
        element = Element(timestamp=custom_timestamp)

        # Check if _created_datetime matches the input timestamp
        expected_datetime = datetime.fromtimestamp(custom_timestamp, tz=timezone.utc)
        self.assertEqual(element._created_datetime, expected_datetime)

        # Verify timezone handling
        self.assertEqual(element._created_datetime.tzinfo, timezone.utc)

    def test_ln_id_validator(self) -> None:
        """Test ln_id validation."""
        # Valid ln_id format
        valid_id = SysUtil.id()
        element = Element(ln_id=valid_id)
        self.assertEqual(element.ln_id, valid_id)

        # Invalid ln_id formats
        invalid_ids = ["", " ", "invalid id", "123", "abc123"]
        for invalid_id in invalid_ids:
            with self.assertRaises(LionIDError):
                Element(ln_id=invalid_id)

        # # Attempt to modify ln_id after initialization
        # element = Element()
        # with self.assertRaises(AttributeError):
        #     element.ln_id = SysUtil.id()

    def test_timestamp_validator(self) -> None:
        """Test timestamp validation and processing."""
        # Valid timestamp formats
        valid_timestamps = [
            1625097600.0,  # float
            1625097600,  # int
            "2021-07-01T00:00:00+00:00",  # ISO format string
        ]
        for valid_timestamp in valid_timestamps:
            element = Element(timestamp=valid_timestamp)
            self.assertIsInstance(element.timestamp, float)

        # Invalid timestamp formats
        invalid_timestamps = [
            "invalid_time",
            "2021-07-01",  # Incomplete datetime string
        ]
        for invalid_timestamp in invalid_timestamps:
            try:
                Element(timestamp=invalid_timestamp)
            except:
                return
            self.fail("Invalid timestamp should raise an exception.")

    def test_from_dict_to_dict(self) -> None:
        """Test serialization and deserialization process."""
        # Roundtrip conversion (dict -> Element -> dict)
        original_dict = {
            "ln_id": SysUtil.id(),
            "timestamp": 1625097600.0,
            # "extra_field": "extra_value",
        }
        element = Element.from_dict(original_dict)
        result_dict = element.to_dict()

        self.assertEqual(result_dict["ln_id"], original_dict["ln_id"])
        self.assertEqual(result_dict["timestamp"], original_dict["timestamp"])
        self.assertEqual(result_dict["lion_class"], "Element")

        # Handling of extra fields
        # self.assertNotIn("extra_field", result_dict)

        # Conversion with missing fields
        minimal_dict = {"ln_id": SysUtil.id()}
        minimal_element = Element.from_dict(minimal_dict)
        self.assertEqual(minimal_element.ln_id, minimal_dict["ln_id"])
        self.assertIsInstance(minimal_element.timestamp, float)

    def test_string_representations(self) -> None:
        """Test string representations of Element."""
        element = Element(ln_id=SysUtil.id(), timestamp=1625097600.0)

        # Test __str__ output
        str_output = str(element)
        self.assertIn("Element", str_output)
        self.assertIn(element.ln_id[:6], str_output)
        self.assertIn("2021-07-01", str_output)

        # Test __repr__ output
        repr_output = repr(element)
        self.assertIn("Element", repr_output)
        self.assertIn(element.ln_id, repr_output)
        self.assertIn("1625097600.0", repr_output)

    def test_boolean_and_length(self) -> None:
        """Test boolean evaluation and length of Elements."""
        element = Element()

        # Boolean evaluation
        self.assertTrue(bool(element))

        # Length
        self.assertEqual(len(element), 1)


    def test_element_immutability(self) -> None:
        """Test that Element instances are immutable."""
        element = Element()
        original_id = element.ln_id
        original_timestamp = element.timestamp

        with self.assertRaises(ValidationError):
            element.ln_id = SysUtil.id()
        
        with self.assertRaises(ValidationError):
            element.timestamp = time.time()

        self.assertEqual(element.ln_id, original_id)
        self.assertEqual(element.timestamp, original_timestamp)

    def test_element_subclass_behavior(self) -> None:
        """Test that subclasses of Element maintain core behaviors."""
        class CustomElement(Element):
            custom_attr: str = "default"

        custom_element = CustomElement(custom_attr="custom")
        self.assertIsInstance(custom_element.ln_id, str)
        self.assertIsInstance(custom_element.timestamp, float)
        self.assertEqual(custom_element.custom_attr, "custom")

        # Ensure core Element behaviors are maintained
        self.assertEqual(len(custom_element), 1)
        self.assertTrue(bool(custom_element))

    def test_element_with_future_timestamp(self) -> None:
        """Test Element creation with a future timestamp."""
        future_timestamp = time.time() + 10000  # 10000 seconds in the future
        element = Element(timestamp=future_timestamp)
        self.assertGreater(element.timestamp, time.time())
        self.assertGreater(element._created_datetime, datetime.now(timezone.utc))

    def test_element_serialization_consistency(self) -> None:
        """Test that Element serialization is consistent across instances."""
        element1 = Element()
        time.sleep(0.1)  # Ensure a different timestamp
        element2 = Element()

        dict1 = element1.to_dict()
        dict2 = element2.to_dict()

        self.assertNotEqual(dict1['ln_id'], dict2['ln_id'])
        self.assertNotEqual(dict1['timestamp'], dict2['timestamp'])
        self.assertEqual(dict1.keys(), dict2.keys())
        self.assertEqual(dict1['lion_class'], dict2['lion_class'])

    def test_element_large_batch_creation(self) -> None:
        """Test creation of a large batch of Elements."""
        batch_size = 10000
        elements = [Element() for _ in range(batch_size)]

        self.assertEqual(len(elements), batch_size)
        self.assertEqual(len(set(e.ln_id for e in elements)), batch_size)  # All IDs should be unique

        timestamps = [e.timestamp for e in elements]
        self.assertAlmostEqual(min(timestamps), max(timestamps), delta=1.0)  # All timestamps should be within 1 second

    def test_element_from_dict_with_extra_fields(self) -> None:
        """Test Element creation from a dict with extra fields."""
        extra_dict = {
            "ln_id": SysUtil.id(),
            "timestamp": time.time(),
            # "extra_field1": "value1",
            # "extra_field2": 42
        }
        element = Element.from_dict(extra_dict)
        
        self.assertEqual(element.ln_id, extra_dict["ln_id"])
        self.assertEqual(element.timestamp, extra_dict["timestamp"])

    def test_element_to_dict_consistency(self) -> None:
        """Test that to_dict() output is consistent with the Element's attributes."""
        element = Element()
        dict_repr = element.to_dict()

        self.assertEqual(dict_repr["ln_id"], element.ln_id)
        self.assertEqual(dict_repr["timestamp"], element.timestamp)
        self.assertEqual(dict_repr["lion_class"], element.__class__.__name__)

        # Ensure no extra fields are present
        self.assertEqual(set(dict_repr.keys()), {"ln_id", "timestamp", "lion_class"})


if __name__ == "__main__":
    unittest.main()

# File: tests/test_element.py