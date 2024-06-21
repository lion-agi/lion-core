"""
Module for converting various input types to pandas DataFrames.

This module provides functions to convert a variety of data structures into
pandas DataFrames, with options for handling missing data, resetting the
index, and custom behavior for specific input types.

Functions:
    to_df: Converts various input types to a pandas DataFrame.
    md_to_df: Converts Markdown table to a DataFrame.
    html_to_df: Converts HTML table to a DataFrame.
"""

from functools import singledispatch
from io import StringIO
from typing import Any, Dict, List, Optional

import pandas as pd
from pandas import DataFrame, Series
from pandas.core.generic import NDFrame

from .type_conversion import to_list


@singledispatch
def to_df(
    input_: Any,
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: Optional[Dict[str, Any]] = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame:
    """
    Convert various input types to a pandas DataFrame.

    Args:
        input_: The input data to convert into a DataFrame.
        drop_how: Specifies how missing values are dropped. Default is 'all'.
        drop_kwargs: Additional keyword arguments for DataFrame.dropna().
        reset_index: If True, the DataFrame index will be reset. Default is True.
        **kwargs: Additional keyword arguments for DataFrame constructor.

    Returns:
        A pandas DataFrame constructed from the input data.

    Raises:
        ValueError: If there is an error during the conversion process.

    Example:
        >>> to_df({'A': [1, 2], 'B': [3, 4]})
           A  B
        0  1  3
        1  2  4
    """
    try:
        df = DataFrame(input_, **kwargs)
        df = df.dropna(how=drop_how, **(drop_kwargs or {}))
        return df.reset_index(drop=True) if reset_index else df
    except Exception as e:
        raise ValueError(f"Error converting input to DataFrame: {e}") from e


@to_df.register(list)
def _(
    input_: List[Any],
    /,
    *,
    drop_how: str = "all",
    drop_kwargs: Optional[Dict[str, Any]] = None,
    reset_index: bool = True,
    **kwargs: Any,
) -> DataFrame:
    """
    Specialized behavior for converting a list of data to a DataFrame.

    This function handles lists of various types, including lists of
    DataFrames, Series, or other data types.

    Args:
        input_: The input list to convert into a DataFrame.
        drop_how: Specifies how missing values are dropped. Default is 'all'.
        drop_kwargs: Additional keyword arguments for DataFrame.dropna().
        reset_index: If True, the DataFrame index will be reset. Default is True.
        **kwargs: Additional keyword arguments for DataFrame constructor.

    Returns:
        A pandas DataFrame constructed from the input list.

    Raises:
        ValueError: If there is an error during the conversion process.

    Example:
        >>> to_df([{'A': 1, 'B': 2}, {'A': 3, 'B': 4}])
           A  B
        0  1  2
        1  3  4
    """
    if not input_:
        return DataFrame()

    if not isinstance(input_[0], (DataFrame, Series, NDFrame)):
        return to_df(input_, drop_how=drop_how, drop_kwargs=drop_kwargs, 
                     reset_index=reset_index, **kwargs)

    try:
        if all(isinstance(i, Series) for i in input_):
            df = pd.concat(input_, axis=1, **kwargs)
        else:
            df = pd.concat(input_, axis=0, **kwargs)
    except Exception as e:
        try:
            input_ = to_list(input_)
            df = pd.concat(input_, **kwargs)
        except Exception as e2:
            raise ValueError(
                f"Error concatenating DataFrames/Series: {e}, {e2}"
            ) from e2

    df = df.dropna(how=drop_how, **(drop_kwargs or {}))
    return df.reset_index(drop=True) if reset_index else df


def md_to_df(md_str: str) -> Optional[DataFrame]:
    """
    Convert Markdown table to DataFrame.

    Args:
        md_str: The markdown string containing a table.

    Returns:
        A pandas DataFrame constructed from the markdown table,
        or None if the table is empty or invalid.

    Example:
        >>> md = '''
        ... | A | B |
        ... |---|---|
        ... | 1 | 2 |
        ... | 3 | 4 |
        ... '''
        >>> md_to_df(md)
           A  B
        0  1  2
        1  3  4
    """
    lines = md_str.strip().split("\n")
    if len(lines) < 3:
        return None

    # Remove header separator line
    lines = [line.strip() for line in lines if '|' in line]
    lines = [line for line in lines if not all(c in '|-' for c in line)]

    if not lines:
        return None

    csv_data = [
        ','.join(cell.strip() for cell in line.strip('|').split('|'))
        for line in lines
    ]
    csv_str = '\n'.join(csv_data)

    try:
        return pd.read_csv(StringIO(csv_str))
    except pd.errors.EmptyDataError:
        return None
