# import unittest
# # from pandas import DataFrame, Series

# from lion_core.libs.data_handlers._to_df import to_df


# class TestToDfFunction(unittest.TestCase):

#     def test_to_df_basic(self):
#         data = {"a": [1, 2, 3], "b": [4, 5, 6]}
#         df = to_df(data)
#         expected = DataFrame(data).dropna(how="all").reset_index(drop=True)
#         self.assertTrue(df.equals(expected))

#     def test_to_df_empty_list(self):
#         data = []
#         df = to_df(data)
#         expected = DataFrame()
#         self.assertTrue(df.equals(expected))

#     def test_to_df_list_of_dicts(self):
#         data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
#         df = to_df(data)
#         expected = DataFrame(data).dropna(how="all").reset_index(drop=True)
#         self.assertTrue(df.equals(expected))

#     def test_to_df_list_of_series(self):
#         data = [Series([1, 2, 3], name="a"), Series([4, 5, 6], name="b")]
#         df = to_df(data)
#         expected = (
#             DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
#             .dropna(how="all")
#             .reset_index(drop=True)
#         )
#         self.assertTrue(df.equals(expected))

#     def test_to_df_with_drop_kwargs(self):
#         data = {"a": [1, None, 3], "b": [4, 5, None]}
#         df = to_df(data, drop_kwargs={"thresh": 2})
#         expected = DataFrame(data).dropna(thresh=2).reset_index(drop=True)
#         self.assertTrue(df.equals(expected))

#     def test_to_df_raises_value_error(self):
#         with self.assertRaises(ValueError):
#             to_df("invalid_input")


# if __name__ == "__main__":
#     unittest.main()
