import unittest
# import pandas as pd
from lion_core.libs.data_handlers._to_dict import to_dict


class TestToDictFunction(unittest.TestCase):

    def test_to_dict_with_dict(self):
        input_data = {"a": 1, "b": 2}
        result = to_dict(input_data)
        self.assertEqual(result, input_data)

    def test_to_dict_with_list_of_dicts(self):
        input_data = [{"a": 1}, {"b": 2}]
        result = to_dict(input_data)
        self.assertEqual(result, input_data)

    # def test_to_dict_with_dataframe(self):
    #     input_data = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    #     result = to_dict(input_data)
    #     expected = [{"a": 1, "b": 3}, {"a": 2, "b": 4}]
    #     self.assertEqual(result, expected)

    # def test_to_dict_with_dataframe_as_dict(self):
    #     input_data = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    #     result = to_dict(input_data, as_list=False)
    #     expected = {"a": {0: 1, 1: 2}, "b": {0: 3, 1: 4}}
    #     self.assertEqual(result, expected)

    def test_to_dict_with_json_string(self):
        input_data = '{"a": 1, "b": 2}'
        result = to_dict(input_data, str_type="json")
        expected = {"a": 1, "b": 2}
        self.assertEqual(result, expected)

    def test_to_dict_with_xml_string(self):
        input_data = "<root><a>1</a><b>2</b></root>"
        result = to_dict(input_data, str_type="xml")
        expected = {"root": {"a": "1", "b": "2"}}
        self.assertEqual(result, expected)

    def test_to_dict_with_unsupported_type(self):
        input_data = 12345
        with self.assertRaises(TypeError):
            to_dict(input_data)


if __name__ == "__main__":
    unittest.main()
